from fastapi import APIRouter
from schemas import User
from typing import List

router = APIRouter()


@router.get("/", response_model=List[User])
async def read_users():
    return [User(name="Rick"), User(name="Morty")]


@router.get("/me", response_model=User)
async def read_user_me():
    return User(name="Fra")


@router.get("/{name}", response_model=User)
async def read_user(name: str):
    return User(name=name)


@router.post("/", response_model=User)
async def create_user(user: User):
    return user
