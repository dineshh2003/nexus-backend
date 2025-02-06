import strawberry
from typing import Optional, List

# Import mutation classes
from ..graphql.mutations.user_mutations import UserMutations
from ..graphql.mutations.hotel_mutations import HotelMutations
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

# Import query classes
from ..graphql.queries.user_queries import UserQueries
from ..graphql.queries.hotel_queries import HotelQueries

@strawberry.type
class Query:
    """
    Root query class for GraphQL schema.
    Includes both user and hotel queries.
    """
    @strawberry.field
    def user(self) -> UserQueries:
        return UserQueries()
    
    @strawberry.field
    def hotel(self) -> HotelQueries:
        return HotelQueries()

@strawberry.type
class Mutation:
    """
    Root mutation class for GraphQL schema.
    Includes both user and hotel mutations.
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

# Create the schema with both queries and mutations
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)