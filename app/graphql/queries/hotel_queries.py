import strawberry
from typing import List, Optional
from bson import ObjectId

from app.graphql.types.hotel import Hotel, HotelStatus
from app.db.mongodb import MongoDB

@strawberry.type
class HotelQueries:
    @strawberry.field
    async def get_hotel(self, id: str) -> Optional[Hotel]:
        """Get a single hotel by ID"""
        try:
            hotel = await MongoDB.database.hotels.find_one({"_id": ObjectId(id)})
            return Hotel.from_db(hotel)
        except Exception as e:
            raise ValueError(f"Error fetching hotel: {str(e)}")

    @strawberry.field
    async def get_hotels(
        self,
        status: Optional[HotelStatus] = None,
        city: Optional[str] = None,
        country: Optional[str] = None,
        admin_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Hotel]:
        """List hotels with optional filtering"""
        try:
            query = {}

            if status:
                query["status"] = status
            if city:
                query["city"] = city
            if country:
                query["country"] = country
            if admin_id:
                query["admin_id"] = admin_id

            hotels = await MongoDB.database.hotels.find(query).skip(offset).limit(limit).to_list(length=limit)
            return [Hotel.from_db(hotel) for hotel in hotels if hotel]
        except Exception as e:
            raise ValueError(f"Error fetching hotels: {str(e)}")

    @strawberry.field
    async def search_hotels(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Hotel]:
        """Search hotels by name, city, country, or address"""
        try:
            search_query = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"city": {"$regex": query, "$options": "i"}},
                    {"country": {"$regex": query, "$options": "i"}},
                    {"address": {"$regex": query, "$options": "i"}}
                ]
            }

            hotels = await MongoDB.database.hotels.find(search_query).skip(offset).limit(limit).to_list(length=limit)
            return [Hotel.from_db(hotel) for hotel in hotels if hotel]
        except Exception as e:
            raise ValueError(f"Error searching hotels: {str(e)}")

    @strawberry.field
    async def get_hotels_by_amenities(
        self,
        amenities: List[str],
        limit: int = 10,
        offset: int = 0
    ) -> List[Hotel]:
        """Get hotels that have all specified amenities"""
        try:
            query = {"amenities": {"$all": amenities}}
            hotels = await MongoDB.database.hotels.find(query).skip(offset).limit(limit).to_list(length=limit)
            return [Hotel.from_db(hotel) for hotel in hotels if hotel]
        except Exception as e:
            raise ValueError(f"Error fetching hotels by amenities: {str(e)}")

    @strawberry.field
    async def get_hotels_by_location(
        self,
        latitude: float,
        longitude: float,
        radius: float,  # in kilometers
        limit: int = 10,
        offset: int = 0
    ) -> List[Hotel]:
        """Get hotels within a specified radius of a location"""
        try:
            query = {
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [longitude, latitude]
                        },
                        "$maxDistance": radius * 1000  # Convert km to meters
                    }
                }
            }

            hotels = await MongoDB.database.hotels.find(query).skip(offset).limit(limit).to_list(length=limit)
            return [Hotel.from_db(hotel) for hotel in hotels if hotel]
        except Exception as e:
            raise ValueError(f"Error fetching hotels by location: {str(e)}")

    @strawberry.field
    async def get_hotels_by_rating(
        self,
        min_rating: int,
        max_rating: int,
        limit: int = 10,
        offset: int = 0
    ) -> List[Hotel]:
        """Get hotels within a specified star rating range"""
        try:
            query = {
                "star_rating": {
                    "$gte": min_rating,
                    "$lte": max_rating
                }
            }

            hotels = await MongoDB.database.hotels.find(query).skip(offset).limit(limit).to_list(length=limit)
            return [Hotel.from_db(hotel) for hotel in hotels if hotel]
        except Exception as e:
            raise ValueError(f"Error fetching hotels by rating: {str(e)}")

    @strawberry.field
    async def get_hotels_by_admin(
        self,
        admin_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Hotel]:
        """Get all hotels managed by a specific admin"""
        try:
            query = {"admin_id": admin_id}
            hotels = await MongoDB.database.hotels.find(query).skip(offset).limit(limit).to_list(length=limit)
            return [Hotel.from_db(hotel) for hotel in hotels if hotel]
        except Exception as e:
            raise ValueError(f"Error fetching hotels by admin: {str(e)}")