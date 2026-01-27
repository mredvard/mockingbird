"""Progress tracking service for long-running operations."""
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Status of a background task."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    GENERATING = "generating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProgressTracker:
    """Track progress of background tasks."""

    def __init__(self):
        self._tasks: Dict[str, Dict] = {}

    def create_task(self, task_id: str, description: str) -> None:
        """Create a new task for tracking."""
        self._tasks[task_id] = {
            "id": task_id,
            "status": TaskStatus.PENDING,
            "progress": 0,
            "message": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }

    def update_progress(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None
    ) -> None:
        """Update task progress."""
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]

        if status is not None:
            task["status"] = status

        if progress is not None:
            task["progress"] = min(100, max(0, progress))

        if message is not None:
            task["message"] = message

        task["updated_at"] = datetime.now().isoformat()

    def complete_task(self, task_id: str, result: any) -> None:
        """Mark task as completed with result."""
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]
        task["status"] = TaskStatus.COMPLETED
        task["progress"] = 100
        task["message"] = "Completed successfully"
        task["result"] = result
        task["updated_at"] = datetime.now().isoformat()

    def fail_task(self, task_id: str, error: str) -> None:
        """Mark task as failed with error."""
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]
        task["status"] = TaskStatus.FAILED
        task["message"] = "Failed"
        task["error"] = error
        task["updated_at"] = datetime.now().isoformat()

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task status and progress."""
        return self._tasks.get(task_id)

    def delete_task(self, task_id: str) -> None:
        """Remove task from tracking."""
        self._tasks.pop(task_id, None)

    def cleanup_old_tasks(self, max_age_hours: int = 24) -> None:
        """Remove old completed/failed tasks."""
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(hours=max_age_hours)

        to_delete = []
        for task_id, task in self._tasks.items():
            if task["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                updated_at = datetime.fromisoformat(task["updated_at"])
                if updated_at < cutoff:
                    to_delete.append(task_id)

        for task_id in to_delete:
            self.delete_task(task_id)


# Global progress tracker instance
progress_tracker = ProgressTracker()
