from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.user_uc import UserService
from src.core.use_cases.user_dtos import (
    TokenResponseDTO, UserCreateDTO, UserLoginDTO, UserReadDTO, UserUpdateDTO
)
from src.api.dependencies import get_current_user, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/", 
    response_model=UserReadDTO, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user"
)
async def create_user(
    user_create: UserCreateDTO,
    user_service: UserService = Depends(get_user_service)
) -> UserReadDTO:
    """
    Create a new user with the given data.
    """
    try:
        return await user_service.create_user(user_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/token", 
    response_model=TokenResponseDTO,
    summary="Login and get token"
)
async def login(
    login_data: UserLoginDTO,
    user_service: UserService = Depends(get_user_service)
) -> TokenResponseDTO:
    """
    Login with username and password to get an access token.
    """
    token = await user_service.authenticate_user(login_data)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.get(
    "/me", 
    response_model=UserReadDTO,
    summary="Get current user"
)
async def get_current_user_info(
    current_user: UserReadDTO = Depends(get_current_user)
) -> UserReadDTO:
    """
    Get information about the currently authenticated user.
    """
    return current_user


@router.get(
    "/{user_id}", 
    response_model=UserReadDTO,
    summary="Get user by ID"
)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserReadDTO = Depends(get_current_user)
) -> UserReadDTO:
    """
    Get information about a specific user.
    """
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put(
    "/{user_id}", 
    response_model=UserReadDTO,
    summary="Update user"
)
async def update_user(
    user_id: str,
    user_update: UserUpdateDTO,
    user_service: UserService = Depends(get_user_service),
    current_user: UserReadDTO = Depends(get_current_user)
) -> UserReadDTO:
    """
    Update a user with the given data.
    
    Only the user themselves or an admin can update a user.
    """
    # Check if current user is the target user or an admin
    if current_user.user_id != user_id and current_user.tier != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_user = await user_service.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return updated_user


@router.delete(
    "/{user_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user"
)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserReadDTO = Depends(get_current_user)
):
    """
    Delete a user.
    
    Only the user themselves or an admin can delete a user.
    """
    # Check if current user is the target user or an admin
    if current_user.user_id != user_id and current_user.tier != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    deleted = await user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get(
    "/", 
    response_model=List[UserReadDTO],
    summary="List users",
    dependencies=[Depends(get_current_user)]  # Must be authenticated
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service)
) -> List[UserReadDTO]:
    """
    List all users with pagination.
    """
    return await user_service.list_users(skip=skip, limit=limit)