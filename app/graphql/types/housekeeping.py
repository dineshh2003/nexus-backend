# app/graphql/types/housekeeping.py
import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum

@strawberry.enum
class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CANCELLED = "cancelled"

@strawberry.enum
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@strawberry.enum
class TaskType(str, Enum):
    CLEANING = "cleaning"
    TURNDOWN = "turndown"
    MAINTENANCE = "maintenance"
    DEEP_CLEANING = "deep_cleaning"
    INSPECTION = "inspection"
    SPECIAL_REQUEST = "special_request"

@strawberry.type
class TaskChecklistItem:
    id: str
    description: str
    is_completed: bool
    completed_at: Optional[datetime]
    notes: Optional[str]

@strawberry.type
class HousekeepingTask:
    id: str
    hotel_id: str
    room_id: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    assigned_to: Optional[str]
    scheduled_date: datetime
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    checklist: List[TaskChecklistItem]
    notes: Optional[str]
    issues_reported: List[str]
    verified_by: Optional[str]
    verification_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: str

    @classmethod
    def from_db(cls, db_data: dict):
        return cls(
            id=str(db_data['_id']),
            hotel_id=db_data['hotel_id'],
            room_id=db_data['room_id'],
            task_type=db_data['task_type'],
            priority=db_data['priority'],
            status=db_data['status'],
            assigned_to=db_data.get('assigned_to'),
            scheduled_date=db_data['scheduled_date'],
            start_time=db_data.get('start_time'),
            end_time=db_data.get('end_time'),
            duration_minutes=db_data.get('duration_minutes'),
            checklist=[TaskChecklistItem(**item) for item in db_data.get('checklist', [])],
            notes=db_data.get('notes'),
            issues_reported=db_data.get('issues_reported', []),
            verified_by=db_data.get('verified_by'),
            verification_notes=db_data.get('verification_notes'),
            created_at=db_data['created_at'],
            updated_at=db_data['updated_at'],
            created_by=db_data['created_by'],
            updated_by=db_data['updated_by']
        )



@strawberry.input
class TaskChecklistItemInput:
    description: str
    is_completed: bool = False
    notes: Optional[str] = None

@strawberry.input
class HousekeepingTaskInput:
    hotel_id: str
    room_id: str
    task_type: TaskType
    priority: TaskPriority
    scheduled_date: datetime
    assigned_to: Optional[str] = None
    checklist: List[TaskChecklistItemInput]  # Fixed
    notes: Optional[str] = None

@strawberry.input
class HousekeepingTaskUpdateInput:
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None
    issues_reported: Optional[List[str]] = None

@strawberry.input
class TaskVerificationInput:
    task_id: str
    verified_by: str
    verification_notes: Optional[str] = None
    verification_status: bool

@strawberry.type
class StaffAssignment:
    staff_id: str
    role: str
    hours: int

@strawberry.type
class RoomAssignment:
    room_id: str
    status: str
    notes: Optional[str]

@strawberry.type
class HousekeepingSchedule:
    id: str
    hotel_id: str
    date: datetime
    shift: str
    staff_assignments: List[StaffAssignment]  # Fixed
    room_assignments: List[RoomAssignment]    # Fixed
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

@strawberry.input
class StaffAssignmentInput:
    staff_id: str
    role: str
    hours: int

@strawberry.input
class RoomAssignmentInput:
    room_id: str
    status: str
    notes: Optional[str] = None

@strawberry.input
class ScheduleInput:
    hotel_id: str
    date: datetime
    shift: str
    staff_assignments: List[StaffAssignmentInput]  # Fixed
    room_assignments: List[RoomAssignmentInput]    # Fixed
    notes: Optional[str] = None