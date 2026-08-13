from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from ..database import SessionLocal
from fastapi import HTTPException

from .. import schemas
from .. import crud
from ..security import verify_password
from ..security import create_access_token
from fastapi.security import OAuth2PasswordBearer
from ..security import verify_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post(
    "/register",
    response_model=schemas.UserResponse
)
def register_user(

    user: schemas.UserCreate,

    db: Session = Depends(get_db)

):

    existing_user = crud.get_user_by_email(
        db,
        user.email
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="User already exists."
        )

    return crud.create_user(
        db,
        user
    )


@router.get(
    "/users",
    response_model=list[
        schemas.UserResponse
    ]
)
def get_users(

    db: Session = Depends(get_db)

):

    return crud.get_all_users(
        db
    )


@router.get(
    "/users/{user_id}",
    response_model=schemas.UserResponse
)
def get_user(

    user_id:int,

    db: Session = Depends(get_db)

):

    user = crud.get_user_by_id(
        db,
        user_id
    )


    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )


    return user



@router.post("/login")
def login_user(

    form_data: OAuth2PasswordRequestForm = Depends(),

    db: Session = Depends(get_db)

):

    existing_user = crud.get_user_by_email(
        db,
        form_data.username
    )


    if not existing_user:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )


    if not verify_password(
        form_data.password,
        existing_user.hashed_password
    ):

        raise HTTPException(
            status_code=401,
            detail="Incorrect password."
        )
    

    access_token = create_access_token(
        data={"sub": existing_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_current_user(

    token: str = Depends(
        oauth2_scheme
    ),

    db: Session = Depends(
        get_db
    )

):

    email = verify_access_token(
        token
    )


    if email is None:

        raise HTTPException(

            status_code=401,

            detail="Invalid token."

        )


    user = crud.get_user_by_email(
        db,
        email
    )


    if user is None:

        raise HTTPException(

            status_code=404,

            detail="User not found."

        )


    return user



def get_current_logged_in_user(

    token: str = Depends(oauth2_scheme),

    db: Session = Depends(get_db)

):

    email = verify_access_token(token)

    if email is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid token."
        )

    user = crud.get_user_by_email(
        db,
        email
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return user