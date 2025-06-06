from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Global settings configuration using environment variables"""
    
    INPUT_DIR: str = Field(
        default="/input",
        description="Directory containing input files to process"
    )
    
    OUTPUT_DIR: str = Field(
        default="/output",
        description="Directory where output files will be written"
    )
    
    REFINEMENT_ENCRYPTION_KEY: str = Field(
        default="",
        description="Key to symmetrically encrypt the refinement. This is derived from the original file encryption key"
    )
    
    # Add private IPFS server configuration
    IPFS_API_URL: str = Field(
        default="https://test.ipfs.ykyr.net/api/v0",
        description="URL for the private IPFS server API"
    )
    
        # Add private IPFS server configuration
    IPFS_HTTPS_URL: str = Field(
        default="https://test.ipfs.ykyr.net",
        description="URL for the private IPFS server HTTPS"
    )
    
    IPFS_GATEWAY_URL: str = Field(
        default="https://gateway.pinata.cloud/ipfs",
        description="URL for the IPFS gateway to access content"
    )
    
    SCHEMA_NAME: str = Field(
        default="Browsing Data Analytics",
        description="Name of the schema"
    )
    
    SCHEMA_VERSION: str = Field(
        default="0.0.1",
        description="Version of the schema"
    )
    
    SCHEMA_DESCRIPTION: str = Field(
        default="Schema for browsing data analytics, representing user browsing patterns and statistics",
        description="Description of the schema"
    )
    
    SCHEMA_DIALECT: str = Field(
        default="sqlite",
        description="Dialect of the schema"
    )
    
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
