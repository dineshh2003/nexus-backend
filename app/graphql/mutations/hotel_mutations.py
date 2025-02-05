# app/graphql/mutations/hotel_mutations.py
import strawberry
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.graphql.types.hotel import (
    Hotel,
    HotelInput,
    HotelUpdateInput,
    HotelStatus,
    HotelPolicy,
    HotelPolicyInput
)
from app.db.mongodb import MongoDB

@strawberry.type
class HotelMutations:
    @strawberry.mutation
    async def create_hotel(self, hotel_data: HotelInput) -> Hotel:
        try:
            db = await MongoDB.get_database()
            
            # Check if admin exists
            admin = await db.users.find_one({"_id": ObjectId(hotel_data.admin_id)})
            if not admin:
                raise ValueError("Admin user not found")

            # Create hotel document
            policies_dict = {
                "check_in_time": hotel_data.policies.check_in_time if hotel_data.policies else "14:00",
                "check_out_time": hotel_data.policies.check_out_time if hotel_data.policies else "11:00",
                "cancellation_hours": hotel_data.policies.cancellation_hours if hotel_data.policies else 24,
                "payment_methods": hotel_data.policies.payment_methods if hotel_data.policies else ["credit_card", "cash"],
                "pet_policy": hotel_data.policies.pet_policy if hotel_data.policies else "not_allowed"
            }

            hotel_dict = {
                "name": hotel_data.name,
                "description": hotel_data.description,
                "address": hotel_data.address,
                "city": hotel_data.city,
                "state": hotel_data.state,
                "country": hotel_data.country,
                "zipcode": hotel_data.zipcode,
                "latitude": hotel_data.latitude,
                "longitude": hotel_data.longitude,
                "contact_phone": hotel_data.contact_phone,
                "contact_email": hotel_data.contact_email,
                "website": hotel_data.website,
                "admin_id": hotel_data.admin_id,
                "status": HotelStatus.ACTIVE.value,
                "amenities": hotel_data.amenities or [],
                "room_count": 0,
                "floor_count": hotel_data.floor_count,
                "star_rating": hotel_data.star_rating,
                "policies": policies_dict,
                "images": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            result = await db.hotels.insert_one(hotel_dict)
            hotel_dict["id"] = str(result.inserted_id)

            # Update admin's hotel assignments
            await db.users.update_one(
                {"_id": ObjectId(hotel_data.admin_id)},
                {"$addToSet": {"hotel_ids": str(result.inserted_id)}}
            )
            
            return Hotel.from_db(hotel_dict)

        except Exception as e:
            raise ValueError(f"Error creating hotel: {str(e)}")

    @strawberry.mutation
    async def update_hotel(self, id: str, hotel_data: HotelUpdateInput) -> Hotel:
        try:
            db = await MongoDB.get_database()
            
            # Check if hotel exists
            existing_hotel = await db.hotels.find_one({"_id": ObjectId(id)})
            if not existing_hotel:
                raise ValueError("Hotel not found")

            # Build update dictionary
            update_dict = {}
            
            # Basic hotel details
            if hotel_data.name is not None:
                update_dict["name"] = hotel_data.name
            
            if hotel_data.description is not None:
                update_dict["description"] = hotel_data.description
            
            if hotel_data.address is not None:
                update_dict["address"] = hotel_data.address
            
            if hotel_data.city is not None:
                update_dict["city"] = hotel_data.city
            
            if hotel_data.state is not None:
                update_dict["state"] = hotel_data.state
            
            if hotel_data.country is not None:
                update_dict["country"] = hotel_data.country
            
            if hotel_data.zipcode is not None:
                update_dict["zipcode"] = hotel_data.zipcode
            
            if hotel_data.contact_phone is not None:
                update_dict["contact_phone"] = hotel_data.contact_phone
            
            if hotel_data.contact_email is not None:
                update_dict["contact_email"] = hotel_data.contact_email
            
            if hotel_data.website is not None:
                update_dict["website"] = hotel_data.website
            
            if hotel_data.star_rating is not None:
                update_dict["star_rating"] = hotel_data.star_rating
            
            # Status update
            if hotel_data.status is not None:
                if hotel_data.status not in [status.value for status in HotelStatus]:
                    raise ValueError(f"Invalid hotel status: {hotel_data.status}")
                update_dict["status"] = hotel_data.status
            
            # Amenities update
            if hotel_data.amenities is not None:
                update_dict["amenities"] = hotel_data.amenities
            
            # Policies update
            if hotel_data.policies is not None:
                policies_update = {}
                if hotel_data.policies.check_in_time is not None:
                    policies_update["check_in_time"] = hotel_data.policies.check_in_time
                if hotel_data.policies.check_out_time is not None:
                    policies_update["check_out_time"] = hotel_data.policies.check_out_time
                if hotel_data.policies.cancellation_hours is not None:
                    policies_update["cancellation_hours"] = hotel_data.policies.cancellation_hours
                if hotel_data.policies.payment_methods is not None:
                    policies_update["payment_methods"] = hotel_data.policies.payment_methods
                if hotel_data.policies.pet_policy is not None:
                    policies_update["pet_policy"] = hotel_data.policies.pet_policy
                
                if policies_update:
                    update_dict["policies"] = policies_update

            # Always update timestamp
            update_dict["updated_at"] = datetime.utcnow()

            # Update hotel
            await db.hotels.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_dict}
            )

            updated_hotel = await db.hotels.find_one({"_id": ObjectId(id)})
            return Hotel.from_db(updated_hotel)

        except Exception as e:
            raise ValueError(f"Error updating hotel: {str(e)}")

    @strawberry.mutation
    async def delete_hotel(self, id: str) -> bool:
        try:
            db = await MongoDB.get_database()
            
            # Check if hotel exists
            hotel = await db.hotels.find_one({"_id": ObjectId(id)})
            if not hotel:
                raise ValueError("Hotel not found")

            # Set hotel status to inactive
            result = await db.hotels.update_one(
                {"_id": ObjectId(id)},
                {
                    "$set": {
                        "status": HotelStatus.INACTIVE.value,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            # Remove hotel from all users' hotel_ids
            await db.users.update_many(
                {"hotel_ids": id},
                {"$pull": {"hotel_ids": id}}
            )

            return result.modified_count > 0

        except Exception as e:
            raise ValueError(f"Error deleting hotel: {str(e)}")

    # ... (rest of the methods from the previous implementation remain the same)

@strawberry.mutation
async def update_hotel_policies(
    self,
    hotel_id: str,
    policies: HotelPolicyInput  # Use the input type instead of dict
) -> Hotel:
    try:
        db = await MongoDB.get_database()
        
        # Check if hotel exists
        hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
        if not hotel:
            raise ValueError("Hotel not found")

        # Convert input to dictionary, only including non-None values
        policies_update = {
            k: v for k, v in {
                "check_in_time": policies.check_in_time,
                "check_out_time": policies.check_out_time,
                "cancellation_hours": policies.cancellation_hours,
                "payment_methods": policies.payment_methods,
                "pet_policy": policies.pet_policy
            }.items() if v is not None
        }

        # Update policies
        await db.hotels.update_one(
            {"_id": ObjectId(hotel_id)},
            {
                "$set": {
                    "policies": policies_update,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        updated_hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
        return Hotel.from_db(updated_hotel)

    except Exception as e:
        raise ValueError(f"Error updating hotel policies: {str(e)}")

# app/graphql/mutations/hotel_mutations.py (continued)
@strawberry.mutation
async def add_hotel_amenities(
        self,
        hotel_id: str,
        amenities: List[str]
) -> Hotel:
    try:
        db = await MongoDB.get_database()
            
        # Check if hotel exists
        hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
        if not hotel:
            raise ValueError("Hotel not found")

        # Add amenities (avoid duplicates)
        await db.hotels.update_one(
            {"_id": ObjectId(hotel_id)},
            {
                "$addToSet": {"amenities": {"$each": amenities}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        updated_hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
        return Hotel.from_db(updated_hotel)

    except Exception as e:
        raise ValueError(f"Error adding hotel amenities: {str(e)}")

    @strawberry.mutation
    async def remove_hotel_amenities(
        self,
        hotel_id: str,
        amenities: List[str]
    ) -> Hotel:
        try:
            db = await MongoDB.get_database()
            
            # Check if hotel exists
            hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            if not hotel:
                raise ValueError("Hotel not found")

            # Remove specified amenities
            await db.hotels.update_one(
                {"_id": ObjectId(hotel_id)},
                {
                    "$pull": {"amenities": {"$in": amenities}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )

            updated_hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            return Hotel.from_db(updated_hotel)

        except Exception as e:
            raise ValueError(f"Error removing hotel amenities: {str(e)}")

    @strawberry.mutation
    async def update_hotel_images(
        self,
        hotel_id: str,
        images: List[str],
        operation: str = "add"  # "add" or "remove"
    ) -> Hotel:
        try:
            db = await MongoDB.get_database()
            
            # Check if hotel exists
            hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            if not hotel:
                raise ValueError("Hotel not found")

            if operation == "add":
                update_operation = {
                    "$addToSet": {"images": {"$each": images}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            elif operation == "remove":
                update_operation = {
                    "$pull": {"images": {"$in": images}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            else:
                raise ValueError("Invalid operation. Use 'add' or 'remove'")

            await db.hotels.update_one(
                {"_id": ObjectId(hotel_id)},
                update_operation
            )

            updated_hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            return Hotel.from_db(updated_hotel)

        except Exception as e:
            raise ValueError(f"Error updating hotel images: {str(e)}")

    @strawberry.mutation
    async def change_hotel_status(
        self,
        hotel_id: str,
        status: HotelStatus,
        reason: Optional[str] = None
    ) -> Hotel:
        try:
            db = await MongoDB.get_database()
            
            # Check if hotel exists
            hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            if not hotel:
                raise ValueError("Hotel not found")

            # Update status
            update_dict = {
                "status": status.value,
                "updated_at": datetime.utcnow()
            }
            
            if reason:
                update_dict["status_change_reason"] = reason
                update_dict["status_changed_at"] = datetime.utcnow()

            await db.hotels.update_one(
                {"_id": ObjectId(hotel_id)},
                {"$set": update_dict}
            )

            updated_hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            return Hotel.from_db(updated_hotel)

        except Exception as e:
            raise ValueError(f"Error changing hotel status: {str(e)}")

    @strawberry.mutation
    async def assign_hotel_admin(
        self,
        hotel_id: str,
        admin_id: str
    ) -> Hotel:
        try:
            db = await MongoDB.get_database()
            
            # Check if hotel exists
            hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            if not hotel:
                raise ValueError("Hotel not found")

            # Check if admin exists and has appropriate role
            admin = await db.users.find_one({
                "_id": ObjectId(admin_id),
                "role": {"$in": ["superadmin", "hotel_admin"]}
            })
            if not admin:
                raise ValueError("Admin not found or has insufficient privileges")

            # Update hotel's admin
            await db.hotels.update_one(
                {"_id": ObjectId(hotel_id)},
                {
                    "$set": {
                        "admin_id": admin_id,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            # Update admin's hotel assignments
            await db.users.update_one(
                {"_id": ObjectId(admin_id)},
                {"$addToSet": {"hotel_ids": hotel_id}}
            )

            # Remove hotel from previous admin's assignments
            if hotel.get("admin_id") and hotel["admin_id"] != admin_id:
                await db.users.update_one(
                    {"_id": ObjectId(hotel["admin_id"])},
                    {"$pull": {"hotel_ids": hotel_id}}
                )

            updated_hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            return Hotel.from_db(updated_hotel)

        except Exception as e:
            raise ValueError(f"Error assigning hotel admin: {str(e)}")

    @strawberry.mutation
    async def update_hotel_location(
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
        try:
            db = await MongoDB.get_database()
            
            # Check if hotel exists
            hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            if not hotel:
                raise ValueError("Hotel not found")

            # Build update dictionary
            update_dict = {
                "latitude": latitude,
                "longitude": longitude,
                "updated_at": datetime.utcnow()
            }
            
            if address:
                update_dict["address"] = address
            if city:
                update_dict["city"] = city
            if state:
                update_dict["state"] = state
            if country:
                update_dict["country"] = country
            if zipcode:
                update_dict["zipcode"] = zipcode

            await db.hotels.update_one(
                {"_id": ObjectId(hotel_id)},
                {"$set": update_dict}
            )

            updated_hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
            return Hotel.from_db(updated_hotel)

        except Exception as e:
            raise ValueError(f"Error updating hotel location: {str(e)}")