"""Task and progress schemas."""
from pydantic import BaseModel
from typing import Optional, Any


class TaskStatus(BaseModel):
    """Task progress status."""
    id: str
    status: str  # pending, initializing, generating, processing, completed, failed
    progress: int  # 0-100
    message: str
    created_at: str
    updated_at: str
    result: Optional[Any] = None
    error: Optional[str] = None


class GenerationTaskResponse(BaseModel):
    """Response when generation is started asynchronously."""
    task_id: str
    message: str
    status_url: str
