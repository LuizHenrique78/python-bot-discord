
from pydantic import Field

class EnvConfig(BaseSettings):
    """
    Environment configuration for the application.
    """
    discord_bot_token: str = Field(validation_alias="DISCORD_BOT_TOKEN")
