from core.exceptions.user_exceptions import UserAlreadyExist
from fastapi import HTTPException, status


class ExceptionHandler:
    def __init__(self):
        pass

    async def user_already_exist_handler(self, exc: UserAlreadyExist):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )
