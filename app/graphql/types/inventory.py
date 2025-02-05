# app/graphql/types/inventory.py
import strawberry
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

@strawberry.enum
class InventoryCategory(str, Enum):
    ROOM_SUPPLIES = "room_supplies"
    CLEANING_SUPPLIES = "cleaning_supplies"
    LINENS = "linens"
    TOILETRIES = "toiletries"
    AMENITIES = "amenities"
    MAINTENANCE = "maintenance"
    FOOD_BEVERAGE = "food_beverage"
    OFFICE_SUPPLIES = "office_supplies"
    UNIFORMS = "uniforms"
    ELECTRONICS = "electronics"

@strawberry.enum
class InventoryStatus(str, Enum):
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    ON_ORDER = "on_order"

@strawberry.enum
class TransactionType(str, Enum):
    PURCHASE = "purchase"
    CONSUMPTION = "consumption"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    DAMAGE = "damage"
    TRANSFER = "transfer"

@strawberry.type
class Supplier:
    id: str
    name: str
    contact_person: str
    email: str
    phone: str
    address: str
    payment_terms: Optional[str]
    lead_time_days: int
    active: bool

@strawberry.type
class InventoryItem:
    id: str
    hotel_id: str
    name: str
    category: InventoryCategory
    description: Optional[str]
    sku: str
    unit_of_measure: str
    quantity: int
    reorder_point: int
    optimal_stock: int
    unit_price: float
    supplier_id: Optional[str]
    location: str
    status: InventoryStatus
    last_ordered: Optional[datetime]
    last_received: Optional[datetime]
    expiry_date: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_db(cls, db_data: dict):
        return cls(
            id=str(db_data['_id']),
            hotel_id=db_data['hotel_id'],
            name=db_data['name'],
            category=db_data['category'],
            description=db_data.get('description'),
            sku=db_data['sku'],
            unit_of_measure=db_data['unit_of_measure'],
            quantity=db_data['quantity'],
            reorder_point=db_data['reorder_point'],
            optimal_stock=db_data['optimal_stock'],
            unit_price=db_data['unit_price'],
            supplier_id=db_data.get('supplier_id'),
            location=db_data['location'],
            status=db_data['status'],
            last_ordered=db_data.get('last_ordered'),
            last_received=db_data.get('last_received'),
            expiry_date=db_data.get('expiry_date'),
            notes=db_data.get('notes'),
            created_at=db_data['created_at'],
            updated_at=db_data['updated_at']
        )

@strawberry.type
class InventoryTransaction:
    id: str
    item_id: str
    transaction_type: TransactionType
    quantity: int
    unit_price: Optional[float]
    total_amount: Optional[float]
    reference_number: Optional[str]
    source_location: Optional[str]
    destination_location: Optional[str]
    performed_by: str
    notes: Optional[str]
    created_at: datetime

@strawberry.type
class StockItem:
    item_id: str
    quantity: int
    notes: Optional[str]

@strawberry.type
class Discrepancy:
    item_id: str
    expected_quantity: int
    actual_quantity: int
    notes: Optional[str]

@strawberry.type
class StockCount:
    id: str
    hotel_id: str
    count_date: datetime
    status: str
    counted_by: str
    verified_by: Optional[str]
    items: List[StockItem]  # Fixed
    discrepancies: List[Discrepancy]  # Fixed
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

@strawberry.input
class InventoryItemInput:
    hotel_id: str
    name: str
    category: InventoryCategory
    description: Optional[str]
    sku: str
    unit_of_measure: str
    quantity: int
    reorder_point: int
    optimal_stock: int
    unit_price: float
    supplier_id: Optional[str]
    location: str
    expiry_date: Optional[datetime]
    notes: Optional[str]

@strawberry.input
class InventoryTransactionInput:
    item_id: str
    transaction_type: TransactionType
    quantity: int
    unit_price: Optional[float]
    reference_number: Optional[str]
    source_location: Optional[str]
    destination_location: Optional[str]
    notes: Optional[str]

@strawberry.input
class StockItemInput:
    item_id: str
    quantity: int
    notes: Optional[str] = None

@strawberry.input
class StockCountInput:
    hotel_id: str
    items: List[StockItemInput]  # Fixed
    notes: Optional[str]