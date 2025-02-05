import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import field

@strawberry.enum
class HotelStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    UNDER_CONSTRUCTION = "under_construction"

@strawberry.type
class HotelAmenity:
    id: str
    name: str
    category: str
    description: Optional[str] = None
    icon: Optional[str] = None

# In app/graphql/types/hotel.py
@strawberry.type
class HotelPolicy:
    check_in_time: str
    check_out_time: str
    cancellation_hours: int
    payment_methods: List[str]
    pet_policy: str
    extra_bed_policy: Optional[str] = None

@strawberry.input
class HotelPolicyInput:
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    cancellation_hours: Optional[int] = None
    payment_methods: Optional[List[str]] = None
    pet_policy: Optional[str] = None


@strawberry.type
class Hotel:
    id: str
    name: str
    description: Optional[str] = None
    address: str
    city: str
    state: str
    country: str
    zipcode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: str
    contact_email: str
    website: Optional[str] = None
    admin_id: str
    status: HotelStatus
    amenities: List[str] = field(default_factory=list)
    room_count: int = 0
    floor_count: int
    star_rating: Optional[int] = None
    policies: HotelPolicy
    images: List[str] = field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_db(cls, db_data: dict):
        if not db_data:
            return None
            
        # Create HotelPolicy instance with proper defaults
        policies_data = db_data.get('policies', {})
        policies = HotelPolicy(
            check_in_time=policies_data.get('check_in_time', '14:00'),
            check_out_time=policies_data.get('check_out_time', '11:00'),
            cancellation_hours=policies_data.get('cancellation_hours', 24),
            payment_methods=policies_data.get('payment_methods', ["credit_card", "cash"]),
            pet_policy=policies_data.get('pet_policy', 'not_allowed'),
            extra_bed_policy=policies_data.get('extra_bed_policy')
        )

        return cls(
            id=str(db_data['_id']),
            name=db_data['name'],
            description=db_data.get('description'),
            address=db_data['address'],
            city=db_data['city'],
            state=db_data['state'],
            country=db_data['country'],
            zipcode=db_data['zipcode'],
            latitude=db_data.get('latitude'),
            longitude=db_data.get('longitude'),
            contact_phone=db_data['contact_phone'],
            contact_email=db_data['contact_email'],
            website=db_data.get('website'),
            admin_id=db_data['admin_id'],
            status=HotelStatus(db_data['status']),
            amenities=db_data.get('amenities', []),
            room_count=db_data.get('room_count', 0),
            floor_count=db_data['floor_count'],
            star_rating=db_data.get('star_rating'),
            policies=policies,
            images=db_data.get('images', []),
            created_at=db_data['created_at'],
            updated_at=db_data['updated_at']
        )

@strawberry.input
class HotelPolicyInput:
    check_in_time: str = "14:00"
    check_out_time: str = "11:00"
    cancellation_hours: int = 24
    payment_methods: List[str] = field(default_factory=lambda: ["credit_card", "cash"])
    pet_policy: str = "not_allowed"
    extra_bed_policy: Optional[str] = None

@strawberry.input
class HotelInput:
    name: str
    description: Optional[str] = None
    address: str
    city: str
    state: str
    country: str
    zipcode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: str
    contact_email: str
    website: Optional[str] = None
    admin_id: str
    floor_count: int
    star_rating: Optional[int] = None
    amenities: List[str] = field(default_factory=list)
    policies: Optional[HotelPolicyInput] = None

@strawberry.input
class HotelUpdateInput:
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    zipcode: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    status: Optional[HotelStatus] = None
    amenities: Optional[List[str]] = None
    star_rating: Optional[int] = None
    floor_count: Optional[int] = None
    policies: Optional[HotelPolicyInput] = None

