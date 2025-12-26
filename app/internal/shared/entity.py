from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps"""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: datetime | None = Field(default=None)


class SoftDeleteMixin(SQLModel):
    """Mixin for soft delete functionality"""

    is_deleted: bool = Field(default=False, nullable=False)
    deleted_at: datetime | None = None
