# app/graphql/schema.py
from typing import List, Optional
import strawberry
from datetime import datetime
from app.db.mongodb import MongoDB

@strawberry.type
class Hotel:
    id: str
    name: str
    address: str
    contact: str
    admin_id: str

@strawberry.type
class Room:
    id: str
    floor: int
    room_number: str
    room_type: str
    status: str
    price: float
    hotel_id: str

@strawberry.type
class Booking:
    id: str
    booking_info: str
    guest_name: str
    number_of_guests: int
    booking_type: str
    room_type: str
    room_number: str
    check_in: datetime
    check_out: datetime
    payment_status: str
    total_amount: float
    hotel_id: str

@strawberry.type
class Query:
    @strawberry.field
    async def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        hotel_doc = await MongoDB.database["hotels"].find_one({"_id": hotel_id})
        if hotel_doc:
            return Hotel(**hotel_doc)
        return None

    @strawberry.field
    async def get_rooms(self, hotel_id: str) -> List[Room]:
        rooms = []
        cursor = MongoDB.database["rooms"].find({"hotel_id": hotel_id})
        async for room in cursor:
            rooms.append(Room(**room))
        return rooms

    @strawberry.field
    async def get_bookings(self, hotel_id: str) -> List[Booking]:
        bookings = []
        cursor = MongoDB.database["bookings"].find({"hotel_id": hotel_id})
        async for booking in cursor:
            bookings.append(Booking(**booking))
        return bookings

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_hotel(
        self, name: str, address: str, contact: str, admin_id: str
    ) -> Hotel:
        hotel_doc = {
            "name": name,
            "address": address,
            "contact": contact,
            "admin_id": admin_id
        }
        result = await MongoDB.database["hotels"].insert_one(hotel_doc)
        hotel_doc["id"] = str(result.inserted_id)
        return Hotel(**hotel_doc)

    @strawberry.mutation
    async def create_room(
        self,
        floor: int,
        room_number: str,
        room_type: str,
        status: str,
        price: float,
        hotel_id: str
    ) -> Room:
        room_doc = {
            "floor": floor,
            "room_number": room_number,
            "room_type": room_type,
            "status": status,
            "price": price,
            "hotel_id": hotel_id
        }
        result = await MongoDB.database["rooms"].insert_one(room_doc)
        room_doc["id"] = str(result.inserted_id)
        return Room(**room_doc)

    @strawberry.mutation
    async def create_booking(
        self,
        booking_info: str,
        guest_name: str,
        number_of_guests: int,
        booking_type: str,
        room_type: str,
        room_number: str,
        check_in: datetime,
        check_out: datetime,
        payment_status: str,
        total_amount: float,
        hotel_id: str
    ) -> Booking:
        booking_doc = {
            "booking_info": booking_info,
            "guest_name": guest_name,
            "number_of_guests": number_of_guests,
            "booking_type": booking_type,
            "room_type": room_type,
            "room_number": room_number,
            "check_in": check_in,
            "check_out": check_out,
            "payment_status": payment_status,
            "total_amount": total_amount,
            "hotel_id": hotel_id
        }
        result = await MongoDB.database["bookings"].insert_one(booking_doc)
        booking_doc["id"] = str(result.inserted_id)
        return Booking(**booking_doc)

schema = strawberry.Schema(query=Query, mutation=Mutation)