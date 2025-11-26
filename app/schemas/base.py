"""Base schema configuration for camelCase API responses."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseSchema(BaseModel):
    """
    Base schema that converts snake_case field names to camelCase in JSON.

    Configuration:
    - alias_generator: Automatically converts field names to camelCase
    - populate_by_name: Accept both snake_case and camelCase in requests
    - from_attributes: Load data from SQLModel entities
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
