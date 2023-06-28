"""Various settings used by the client."""
from pydantic import BaseSettings, Field, SecretStr


class iCIMSCreds(BaseSettings):
    """iCIMS Credentials."""

    access_token_url: str = "https://login.icims.com/oauth/token"
    environment: str = Field(..., env="ENV")
    client_id: str = Field(..., env="CLIENT_ID")
    dev_customer_id: str = Field(..., env="DEV_CUSTOMER_ID")
    prd_customer_id: str = Field(..., env="PRD_CUSTOMER_ID")
    client_secret: SecretStr

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        secrets_dir = "./secrets"


class iCIMSUrls:
    """iCIMS Urls/Endpoints."""

    creds: iCIMSCreds = iCIMSCreds()
    is_dev: bool = creds.environment == "DEV"
    person_id_placeholder: str = "<<person_id>>"
    customer_id: str = creds.dev_customer_id if is_dev else creds.prd_customer_id
    base_url: str = f"https://api.icims.com/customers/{customer_id}"
    people_url: str = f"{base_url}/people"
    offer_url: str = f"{base_url}/offer"
    offer_status_url: str = f"{base_url}/offer/status"
    offer_document_url: str = f"{base_url}/offer/document"
    search_people_url: str = f"{base_url}/search/people"
    search_offer_url: str = f"{base_url}/offer/search"
    get_resume_url: str = f"{base_url}/people/{person_id_placeholder}/fields/resume/binary"
