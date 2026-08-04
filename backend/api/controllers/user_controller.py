from fastapi import APIRouter, Depends
from api.schemas.user_schemas.registration_schema import RegistrationRequestSchema, RegistrationResponseSchema
from core.service.user_service import UserService
from core.service.dependencies import get_user_service

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("/registration", response_model=RegistrationResponseSchema)
async def registrate(
        payload: RegistrationRequestSchema,
        user_service: UserService = Depends(get_user_service)
):
    created_user = await user_service.registrate_user(payload=payload)
    return RegistrationResponseSchema(
        id=created_user.id,
        login=created_user.login
    )
