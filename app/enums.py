from enum import Enum

class ReminderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"
    notified = "notified"
    overdue = "overdue"
    