"""Sheets Routes - Handle sheet/table operations"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

router = APIRouter()

class Sheet(BaseModel):
    id: str
    name: str
    type: str
    columns: List[dict]
    created_at: datetime

@router.get("/")
async def list_sheets(user_id: Optional[str] = None):
    """Get all sheets for a user"""
    # TODO: Fetch from Supabase
    return {"sheets": []}

@router.post("/")
async def create_sheet(sheet: dict):
    """Create a new sheet"""
    # TODO: Create in Supabase
    return {"message": "Sheet created", "sheet_id": "sheet-123"}

@router.get("/{sheet_id}")
async def get_sheet(sheet_id: str):
    """Get a specific sheet with all rows"""
    # TODO: Fetch from Supabase
    return {"sheet": {}, "rows": []}

@router.post("/{sheet_id}/rows")
async def add_row(sheet_id: str, row_data: dict):
    """Add a row to a sheet"""
    # TODO: Insert into Supabase
    return {"message": "Row added", "row_id": "row-123"}
