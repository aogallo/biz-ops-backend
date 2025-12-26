# =======
# Enum
# =======

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.internal.shared.entity import SoftDeleteMixin, TimestampMixin


class SubscriptionPlan(str, Enum):
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class SubscriptionBase(SQLModel):
    plan: SubscriptionPlan = Field(default=SubscriptionPlan.TRIAL)
    status: SubscriptionStatus = Field(
        default=SubscriptionStatus.ACTIVE,
        index=True,
    )
    started_at: datetime | None = None
    ends_at: datetime | None = None
    billing_email: str | None = Field(default=None, max_length=255)


class Subscription(
    SubscriptionBase, TimestampMixin, SoftDeleteMixin, table=True
):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
