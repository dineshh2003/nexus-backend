# app/db/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT, GEOSPHERE
from app.core.config import settings
import os
import asyncio



class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    @classmethod
    async def connect_to_mongo(cls):
        max_retries = 5
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                print(f"Connecting to MongoDB (attempt {attempt+1}/{max_retries})...")
                cls.client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    serverSelectionTimeoutMS=5000  # 5 second timeout
                )
                # Wait for connection to be established
                await cls.client.server_info()
                cls.database = cls.client[settings.DATABASE_NAME]
                print(f"Connected to MongoDB on attempt {attempt+1}!")
                
                # Initialize database after connection
                await cls.init_db()
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Failed to connect to MongoDB: {e}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"Could not connect to MongoDB after {max_retries} attempts: {e}")
                    raise

    @classmethod
    async def get_database(cls):
        """
        Returns the database instance. If not connected yet, establishes connection first.
        """
        if cls.database is None:
            await cls.connect_to_mongo()
        return cls.database
    

    @classmethod
    async def close_mongo_connection(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed!")


    @classmethod
    async def init_db(cls):
        """Initialize database with indexes and collection validations"""
        try:
            # Create indexes
            await cls.create_indexes()
            
            # Set up collection validations
            await cls.setup_validations()
            
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    @classmethod
    async def create_indexes(cls):
        """Create all necessary indexes"""
        try:
            # Users Collection Indexes
            await cls.database.users.create_indexes([
                IndexModel([("email", ASCENDING)], unique=True),
                IndexModel([("role", ASCENDING)]),
                IndexModel([("hotel_ids", ASCENDING)]),
                IndexModel([("is_active", ASCENDING)]),
                IndexModel([("name", TEXT)])
            ])

            # Hotels Collection Indexes
            await cls.database.hotels.create_indexes([
            # Existing indexes
            IndexModel([("name", TEXT)]),
            IndexModel([("city", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
            IndexModel([("admin_id", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
            
            # New indexes for enhanced functionality
            IndexModel([("country", ASCENDING)]),
            IndexModel([("star_rating", ASCENDING)]),
            IndexModel([("amenities", ASCENDING)]),
            IndexModel([("location", GEOSPHERE)]),  # For geospatial queries
            IndexModel([("policies.check_in_time", ASCENDING)]),
            IndexModel([("policies.check_out_time", ASCENDING)]),
            # Compound indexes for common query patterns
            IndexModel([("status", ASCENDING), ("city", ASCENDING)]),
            IndexModel([("status", ASCENDING), ("star_rating", ASCENDING)])
        ])

            # Rooms Collection Indexes
            await cls.database.rooms.create_indexes([
                IndexModel([("hotel_id", ASCENDING)]),
                IndexModel([("room_number", ASCENDING)]),
                IndexModel([("hotel_id", ASCENDING), ("room_number", ASCENDING)], unique=True),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("room_type", ASCENDING)]),
                IndexModel([("floor", ASCENDING)])
            ])

            # Bookings Collection Indexes
            await cls.database.bookings.create_indexes([
                IndexModel([("hotel_id", ASCENDING)]),
                IndexModel([("room_id", ASCENDING)]),
                IndexModel([("booking_number", ASCENDING)], unique=True),
                IndexModel([("guest.email", ASCENDING)]),
                IndexModel([("check_in_date", ASCENDING)]),
                IndexModel([("check_out_date", ASCENDING)]),
                IndexModel([("booking_status", ASCENDING)]),
                IndexModel([("payment_status", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)])
            ])

            # Housekeeping Tasks Collection Indexes
            await cls.database.housekeeping_tasks.create_indexes([
                IndexModel([("hotel_id", ASCENDING)]),
                IndexModel([("room_id", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("assigned_to", ASCENDING)]),
                IndexModel([("scheduled_date", ASCENDING)]),
                IndexModel([("priority", ASCENDING)])
            ])

            # Inventory Collection Indexes
            await cls.database.inventory.create_indexes([
                IndexModel([("hotel_id", ASCENDING)]),
                IndexModel([("sku", ASCENDING)]),
                IndexModel([("hotel_id", ASCENDING), ("sku", ASCENDING)], unique=True),
                IndexModel([("category", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("quantity", ASCENDING)])
            ])

            # Maintenance Tasks Collection Indexes
            await cls.database.maintenance_tasks.create_indexes([
                IndexModel([("hotel_id", ASCENDING)]),
                IndexModel([("room_id", ASCENDING)]),
                IndexModel([("status", ASCENDING)]),
                IndexModel([("priority", ASCENDING)]),
                IndexModel([("scheduled_date", ASCENDING)]),
                IndexModel([("assigned_to", ASCENDING)])
            ])

            # Reports Collection Indexes
            await cls.database.reports.create_indexes([
                IndexModel([("hotel_id", ASCENDING)]),
                IndexModel([("report_type", ASCENDING)]),
                IndexModel([("created_at", DESCENDING)])
            ])

            print("All indexes created successfully!")
        except Exception as e:
            print(f"Error creating indexes: {e}")
            raise
    
    @classmethod
    async def setup_validations(cls):
        """Set up collection validations"""
        try:
            # Users Collection Validation
            await cls.database.command({
                "collMod": "users",
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["email", "name", "role", "hashed_password", "created_at", "updated_at"],
                        "properties": {
                            "email": {"bsonType": "string"},
                            "name": {"bsonType": "string"},
                            "role": {"enum": ["superadmin", "hotel_admin", "staff", "housekeeper"]},
                            "hashed_password": {"bsonType": "string"},
                            "phone": {"bsonType": "string"},
                            "hotel_ids": {"bsonType": "array"},
                            "is_active": {"bsonType": "bool"},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            })

            # Hotels Collection Validation
            await cls.database.command({
            "collMod": "hotels",
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "name", 
                        "address", 
                        "city", 
                        "state",
                        "country",
                        "zipcode",
                        "status", 
                        "admin_id", 
                        "floor_count",
                        "policies",
                        "created_at", 
                        "updated_at"
                    ],
                    "properties": {
                        "name": {"bsonType": "string"},
                        "description": {"bsonType": ["string", "null"]},
                        "address": {"bsonType": "string"},
                        "city": {"bsonType": "string"},
                        "state": {"bsonType": "string"},
                        "country": {"bsonType": "string"},
                        "zipcode": {"bsonType": "string"},
                        "latitude": {"bsonType": ["double", "null"]},
                        "longitude": {"bsonType": ["double", "null"]},
                        "contact_phone": {"bsonType": "string"},
                        "contact_email": {"bsonType": "string"},
                        "website": {"bsonType": ["string", "null"]},
                        "status": {
                            "enum": [
                                "active", 
                                "inactive", 
                                "maintenance", 
                                "under_construction"
                            ]
                        },
                        "admin_id": {"bsonType": "string"},
                        "room_count": {"bsonType": "int"},
                        "floor_count": {"bsonType": "int"},
                        "star_rating": {"bsonType": ["int", "null"]},
                        "amenities": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "policies": {
                            "bsonType": "object",
                            "required": [
                                "check_in_time",
                                "check_out_time",
                                "cancellation_hours",
                                "payment_methods",
                                "pet_policy"
                            ],
                            "properties": {
                                "check_in_time": {"bsonType": "string"},
                                "check_out_time": {"bsonType": "string"},
                                "cancellation_hours": {"bsonType": "int"},
                                "payment_methods": {
                                    "bsonType": "array",
                                    "items": {"bsonType": "string"}
                                },
                                "pet_policy": {"bsonType": "string"},
                                "extra_bed_policy": {"bsonType": ["string", "null"]}
                            }
                        },
                        "images": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "location": {
                            "bsonType": ["object", "null"],
                            "properties": {
                                "type": {"bsonType": "string"},
                                "coordinates": {
                                    "bsonType": "array",
                                    "items": {"bsonType": "double"}
                                }
                            }
                        },
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": "date"}
                    }
                }
            }
        })

            # Bookings Collection Validation
            await cls.database.command({
                "collMod": "bookings",
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["hotel_id", "room_id", "guest", "check_in_date", "check_out_date", "created_at", "updated_at"],
                        "properties": {
                            "hotel_id": {"bsonType": "string"},
                            "room_id": {"bsonType": "string"},
                            "booking_number": {"bsonType": "string"},
                            "guest": {
                                "bsonType": "object",
                                "required": ["name", "email", "phone"],
                                "properties": {
                                    "name": {"bsonType": "string"},
                                    "email": {"bsonType": "string"},
                                    "phone": {"bsonType": "string"}
                                }
                            },
                            "booking_status": {"enum": ["pending", "confirmed", "checked_in", "checked_out", "cancelled"]},
                            "payment_status": {"enum": ["pending", "partial", "paid", "refunded"]},
                            "total_amount": {"bsonType": "double"},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            })

            # Housekeeping Tasks Collection Validation
            await cls.database.command({
                "collMod": "housekeeping_tasks",
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["hotel_id", "room_id", "task_type", "status", "created_at", "updated_at"],
                        "properties": {
                            "hotel_id": {"bsonType": "string"},
                            "room_id": {"bsonType": "string"},
                            "task_type": {"enum": ["cleaning", "turndown", "inspection", "maintenance"]},
                            "status": {"enum": ["pending", "in_progress", "completed", "verified", "cancelled"]},
                            "assigned_to": {"bsonType": "string"},
                            "priority": {"enum": ["low", "medium", "high", "urgent"]},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            })

            # Inventory Collection Validation
            await cls.database.command({
                "collMod": "inventory",
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["hotel_id", "name", "category", "quantity", "created_at", "updated_at"],
                        "properties": {
                            "hotel_id": {"bsonType": "string"},
                            "name": {"bsonType": "string"},
                            "category": {"enum": ["room_supplies", "cleaning_supplies", "linens", "amenities", "maintenance"]},
                            "quantity": {"bsonType": "int"},
                            "reorder_point": {"bsonType": "int"},
                            "unit_price": {"bsonType": "double"},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            })

            # Maintenance Tasks Collection Validation
            await cls.database.command({
                "collMod": "maintenance_tasks",
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["hotel_id", "task_type", "status", "priority", "created_at", "updated_at"],
                        "properties": {
                            "hotel_id": {"bsonType": "string"},
                            "room_id": {"bsonType": "string"},
                            "task_type": {"enum": ["preventive", "corrective", "emergency"]},
                            "status": {"enum": ["pending", "in_progress", "completed", "verified", "cancelled"]},
                            "priority": {"enum": ["low", "medium", "high", "urgent"]},
                            "created_at": {"bsonType": "date"},
                            "updated_at": {"bsonType": "date"}
                        }
                    }
                }
            })

            # Reports Collection Validation
            await cls.database.command({
                "collMod": "reports",
                "validator": {
                    "$jsonSchema": {
                        "bsonType": "object",
                        "required": ["hotel_id", "report_type", "created_at"],
                        "properties": {
                            "hotel_id": {"bsonType": "string"},
                            "report_type": {"enum": ["operational", "financial", "inventory", "housekeeping"]},
                            "data": {"bsonType": "object"},
                            "created_at": {"bsonType": "date"}
                        }
                    }
                }
            })

            print("All collection validations set up successfully!")
        except Exception as e:
            print(f"Error setting up collection validations: {e}")
            raise


