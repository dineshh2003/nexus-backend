# app/graphql/mutations/housekeeping_mutations.py
import strawberry
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.graphql.types.housekeeping import (
    HousekeepingTask,
    HousekeepingTaskInput,
    HousekeepingTaskUpdateInput,
    TaskVerificationInput,
    TaskStatus,
    TaskPriority,
    TaskType,
    ScheduleInput,
    HousekeepingSchedule
)
from app.db.mongodb import MongoDB

@strawberry.type
class HousekeepingMutations:
    @strawberry.mutation
    async def create_housekeeping_task(
        self,
        task_data: HousekeepingTaskInput
    ) -> HousekeepingTask:
        try:
            db = await MongoDB.get_database()
            
            # Validate hotel and room
            room = await db.rooms.find_one({
                "_id": ObjectId(task_data.room_id),
                "hotel_id": task_data.hotel_id
            })
            if not room:
                raise ValueError("Room not found in specified hotel")

            # Create task
            task_dict = {
                "hotel_id": task_data.hotel_id,
                "room_id": task_data.room_id,
                "task_type": task_data.task_type,
                "priority": task_data.priority,
                "status": TaskStatus.PENDING.value,
                "assigned_to": task_data.assigned_to,
                "scheduled_date": task_data.scheduled_date,
                "checklist": [item.dict() for item in task_data.checklist],
                "notes": task_data.notes,
                "issues_reported": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": "system",
                "updated_by": "system"
            }

            result = await db.housekeeping_tasks.insert_one(task_dict)
            task_dict["id"] = str(result.inserted_id)

            # Update room status if needed
            if room["status"] not in ["occupied", "out_of_order"]:
                await db.rooms.update_one(
                    {"_id": ObjectId(task_data.room_id)},
                    {
                        "$set": {
                            "status": "cleaning",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )

            return HousekeepingTask.from_db(task_dict)

        except Exception as e:
            raise ValueError(f"Error creating housekeeping task: {str(e)}")

    @strawberry.mutation
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        notes: Optional[str] = None
    ) -> HousekeepingTask:
        try:
            db = await MongoDB.get_database()
            
            # Get task
            task = await db.housekeeping_tasks.find_one({"_id": ObjectId(task_id)})
            if not task:
                raise ValueError("Task not found")

            update_dict = {
                "status": status.value,
                "updated_at": datetime.utcnow(),
                "updated_by": "system"
            }

            if notes:
                update_dict["notes"] = notes

            # Handle status-specific updates
            if status == TaskStatus.IN_PROGRESS:
                update_dict["start_time"] = datetime.utcnow()
            elif status == TaskStatus.COMPLETED:
                update_dict["end_time"] = datetime.utcnow()
                
                # Calculate duration
                if task.get("start_time"):
                    duration = (datetime.utcnow() - task["start_time"]).total_seconds() / 60
                    update_dict["duration_minutes"] = int(duration)

                # Update room status if cleaning task
                if task["task_type"] == TaskType.CLEANING.value:
                    await db.rooms.update_one(
                        {"_id": ObjectId(task["room_id"])},
                        {
                            "$set": {
                                "status": "available",
                                "last_cleaned": datetime.utcnow(),
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )

            await db.housekeeping_tasks.update_one(
                {"_id": ObjectId(task_id)},
                {"$set": update_dict}
            )

            updated_task = await db.housekeeping_tasks.find_one({"_id": ObjectId(task_id)})
            return HousekeepingTask.from_db(updated_task)

        except Exception as e:
            raise ValueError(f"Error updating task status: {str(e)}")

# app/graphql/mutations/housekeeping_mutations.py (continued)
    @strawberry.mutation
    async def verify_task(self, verification_data: TaskVerificationInput) -> HousekeepingTask:
        try:
            db = await MongoDB.get_database()
            
            # Get task
            task = await db.housekeeping_tasks.find_one({"_id": ObjectId(verification_data.task_id)})
            if not task:
                raise ValueError("Task not found")

            if task["status"] != TaskStatus.COMPLETED.value:
                raise ValueError("Only completed tasks can be verified")

            update_dict = {
                "status": TaskStatus.VERIFIED.value if verification_data.verification_status else TaskStatus.IN_PROGRESS.value,
                "verified_by": verification_data.verified_by,
                "verification_notes": verification_data.verification_notes,
                "verification_date": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "updated_by": "system"
            }

            await db.housekeeping_tasks.update_one(
                {"_id": ObjectId(verification_data.task_id)},
                {"$set": update_dict}
            )

            updated_task = await db.housekeeping_tasks.find_one({"_id": ObjectId(verification_data.task_id)})
            return HousekeepingTask.from_db(updated_task)

        except Exception as e:
            raise ValueError(f"Error verifying task: {str(e)}")

    @strawberry.mutation
    async def assign_bulk_tasks(
        self,
        staff_id: str,
        task_ids: List[str],
        notes: Optional[str] = None
    ) -> List[HousekeepingTask]:
        try:
            db = await MongoDB.get_database()
            
            # Validate staff exists
            staff = await db.users.find_one({
                "_id": ObjectId(staff_id),
                "role": "housekeeper"
            })
            if not staff:
                raise ValueError("Staff member not found or not a housekeeper")

            # Update tasks
            task_object_ids = [ObjectId(tid) for tid in task_ids]
            
            await db.housekeeping_tasks.update_many(
                {
                    "_id": {"$in": task_object_ids},
                    "status": TaskStatus.PENDING.value
                },
                {
                    "$set": {
                        "assigned_to": staff_id,
                        "assignment_date": datetime.utcnow(),
                        "assignment_notes": notes,
                        "updated_at": datetime.utcnow(),
                        "updated_by": "system"
                    }
                }
            )

            # Return updated tasks
            updated_tasks = await db.housekeeping_tasks.find(
                {"_id": {"$in": task_object_ids}}
            ).to_list(None)
            
            return [HousekeepingTask.from_db(task) for task in updated_tasks]

        except Exception as e:
            raise ValueError(f"Error assigning tasks: {str(e)}")

    @strawberry.mutation
    async def report_cleaning_issue(
        self,
        task_id: str,
        issue_description: str,
        priority: TaskPriority,
        requires_maintenance: bool = False
    ) -> HousekeepingTask:
        try:
            db = await MongoDB.get_database()
            
            # Get task
            task = await db.housekeeping_tasks.find_one({"_id": ObjectId(task_id)})
            if not task:
                raise ValueError("Task not found")

            issue = {
                "description": issue_description,
                "reported_at": datetime.utcnow(),
                "reported_by": "system",
                "priority": priority.value,
                "status": "pending",
                "requires_maintenance": requires_maintenance
            }

            # Update task
            await db.housekeeping_tasks.update_one(
                {"_id": ObjectId(task_id)},
                {
                    "$push": {"issues_reported": issue},
                    "$set": {
                        "updated_at": datetime.utcnow(),
                        "updated_by": "system"
                    }
                }
            )

            # Create maintenance task if required
            if requires_maintenance:
                maintenance_task = {
                    "hotel_id": task["hotel_id"],
                    "room_id": task["room_id"],
                    "task_type": "maintenance",
                    "description": f"Maintenance required: {issue_description}",
                    "priority": priority.value,
                    "status": "pending",
                    "reported_by": "housekeeping",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await db.maintenance_tasks.insert_one(maintenance_task)

            updated_task = await db.housekeeping_tasks.find_one({"_id": ObjectId(task_id)})
            return HousekeepingTask.from_db(updated_task)

        except Exception as e:
            raise ValueError(f"Error reporting issue: {str(e)}")

    @strawberry.mutation
    async def create_housekeeping_schedule(
        self,
        schedule_data: ScheduleInput
    ) -> HousekeepingSchedule:
        try:
            db = await MongoDB.get_database()
            
            # Create schedule
            schedule_dict = {
                "hotel_id": schedule_data.hotel_id,
                "date": schedule_data.date,
                "shift": schedule_data.shift,
                "staff_assignments": schedule_data.staff_assignments,
                "room_assignments": schedule_data.room_assignments,
                "notes": schedule_data.notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": "system",
                "updated_by": "system"
            }

            result = await db.housekeeping_schedules.insert_one(schedule_dict)

            # Create tasks for each room assignment
            for assignment in schedule_data.room_assignments:
                task = {
                    "hotel_id": schedule_data.hotel_id,
                    "room_id": assignment["room_id"],
                    "task_type": TaskType.CLEANING.value,
                    "priority": TaskPriority.MEDIUM.value,
                    "status": TaskStatus.PENDING.value,
                    "assigned_to": assignment.get("assigned_to"),
                    "scheduled_date": schedule_data.date,
                    "schedule_id": str(result.inserted_id),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                await db.housekeeping_tasks.insert_one(task)

            schedule_dict["id"] = str(result.inserted_id)
            return HousekeepingSchedule.from_db(schedule_dict)

        except Exception as e:
            raise ValueError(f"Error creating schedule: {str(e)}")