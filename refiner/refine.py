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
        for input_filename in os.listdir(settings.INPUT_DIR):
            input_file = os.path.join(settings.INPUT_DIR, input_filename)
            if os.path.splitext(input_file)[1].lower() in ['.json', '.bin']:
                with open(input_file, 'r') as f:
                    input_data = json.load(f)

                    # Transform browsing data
                    transformer = BrowsingTransformer(self.db_path)
                    transformer.process(input_data)
                    logging.info(f"Transformed {input_filename}")
                    
                    # Create a schema based on the SQLAlchemy schema
                    schema = OffChainSchema(
                        name=settings.SCHEMA_NAME,
                        version=settings.SCHEMA_VERSION,
                        description=settings.SCHEMA_DESCRIPTION,
                        dialect=settings.SCHEMA_DIALECT,
                        schema=transformer.get_schema()
                    )
                    output.schema = schema
                    
                    # Generate output data for browsing
                    browsing_data = transformer.get_output_data()
                    if browsing_data:
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
                        
                        
                    # Upload the schema to IPFS
                    schema_file = os.path.join(settings.OUTPUT_DIR, 'schema.json')
                    with open(schema_file, 'w') as f:
                        json.dump(schema.model_dump(), f, indent=4)
                        schema_ipfs_hash = upload_json_to_ipfs(schema.model_dump())
                        logging.info(f"Schema uploaded to IPFS with hash: {schema_ipfs_hash}")
                    logging.info(f"DEBUG: refined data:{browsing_data}")
                    logging.info(f"DEBUG: schema:{schema.model_dump()}")
                    
                    # Encrypt and upload the database to IPFS
                    encrypted_path = encrypt_file(settings.REFINEMENT_ENCRYPTION_KEY, self.db_path)
                    ipfs_hash = upload_file_to_ipfs(encrypted_path)
                    output.refinement_url = f"{settings.IPFS_GATEWAY_URL}/{ipfs_hash}"
                    continue

        logging.info("Data transformation completed successfully")
        return output
