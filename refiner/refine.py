import json
import logging
import os
from refiner.models.offchain_schema import OffChainSchema
from refiner.models.output import Output, BrowsingOutput, BrowsingStatsOutput, BrowsingEntryOutput
from refiner.transformer.browsing_transformer import BrowsingTransformer
from refiner.config import settings
from refiner.utils.encrypt import encrypt_file
from refiner.utils.ipfs import upload_file_to_ipfs, upload_json_to_ipfs

class Refiner:
    def __init__(self):
        self.db_path = os.path.join(settings.OUTPUT_DIR, 'db.libsql')

    def transform(self) -> Output:
        """Transform all input files into the database."""
        logging.info("Starting data transformation")
        output = Output()

        # Iterate through files and transform data
        input_files = os.listdir(settings.INPUT_DIR)
        logging.info(f"Discovered input files: {input_files}")
        for input_filename in input_files:
            input_file = os.path.join(settings.INPUT_DIR, input_filename)
            ext = os.path.splitext(input_file)[1].lower()
            logging.info(f"Processing file: {input_filename} (full path: {input_file}, extension: {ext})")
            if ext in ['.json', '.bin']:
                try:
                    with open(input_file, 'r') as f:
                        logging.info(f"Loading data from {input_file}")
                        input_data = json.load(f)
                except Exception as e:
                    logging.error(f"Failed to load {input_file}: {e}")
                    continue

                # Transform browsing data
                logging.info(f"Instantiating BrowsingTransformer for {input_filename}")
                transformer = BrowsingTransformer(self.db_path)
                logging.info(f"Processing input data with BrowsingTransformer for {input_filename}")
                transformer.process(input_data)
                logging.info(f"Transformed {input_filename}")
                
                # Create a schema based on the SQLAlchemy schema
                logging.info(f"Creating OffChainSchema for {input_filename}")
                schema = OffChainSchema(
                    name=settings.SCHEMA_NAME,
                    version=settings.SCHEMA_VERSION,
                    description=settings.SCHEMA_DESCRIPTION,
                    dialect=settings.SCHEMA_DIALECT,
                    schema=transformer.get_schema()
                )
                output.schema = schema
                logging.info(f"Schema created: {schema.model_dump()}")
                
                # Generate output data for browsing
                browsing_data = transformer.get_output_data()
                if browsing_data:
                    logging.info(f"Browsing data found for {input_filename}: {browsing_data}")
                    stats = BrowsingStatsOutput(
                        urls=browsing_data["stats"]["urls"],
                        averageTimeSpent=browsing_data["stats"]["averageTimeSpent"],
                        type=browsing_data["stats"]["type"]
                    )
                    
                    entries = [
                        BrowsingEntryOutput(
                            url=entry["url"],
                            timeSpent=entry["timeSpent"],
                            timestamp=entry["timestamp"]
                        )
                        for entry in browsing_data["data"]
                    ]
                    
                    output.browsing_data = BrowsingOutput(
                        stats=stats,
                        data=entries
                    )
                    logging.info(f"Browsing output generated for {input_filename}")
                else:
                    logging.info(f"No browsing data found for {input_filename}")
                
                # Upload the schema to IPFS
                schema_file = os.path.join(settings.OUTPUT_DIR, 'schema.json')
                try:
                    with open(schema_file, 'w') as f:
                        json.dump(schema.model_dump(), f, indent=4)
                        logging.info(f"Schema written to {schema_file}")
                        schema_ipfs_hash = upload_json_to_ipfs(schema.model_dump())
                        logging.info(f"Schema uploaded to IPFS with hash: {schema_ipfs_hash}")
                except Exception as e:
                    logging.error(f"Failed to write/upload schema for {input_filename}: {e}")
                logging.info(f"DEBUG: refined data:{browsing_data}")
                logging.info(f"DEBUG: schema:{schema.model_dump()}")
                
                # Encrypt and upload the database to IPFS
                try:
                    logging.info(f"Encrypting database at {self.db_path}")
                    encrypted_path = encrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, self.db_path)
                    logging.info(f"Encrypted database written to {encrypted_path}")
                    ipfs_hash = upload_file_to_ipfs(encrypted_path)
                    output.refinement_url = f"{settings.IPFS_GATEWAY_URL}/{ipfs_hash}"
                    logging.info(f"Encrypted DB uploaded to IPFS with hash: {ipfs_hash}")
                except Exception as e:
                    logging.error(f"Failed to encrypt/upload database for {input_filename}: {e}")
                continue
            else:
                logging.info(f"Skipping unsupported file type: {input_filename}")

        logging.info("Data transformation completed successfully")
        return output
