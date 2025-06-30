import os
from dotenv import load_dotenv

load_dotenv()


class ENV:
    def __init__(self):
        self.missing_required_envs = []

        self.cors_origins = os.getenv("CORS_ORIGINS", ["*"])

        self.cors_headers = os.getenv("CORSE_HEADERS", ["*"])

        self.cors_methods = os.getenv(
            "CORS_METHODS", ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        )

        self.mongo_db_url = os.getenv("MONGO_URI")
        if not self.mongo_db_url:
            print("Missing mongodb url env")
            self.missing_required_envs.append("MONGO_URI")

        self.database = os.getenv("DATABASE")
        if not self.database:
            print("Missing mongodb url env")
            self.missing_required_envs.append("DATABASE")

        self.secret_key = os.getenv("SECRET_KEY")
        if not self.secret_key:
            print("Missing mongodb url env")
            self.missing_required_envs.append("SECRET_KEY")

        self.smtp_server = os.getenv("SMTP_SERVER")
        if not self.smtp_server:
            print("Missing mongodb url env")
            
        self.smtp_email = os.getenv("SMTP_EMAIL")
        if not self.smtp_email:
            print("Missing mongodb url env")
            
        self.smtp_port = os.getenv("SMTP_PORT")
        if not self.smtp_port:
            print("Missing mongodb url env")\

        self.smtp_password = os.getenv("SMTP_PASSWORD")
        if not self.smtp_password:
            print("Missing mongodb url env")

        if self.missing_required_envs:
            error_message = (
                f"Missing required envs: {','.join(self.missing_required_envs)}"
            )
            print(error_message)
            raise EnvironmentError(error_message)