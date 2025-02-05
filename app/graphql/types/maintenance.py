# app/graphql/types/maintenance.py
import strawberry
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

@strawberry.enum
class MaintenanceType(str, Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"
    SCHEDULED = "scheduled"
    INSPECTION = "inspection"

@strawberry.enum
class MaintenanceStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    VERIFIED = "verified"
    CANCELLED = "cancelled"

@strawberry.enum
class MaintenanceCategory(str, Enum):
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    HVAC = "hvac"
    FURNITURE = "furniture"
    APPLIANCES = "appliances"
    STRUCTURAL = "structural"
    IT_EQUIPMENT = "it_equipment"
    SAFETY_EQUIPMENT = "safety_equipment"
    GENERAL = "general"

@strawberry.type
class PartDetail:
    part_id: str
    quantity: int
    description: Optional[str]

@strawberry.type
class ProgressNote:
    timestamp: datetime
    note: str
    updated_by: str

@strawberry.type
class MaintenanceTask:
    id: str
    hotel_id: str
    room_id: Optional[str]
    area: str
    category: MaintenanceCategory
    maintenance_type: MaintenanceType
    title: str
    description: str
    priority: str
    status: MaintenanceStatus
    assigned_to: Optional[str]
    scheduled_date: datetime
    due_date: datetime
    estimated_duration: int
    actual_duration: Optional[int]
    cost_estimate: Optional[float]
    actual_cost: Optional[float]
    parts_required: List[PartDetail]  # Fixed
    parts_used: List[PartDetail]      # Fixed
    tools_required: List[str]
    safety_notes: Optional[str]
    progress_notes: List[ProgressNote]  # Fixed
    images_before: List[str]
    images_after: List[str]
    completed_at: Optional[datetime]
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
            room_id=db_data.get('room_id'),
            area=db_data['area'],
            category=db_data['category'],
            maintenance_type=db_data['maintenance_type'],
            title=db_data['title'],
            description=db_data['description'],
            priority=db_data['priority'],
            status=db_data['status'],
            assigned_to=db_data.get('assigned_to'),
            scheduled_date=db_data['scheduled_date'],
            due_date=db_data['due_date'],
            estimated_duration=db_data['estimated_duration'],
            actual_duration=db_data.get('actual_duration'),
            cost_estimate=db_data.get('cost_estimate'),
            actual_cost=db_data.get('actual_cost'),
            parts_required=db_data.get('parts_required', []),
            parts_used=db_data.get('parts_used', []),
            tools_required=db_data.get('tools_required', []),
            safety_notes=db_data.get('safety_notes'),
            progress_notes=db_data.get('progress_notes', []),
            images_before=db_data.get('images_before', []),
            images_after=db_data.get('images_after', []),
            completed_at=db_data.get('completed_at'),
            verified_by=db_data.get('verified_by'),
            verification_notes=db_data.get('verification_notes'),
            created_at=db_data['created_at'],
            updated_at=db_data['updated_at'],
            created_by=db_data['created_by'],
            updated_by=db_data['updated_by']
        )

@strawberry.type
class StaffAssignment:
    staff_id: str
    role: str
    shift: str

@strawberry.type
class MaintenanceSchedule:
    id: str
    hotel_id: str
    start_date: datetime
    end_date: datetime
    staff_assignments: List[StaffAssignment]  # Changed from Dict
    tasks: List[MaintenanceTask]  # Changed from Dict
    notes: Optional[str]


@strawberry.input
class PartDetailInput:
    part_id: str
    quantity: int
    description: Optional[str] = None

@strawberry.input
class MaintenanceTaskInput:
    hotel_id: str
    room_id: Optional[str]
    area: str
    category: MaintenanceCategory
    maintenance_type: MaintenanceType
    title: str
    description: str
    priority: str
    scheduled_date: datetime
    due_date: datetime
    estimated_duration: int
    cost_estimate: Optional[float]
    parts_required: Optional[List[PartDetailInput]]  # Fixed
    tools_required: Optional[List[str]]
    safety_notes: Optional[str]

@strawberry.input
class MaintenanceTaskUpdateInput:
    status: Optional[MaintenanceStatus]
    assigned_to: Optional[str]
    scheduled_date: Optional[datetime]
    due_date: Optional[datetime]
    actual_duration: Optional[int]
    actual_cost: Optional[float]
    parts_used: Optional[List[Dict]]
    progress_notes: Optional[str]
    images_after: Optional[List[str]]

@strawberry.input
class MaintenanceVerificationInput:
    task_id: str
    verified_by: str
    verification_notes: Optional[str]
    verification_status: bool