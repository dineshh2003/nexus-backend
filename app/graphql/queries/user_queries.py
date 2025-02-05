import strawberry
from typing import List, Optional
from bson import ObjectId

from app.graphql.types.user import User, UserRole, UserPermission
from app.db.mongodb import MongoDB

@strawberry.type
class UserQueries:
    @strawberry.field
    async def get_user(self, id: str) -> Optional[User]:
        """Get a single user by ID"""
        try:
            user = await MongoDB.database.users.find_one({"_id": ObjectId(id)})
            return User.from_db(user) if user else None
        except Exception as e:
            raise ValueError(f"Error fetching user: {str(e)}")

    @strawberry.field
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a single user by email"""
        try:
            user = await MongoDB.database.users.find_one({"email": email})
            return User.from_db(user) if user else None
        except Exception as e:
            raise ValueError(f"Error fetching user by email: {str(e)}")

    @strawberry.field
    async def list_users(
        self,
        role: Optional[UserRole] = None,
        hotel_id: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """List users with optional filtering"""
        try:
            query = {}

            if role is not None:
                query["role"] = role

            if hotel_id is not None:
                query["hotel_ids"] = hotel_id

            if is_active is not None:
                query["is_active"] = is_active

            cursor = MongoDB.database.users.find(query).skip(skip).limit(limit)
            users = await cursor.to_list(length=limit)
            return [User.from_db(user) for user in users]
        except Exception as e:
            raise ValueError(f"Error listing users: {str(e)}")

    @strawberry.field
    async def get_hotel_staff(
        self,
        hotel_id: str,
        role: Optional[UserRole] = None
    ) -> List[User]:
        """Get all staff members for a specific hotel"""
        try:
            query = {"hotel_ids": hotel_id, "is_active": True}
            
            if role is not None:
                query["role"] = role

            cursor = MongoDB.database.users.find(query)
            users = await cursor.to_list(length=None)
            return [User.from_db(user) for user in users]
        except Exception as e:
            raise ValueError(f"Error fetching hotel staff: {str(e)}")

    @strawberry.field
    async def get_user_permissions(
        self,
        user_id: str
    ) -> List[UserPermission]:
        """Get permissions for a specific user"""
        try:
            cursor = MongoDB.database.user_permissions.find({"user_id": user_id})
            permissions = await cursor.to_list(length=None)
            return [UserPermission(**permission) for permission in permissions]
        except Exception as e:
            raise ValueError(f"Error fetching user permissions: {str(e)}")

    @strawberry.field
    async def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name or email"""
        try:
            search_query = {
                "$or": [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = MongoDB.database.users.find(search_query).skip(skip).limit(limit)
            users = await cursor.to_list(length=limit)
            return [User.from_db(user) for user in users]
        except Exception as e:
            raise ValueError(f"Error searching users: {str(e)}")