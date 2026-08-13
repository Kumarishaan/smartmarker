from dotenv import load_dotenv
import os

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")

ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
)