from passlib.context import CryptContext
from jose import jwt
from datetime import datetime
from datetime import timedelta
from jose import JWTError


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(
        password: str
):

    return pwd_context.hash(
        password
    )


def verify_password(
        plain_password: str,
        hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )




from .config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

def create_access_token(
        data: dict
):

    to_encode = data.copy()

    expire = (
        datetime.utcnow()

        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {"exp": expire}
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_access_token(
        token: str
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:

            return None

        return email


    except JWTError:

        return None