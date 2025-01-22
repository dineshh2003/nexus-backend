# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from app.db.mongodb import MongoDB
from app.graphql.schema import schema

app = FastAPI(title="Hotel Management System API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL route configuration
graphql_app = GraphQLRouter(
    schema,
    graphiql=True  # Enable GraphiQL interface
)
app.include_router(graphql_app, prefix="/graphql")

@app.on_event("startup")
async def startup_db_client():
    await MongoDB.connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await MongoDB.close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Welcome to HMS API"}