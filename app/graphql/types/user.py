# app/graphql/types/user.py
import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum

@strawberry.type
class Condition:
    field: str
    operator: str
    value: str

@strawberry.enum
class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    HOTEL_ADMIN = "hotel_admin"
    STAFF = "staff"
    RECEPTIONIST = "receptionist"
    HOUSEKEEPER = "housekeeper"
    MAINTENANCE = "maintenance"

@strawberry.type
class User:
    id: str
    email: str
    name: str
    role: UserRole
    phone: Optional[str]
    hotel_ids: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    @classmethod
    def from_db(cls, db_data: dict):
        return cls(
            id=str(db_data['_id']),
            email=db_data['email'],
            name=db_data['name'],
            role=db_data['role'],
            phone=db_data.get('phone'),
            hotel_ids=db_data.get('hotel_ids', []),
            is_active=db_data.get('is_active', True),
            created_at=db_data['created_at'],
            updated_at=db_data['updated_at'],
            last_login=db_data.get('last_login')
        )

@strawberry.input
class UserInput:
    email: str
    name: str
    role: UserRole
    password: str
    phone: Optional[str] = None
    hotel_ids: Optional[List[str]] = None

# In app/graphql/types/user.py
@strawberry.input
class UserUpdateInput:
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[UserRole] = None
    phone: Optional[str] = None
    hotel_ids: Optional[List[str]] = None
    is_active: Optional[bool] = None

@strawberry.type
class UserPermission:
    id: str
    user_id: str
    resource: str
    action: str 
    conditions: Optional[List[Condition]] = None