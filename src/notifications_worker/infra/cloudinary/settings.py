from pydantic_settings import BaseSettings, SettingsConfigDict


class CloudinarySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CLOUDINARY_", env_file=".env", extra="ignore")

    cloud_name: str
    api_key: str
    api_secret: str


cloudinary_settings = CloudinarySettings()
