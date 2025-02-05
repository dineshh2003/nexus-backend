import strawberry
from typing import Optional, List

# Import mutation classes
from ..graphql.mutations.user_mutations import UserMutations
from ..graphql.types.user import User, UserInput, UserUpdateInput

# Import query classes
from ..graphql.queries.user_queries import UserQueries

@strawberry.type
class Query:
    """
    Root query class for GraphQL schema.
    You can uncomment and add more queries as needed.
    """
    @strawberry.field
    def user(self) -> UserQueries:
        return UserQueries()
    

@strawberry.type
class Mutation:
    """
    Root mutation class for GraphQL schema.
    Explicitly include all user-related mutations.
    """
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

# Create the schema with both queries and mutations
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
