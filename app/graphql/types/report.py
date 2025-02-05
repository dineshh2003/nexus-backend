# app/graphql/types/report.py
import strawberry
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

@strawberry.enum
class ReportPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"

@strawberry.type
class OccupancyStats:
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    out_of_order_rooms: int
    occupancy_rate: float
    average_daily_rate: float
    revenue_per_available_room: float

@strawberry.type
class RevenueStats:
    room_revenue: float
    food_beverage_revenue: float
    other_revenue: float
    total_revenue: float
    average_daily_rate: float
    revenue_per_available_room: float
    cancellation_revenue: float
    refunds: float
    net_revenue: float

@strawberry.type
class BookingSourceDistribution:
    source: str
    count: int

@strawberry.type
class StaffProductivity:
    staff_id: str
    productivity_rate: float

@strawberry.type
class EquipmentDowntime:
    equipment_id: str
    downtime_hours: float

@strawberry.type
class ExpenseEntry:
    category: str
    amount: float

@strawberry.type
class BookingStats:
    total_bookings: int
    new_bookings: int
    cancelled_bookings: int
    no_shows: int
    check_ins: int
    check_outs: int
    average_length_of_stay: float
    average_lead_time: float
    booking_source_distribution: List[BookingSourceDistribution]  # Changed from Dict
@strawberry.type
class HousekeepingStats:
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    rooms_cleaned: int
    average_cleaning_time: float
    staff_productivity: List[StaffProductivity]  # Changed from Dict
    issues_reported: int

@strawberry.type
class MaintenanceStats:
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    emergency_repairs: int
    preventive_maintenance: int
    average_resolution_time: float
    cost_of_repairs: float
    equipment_downtime: List[EquipmentDowntime]

@strawberry.type
class FinancialReport:
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    revenue: RevenueStats
    expenses: List[ExpenseEntry]  # Changed from Dict
    profit_loss: float
    tax_collected: float
    outstanding_payments: float
    refunds_issued: float
@strawberry.type
class InventoryStatusItem:
    item_name: str
    quantity: int

@strawberry.type
class StaffAttendanceItem:
    staff_id: str
    attendance_hours: float

@strawberry.type
class OperationalReport:
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    occupancy: OccupancyStats
    bookings: BookingStats
    housekeeping: HousekeepingStats
    maintenance: MaintenanceStats
    inventory_status: List[InventoryStatusItem]  # Fixed
    staff_attendance: List[StaffAttendanceItem]  # Fixed

@strawberry.type
class GuestDemographic:
    category: str
    count: int

@strawberry.type
class SatisfactionScore:
    category: str
    score: float

@strawberry.type
class CustomerReport:
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    total_guests: int
    new_guests: int
    returning_guests: int
    average_stay_duration: float
    guest_demographics: List[GuestDemographic]  # Changed from Dict
    satisfaction_scores: List[SatisfactionScore]  # Changed from Dict
    complaints_filed: int
    resolved_complaints: int
    popular_amenities: List[str]

@strawberry.input
class ReportRequest:
    hotel_id: str
    report_type: str
    period: ReportPeriod
    start_date: datetime
    end_date: datetime
    include_sections: Optional[List[str]] = None
    format: str = "json"

@strawberry.type
class ReportSchedule:
    id: str
    hotel_id: str
    report_type: str
    period: ReportPeriod
    recipients: List[str]
    schedule_time: str
    last_sent: Optional[datetime]
    is_active: bool

@strawberry.input
class ReportScheduleInput:
    hotel_id: str
    report_type: str
    period: ReportPeriod
    recipients: List[str]