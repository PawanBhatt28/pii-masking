from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379"
    MYSQL_HOST: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DB: str = "pii_shield"
    ENCRYPTION_KEY: str = "e_v12UcnKtFRt_L0oVyExFP0XGaTPpoMVckVk396YAY="
    
    # HuggingFace API (optional - for BERT fallback)
    HUGGINGFACE_API_KEY: str =  ""
    HUGGINGFACE_API_URL: str = "https://api-inference.huggingface.co/models/ai4privacy/pii-detection-deberta-v3-base"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
