from fastapi import APIRouter, Depends
from api.schemas.user_schema import UserCreate, UserResponse, UserLogin
from core.service.user_service import UserService
from core.service.dependencies import get_user_service

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("/registration", response_model=UserResponse)
async def registrate(
        payload: UserCreate,
        user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    created_user = await user_service.create(payload=payload)
    return UserResponse(
        id=created_user.id,
        login=created_user.login
    )


@router.post("/login", response_model=UserResponse)
async def login(
        payload: UserLogin,
        user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    user = await user_service.login(payload=payload)
    return UserResponse(
        id=user.id,
        login=user.login
    )
