"""Data access repositories — one per entity."""
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.payment_repo import PaymentRepository
from app.data.repositories.time_log_repo import TimeLogRepository
from app.data.repositories.task_repo import TaskRepository
from app.data.repositories.contract_repo import ContractRepository

__all__ = [
    "ClientRepository",
    "ProjectRepository",
    "InvoiceRepository",
    "PaymentRepository",
    "TimeLogRepository",
    "TaskRepository",
    "ContractRepository",
]
