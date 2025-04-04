from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.use_cases.note_uc import NoteService
from src.core.use_cases.note_dtos import NoteCreateDTO, NoteReadDTO, NoteUpdateDTO
from src.core.use_cases.user_dtos import UserReadDTO
from src.api.dependencies import get_current_user, get_note_service

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post(
    "/", 
    response_model=NoteReadDTO, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note"
)
async def create_note(
    note_create: NoteCreateDTO,
    note_service: NoteService = Depends(get_note_service),
    current_user: UserReadDTO = Depends(get_current_user)
) -> NoteReadDTO:
    """
    Create a new note for the current user.
    """
    try:
        return await note_service.create_note(note_create, current_user.user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{note_id}", 
    response_model=NoteReadDTO,
    summary="Get note by ID"
)
async def get_note(
    note_id: str,
    note_service: NoteService = Depends(get_note_service),
    current_user: UserReadDTO = Depends(get_current_user)
) -> NoteReadDTO:
    """
    Get a specific note by ID.
    
    The note must belong to the current user.
    """
    note = await note_service.get_note_by_id(note_id, current_user.user_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Note not found or you don't have access"
        )
    return note


@router.put(
    "/{note_id}", 
    response_model=NoteReadDTO,
    summary="Update note"
)
async def update_note(
    note_id: str,
    note_update: NoteUpdateDTO,
    note_service: NoteService = Depends(get_note_service),
    current_user: UserReadDTO = Depends(get_current_user)
) -> NoteReadDTO:
    """
    Update a specific note by ID.
    
    The note must belong to the current user.
    """
    updated_note = await note_service.update_note(
        note_id, note_update, current_user.user_id
    )
    if not updated_note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Note not found or you don't have access"
        )
    return updated_note


@router.delete(
    "/{note_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete note"
)
async def delete_note(
    note_id: str,
    note_service: NoteService = Depends(get_note_service),
    current_user: UserReadDTO = Depends(get_current_user)
):
    """
    Delete a specific note by ID.
    
    The note must belong to the current user.
    """
    deleted = await note_service.delete_note(note_id, current_user.user_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Note not found or you don't have access"
        )


@router.get(
    "/", 
    response_model=List[NoteReadDTO],
    summary="List user notes"
)
async def list_notes(
    skip: int = 0,
    limit: int = 100,
    note_service: NoteService = Depends(get_note_service),
    current_user: UserReadDTO = Depends(get_current_user)
) -> List[NoteReadDTO]:
    """
    List all notes for the current user with pagination.
    """
    return await note_service.list_user_notes(
        current_user.user_id, skip=skip, limit=limit
    )