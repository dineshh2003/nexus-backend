# app/graphql/mutations/user_mutations.py
import strawberry
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.graphql.types.user import User, UserInput, UserUpdateInput, UserRole
from app.core.security import get_password_hash, verify_password
from app.db.mongodb import MongoDB

@strawberry.type
class UserMutations:
    @strawberry.mutation
    async def create_user(self, user_data: UserInput) -> User:
        try:
            db = MongoDB.database
            
            # Check if user already exists
            existing_user = await db.users.find_one({"email": user_data.email})
            if existing_user:
                raise ValueError("User with this email already exists")

            # Validate role
            if user_data.role not in [role.value for role in UserRole]:
                raise ValueError(f"Invalid role: {user_data.role}")

            # Create user document
            user_dict = {
                "email": user_data.email,
                "name": user_data.name,
                "role": user_data.role,
                "hashed_password": get_password_hash(user_data.password),
                "phone": user_data.phone,
                "hotel_ids": user_data.hotel_ids or [],
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            result = await db.users.insert_one(user_dict)
            user_dict["id"] = str(result.inserted_id)
            
            return User.from_db(user_dict)
            
        except Exception as e:
            raise ValueError(f"Error creating user: {str(e)}")

    @strawberry.mutation
    async def update_user(self, id: str, user_data: UserUpdateInput) -> User:
        try:
            db = MongoDB.database
            
            # Check if user exists
            existing_user = await db.users.find_one({"_id": ObjectId(id)})
            if not existing_user:
                raise ValueError("User not found")

            update_dict = {}
            
            if user_data.email is not None:
                # Check if email is already taken by another user
                email_exists = await db.users.find_one({
                    "email": user_data.email,
                    "_id": {"$ne": ObjectId(id)}
                })
                if email_exists:
                    raise ValueError("Email is already taken")
                update_dict["email"] = user_data.email

            if user_data.name is not None:
                update_dict["name"] = user_data.name

            if user_data.role is not None:
                if user_data.role not in [role.value for role in UserRole]:
                    raise ValueError(f"Invalid role: {user_data.role}")
                update_dict["role"] = user_data.role

            if user_data.phone is not None:
                update_dict["phone"] = user_data.phone

            if user_data.hotel_ids is not None:
                update_dict["hotel_ids"] = user_data.hotel_ids

            if user_data.is_active is not None:
                update_dict["is_active"] = user_data.is_active

            update_dict["updated_at"] = datetime.utcnow()

            # Update user
            await db.users.update_one(
                {"_id": ObjectId(id)},
                {"$set": update_dict}
            )

            updated_user = await db.users.find_one({"_id": ObjectId(id)})
            return User.from_db(updated_user)

        except Exception as e:
            raise ValueError(f"Error updating user: {str(e)}")

    @strawberry.mutation
    async def delete_user(self, id: str) -> bool:
        try:
            db = MongoDB.database
            
            # Check if user exists
            existing_user = await db.users.find_one({"_id": ObjectId(id)})
            if not existing_user:
                raise ValueError("User not found")

            # Soft delete by setting is_active to False
            result = await db.users.update_one(
                {"_id": ObjectId(id)},
                {
                    "$set": {
                        "is_active": False,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            return result.modified_count > 0

        except Exception as e:
            raise ValueError(f"Error deleting user: {str(e)}")

    @strawberry.mutation
    async def change_password(
        self,
        id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        try:
            db = MongoDB.database
            
            # Check if user exists
            user = await db.users.find_one({"_id": ObjectId(id)})
            if not user:
                raise ValueError("User not found")

            # Verify current password
            if not verify_password(current_password, user["hashed_password"]):
                raise ValueError("Current password is incorrect")

            # Update password
            await db.users.update_one(
                {"_id": ObjectId(id)},
                {
                    "$set": {
                        "hashed_password": get_password_hash(new_password),
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            return True

        except Exception as e:
            raise ValueError(f"Error changing password: {str(e)}")

    @strawberry.mutation
    async def assign_hotels_to_user(
        self,
        user_id: str,
        hotel_ids: List[str]
    ) -> User:
        try:
            db = MongoDB.database
            
            # Check if user exists
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValueError("User not found")

            # Check if all hotels exist
            for hotel_id in hotel_ids:
                hotel = await db.hotels.find_one({"_id": ObjectId(hotel_id)})
                if not hotel:
                    raise ValueError(f"Hotel not found: {hotel_id}")

            # Update user's hotel assignments
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "hotel_ids": hotel_ids,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
            return User.from_db(updated_user)

        except Exception as e:
            raise ValueError(f"Error assigning hotels to user: {str(e)}")

    @strawberry.mutation
    async def update_user_role(
        self,
        user_id: str,
        new_role: str
    ) -> User:
        try:
            db = MongoDB.database
            
            # Check if user exists
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValueError("User not found")

            # Validate new role
            if new_role not in [role.value for role in UserRole]:
                raise ValueError(f"Invalid role: {new_role}")

            # Update user's role
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "role": new_role,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
            return User.from_db(updated_user)

        except Exception as e:
            raise ValueError(f"Error updating user role: {str(e)}")