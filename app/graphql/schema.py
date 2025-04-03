import strawberry
from typing import Optional, List
from datetime import datetime

# Import mutation classes
from ..graphql.mutations.room_mutations import RoomMutations
from ..graphql.mutations.user_mutations import UserMutations
from ..graphql.mutations.hotel_mutations import HotelMutations
from ..graphql.mutations.booking_mutations import BookingMutations

# Import types
from ..graphql.types.user import User, UserInput, UserUpdateInput
from ..graphql.types.hotel import (
    Hotel, 
    HotelInput, 
    HotelUpdateInput, 
    HotelPolicyInput,
    HotelResponse,
    HotelDeleteResponse,
    PaginatedHotelResponse
)
from ..graphql.types.maintenance import MaintenanceCategory, MaintenanceType, PartDetailInput, MaintenanceStatus
from ..graphql.types.room import (
    Room,
    RoomInput,
    RoomUpdateInput,
    RoomStatusUpdateInput,
    RoomType,
    RoomStatus,
    BedType
)
from ..graphql.types.booking import (
    Booking,
    BookingInput,
    BookingUpdateInput,
    BookingStatus,
    PaymentStatus,
    PaymentInput
)

# Import query classes
from ..graphql.queries.user_queries import UserQueries
from ..graphql.queries.hotel_queries import HotelQueries
from ..graphql.queries.room_queries import RoomQueries
from ..graphql.queries.booking_queries import BookingQueries

@strawberry.type
class Query:
    """
    Root query class for GraphQL schema.
    Includes user, hotel, room, and booking queries.
    """
    @strawberry.field
    def user(self) -> UserQueries:
        return UserQueries()
    
    @strawberry.field
    def hotel(self) -> HotelQueries:
        return HotelQueries()

    @strawberry.field
    async def room(self, room_id: str) -> Optional[Room]:
        return await RoomQueries().get_room(room_id)

    @strawberry.field
    async def rooms(
        self,
        hotel_id: Optional[str] = None,
        room_type: Optional[RoomType] = None,
        status: Optional[RoomStatus] = None,
        bed_type: Optional[BedType] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[Room]:
        return await RoomQueries().get_rooms(
            hotel_id, room_type, status, bed_type,
            min_price, max_price, limit, offset
        )

    @strawberry.field
    async def available_rooms(
        self,
        hotel_id: str,
        check_in_date: datetime,
        check_out_date: datetime,
        room_type: Optional[RoomType] = None,
        guests: Optional[int] = None
    ) -> List[Room]:
        return await RoomQueries().get_available_rooms(
            hotel_id, check_in_date, check_out_date,
            room_type=room_type, guests=guests
        )

    @strawberry.field
    async def rooms_by_amenities(
        self,
        hotel_id: str,
        amenities: List[str]
    ) -> List[Room]:
        return await RoomQueries().get_rooms_by_amenities(hotel_id, amenities)

    @strawberry.field
    async def rooms_by_status(
        self,
        hotel_id: str,
        status: RoomStatus
    ) -> List[Room]:
        return await RoomQueries().get_rooms_by_status(hotel_id, status)
    
    # Booking Queries
    @strawberry.field
    async def booking(self, booking_id: str) -> Optional[Booking]:
        return await BookingQueries().get_booking(booking_id)

    @strawberry.field
    async def bookings(
        self,
        hotel_id: Optional[str] = None,
        room_id: Optional[str] = None,
        booking_status: Optional[BookingStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[Booking]:
        return await BookingQueries().get_bookings(
            hotel_id, room_id, booking_status, payment_status,
            start_date, end_date, limit, offset
        )

    @strawberry.field
    async def bookings_by_guest(
        self,
        guest_email: str,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[Booking]:
        return await BookingQueries().get_bookings_by_guest(guest_email, limit, offset)

    @strawberry.field
    async def active_bookings(
        self,
        hotel_id: str,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[Booking]:
        return await BookingQueries().get_active_bookings(hotel_id, limit, offset)

    @strawberry.field
    async def upcoming_bookings(
        self,
        hotel_id: str,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[Booking]:
        return await BookingQueries().get_upcoming_bookings(hotel_id, limit, offset)

@strawberry.field
async def booking_by_number(
    self,
    booking_number: str
) -> Optional[Booking]:
    """
    Fetch a booking by its booking number.
    """
    return await BookingQueries().get_booking_by_number(booking_number)

@strawberry.type
class Mutation:
    """
    Root mutation class for GraphQL schema.
    Includes user, hotel, room, and booking mutations.
    """

    # User Mutations
    @strawberry.field
    def create_user(self, user_data: UserInput) -> User:
        return UserMutations().create_user(user_data)

    @strawberry.field
    def update_user(self, id: str, user_data: UserUpdateInput) -> User:
        return UserMutations().update_user(id, user_data)

    @strawberry.field
    def delete_user(self, id: str) -> bool:
        return UserMutations().delete_user(id)

    @strawberry.field
    def change_password(self, id: str, current_password: str, new_password: str) -> bool:
        return UserMutations().change_password(id, current_password, new_password)

    @strawberry.field
    def assign_hotels_to_user(self, user_id: str, hotel_ids: List[str]) -> User:
        return UserMutations().assign_hotels_to_user(user_id, hotel_ids)

    @strawberry.field
    def update_user_role(self, user_id: str, new_role: str) -> User:
        return UserMutations().update_user_role(user_id, new_role)

    # Hotel Mutations
    @strawberry.field
    def create_hotel(self, hotel_data: HotelInput) -> Hotel:
        return HotelMutations().create_hotel(hotel_data)

    @strawberry.field
    def update_hotel(self, id: str, hotel_data: HotelUpdateInput) -> Hotel:
        return HotelMutations().update_hotel(id, hotel_data)

    @strawberry.field
    def delete_hotel(self, id: str) -> bool:
        return HotelMutations().delete_hotel(id)

    @strawberry.field
    def update_hotel_policies(self, hotel_id: str, policies: HotelPolicyInput) -> Hotel:
        return HotelMutations().update_hotel_policies(hotel_id, policies)

    @strawberry.field
    def add_hotel_amenities(self, hotel_id: str, amenities: List[str]) -> Hotel:
        return HotelMutations().add_hotel_amenities(hotel_id, amenities)

    @strawberry.field
    def remove_hotel_amenities(self, hotel_id: str, amenities: List[str]) -> Hotel:
        return HotelMutations().remove_hotel_amenities(hotel_id, amenities)

    @strawberry.field
    def update_hotel_images(self, hotel_id: str, images: List[str], operation: str = "add") -> Hotel:
        return HotelMutations().update_hotel_images(hotel_id, images, operation)

    @strawberry.field
    def change_hotel_status(self, hotel_id: str, status: str, reason: Optional[str] = None) -> Hotel:
        return HotelMutations().change_hotel_status(hotel_id, status, reason)

    @strawberry.field
    def assign_hotel_admin(self, hotel_id: str, admin_id: str) -> Hotel:
        return HotelMutations().assign_hotel_admin(hotel_id, admin_id)

    @strawberry.field
    def update_hotel_location(
        self,
        hotel_id: str,
        latitude: float,
        longitude: float,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        zipcode: Optional[str] = None
    ) -> Hotel:
        return HotelMutations().update_hotel_location(
            hotel_id, latitude, longitude, address, city, state, country, zipcode
        )

    # Room Mutations
    @strawberry.field
    async def create_room(self, room_data: RoomInput) -> Room:
        return await RoomMutations().create_room(room_data)

    @strawberry.field
    async def update_room(self, id: str, room_data: RoomUpdateInput) -> Room:
        return await RoomMutations().update_room(id, room_data)

    @strawberry.field
    async def delete_room(self, id: str) -> bool:
        return await RoomMutations().delete_room(id)

    @strawberry.field
    async def update_room_status(
        self,
        room_id: str,
        status: RoomStatus,
        notes: Optional[str] = None
    ) -> Room:
        return await RoomMutations().update_room_status(room_id, status, notes)

    @strawberry.field
    async def bulk_update_room_status(
        self,
        room_ids: List[str],
        status: RoomStatus,
        notes: Optional[str] = None
    ) -> List[Room]:
        return await RoomMutations().bulk_update_room_status(room_ids, status, notes)

    @strawberry.field
    async def update_room_amenities(
        self,
        room_id: str,
        amenities: List[str],
        operation: str = "add"
    ) -> Room:
        return await RoomMutations().update_room_amenities(room_id, amenities, operation)

    @strawberry.field
    async def update_room_pricing(
        self,
        room_id: str,
        price_per_night: float,
        extra_bed_price: Optional[float] = None
    ) -> Room:
        return await RoomMutations().update_room_pricing(room_id, price_per_night, extra_bed_price)
    
    @strawberry.field
    async def mark_room_maintenance(
        self,
        room_id: str,
        title: str,
        description: str,
        maintenance_type: MaintenanceType = MaintenanceType.CORRECTIVE,
        category: MaintenanceCategory = MaintenanceCategory.GENERAL,
        priority: str = "HIGH",
        estimated_days: int = 1,
        safety_notes: Optional[str] = None,
        parts_required: Optional[List[PartDetailInput]] = None,
        tools_required: Optional[List[str]] = None,
        created_by: str = "SYSTEM"
    ) -> Room:
        return await RoomMutations().mark_room_maintenance(
            room_id, title, description, maintenance_type, category,
            priority, estimated_days, safety_notes, parts_required,
            tools_required, created_by
        )

    # Booking Mutations
    @strawberry.field
    async def create_booking(self, booking_data: BookingInput) -> Booking:
        return await BookingMutations().create_booking(booking_data)

    @strawberry.field
    async def update_booking_status(
        self,
        booking_id: str,
        status: BookingStatus,
        notes: Optional[str] = None
    ) -> Booking:
        return await BookingMutations().update_booking_status(booking_id, status, notes)

    @strawberry.field
    async def add_payment(
        self,
        booking_id: str,
        payment_data: PaymentInput
    ) -> Booking:
        return await BookingMutations().add_payment(booking_id, payment_data)

    @strawberry.field
    async def add_room_charge(
        self,
        booking_id: str,
        description: str,
        amount: float,
        charge_type: str,
        notes: Optional[str] = None
    ) -> Booking:
        return await BookingMutations().add_room_charge(
            booking_id, description, amount, charge_type, notes
        )

    @strawberry.field
    async def extend_booking(
        self,
        booking_id: str,
        new_check_out_date: datetime,
        notes: Optional[str] = None
    ) -> Booking:
        return await BookingMutations().extend_booking(
            booking_id, new_check_out_date, notes
        )

# Create the schema with both queries and mutations
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)