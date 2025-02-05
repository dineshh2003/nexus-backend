# schemas/user.py
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from enum import Enum

class UserRole(str, Enum):
    HOTEL_ADMIN = "HOTEL_ADMIN"
    MANAGER = "MANAGER"
    STAFF = "STAFF"
    HOUSEKEEPING = "HOUSEKEEPING"
    RECEPTIONIST = "RECEPTIONIST"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone_number: str
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    hotels: List[str]  # List of hotel IDs this user has access to
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True

class HotelBase(BaseModel):
    name: str
    address: str
    contact_number: str
    email: EmailStr
    is_active: bool = True

class Hotel(HotelBase):
    id: str
    admin_id: str  # Reference to the HOTEL_ADMIN user
    managers: List[str]  # List of manager user IDs
    staff: List[str]  # List of staff user IDs
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True


