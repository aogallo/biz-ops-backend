# Quick Reference - API Development

## 🎯 TL;DR

When creating a new API endpoint that accepts camelCase JSON:

1. **Define fields in snake_case** in schemas
2. **Use `CamelCaseSchema`** as base class for schemas
3. **Always separate** Schema (API layer) from Entity (domain layer)
4. **Use `model_dump()`** to convert between types
5. **Set `response_model`** on all endpoints

---

## 🚀 Quick Start Checklist

```bash
# 1. Create entity file
touch app/domain/entities/resource.py

# 2. Create schema file
touch app/schemas/resource_schema.py

# 3. Create repository file
touch app/infrastructure/repositories/resource_repository_impl.py

# 4. Create service file
touch app/services/resource_service.py

# 5. Create routes file
touch app/routes/resource_routes.py
```

---

## 📋 File Templates

### Entity Template (`app/domain/entities/resource.py`)

```python
from datetime import UTC, datetime
from sqlmodel import Field, SQLModel


class ResourceBase(SQLModel):
    """Base resource fields"""
    field_one: str
    field_two: int
    optional_field: str | None = None


class ResourceCreate(ResourceBase):
    """Create resource"""
    pass


class Resource(ResourceBase, table=True):
    """Resource table"""
    id: int | None = Field(default=None, primary_key=True)
    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)
```

### Schema Template (`app/schemas/resource_schema.py`)

```python
from datetime import datetime
from app.schemas.base import CamelCaseSchema


class ResourceCreate(CamelCaseSchema):
    """Schema for creating resource"""
    field_one: str
    field_two: int
    optional_field: str | None = None


class ResourceResponse(CamelCaseSchema):
    """Schema for resource response"""
    id: int
    field_one: str
    field_two: int
    optional_field: str | None
    created_by: str
    created_at: datetime
    updated_by: str | None
    updated_at: datetime | None
```

### Repository Template (`app/infrastructure/repositories/resource_repository_impl.py`)

```python
from sqlmodel import select
from app.domain.entities.resource import Resource, ResourceCreate
from app.domain.entities.user import User
from app.infrastructure.database import get_current_session


class ResourceRepositoryImpl:
    """Repository for resource operations"""

    def __init__(self, current_user: User) -> None:
        self.db = get_current_session()
        self.current_user = current_user

    def create(self, resource: ResourceCreate) -> Resource:
        """Create a new resource"""
        resource_data = resource.model_dump()
        resource_data["created_by"] = self.current_user.auth_id

        new_resource = Resource(**resource_data)
        self.db.add(new_resource)
        self.db.commit()
        self.db.refresh(new_resource)
        return new_resource

    def get_all(self) -> list[Resource]:
        """Get all resources"""
        statement = select(Resource)
        return list(self.db.exec(statement))
```

### Service Template (`app/services/resource_service.py`)

```python
from fastapi import HTTPException, status
from app.domain.entities.resource import Resource, ResourceCreate
from app.domain.entities.user import User
from app.infrastructure.repositories.resource_repository_impl import (
    ResourceRepositoryImpl,
)


class ResourceService:
    """Service for resource operations"""

    def __init__(self, current_user: User):
        self.repository = ResourceRepositoryImpl(current_user)

    def create_resource(self, resource_request: ResourceCreate) -> Resource:
        """Create a new resource"""
        # Add business logic here (validation, checks, etc.)
        return self.repository.create(resource_request)

    def list_all_resources(self) -> list[Resource]:
        """Get all resources"""
        return self.repository.get_all()
```

### Routes Template (`app/routes/resource_routes.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.dependencies import get_current_user, verify_token
from app.domain.entities.resource import ResourceCreate as ResourceCreateEntity
from app.infrastructure.database import get_session
from app.schemas.resource_schema import ResourceCreate, ResourceResponse
from app.services.resource_service import ResourceService

router = APIRouter(
    prefix="/resources",
    tags=["Resources"],
    dependencies=[Depends(verify_token), Depends(get_session)],
)


@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(
    resource: ResourceCreate, current_user=Depends(get_current_user)
):
    """Create a new resource"""
    try:
        service = ResourceService(current_user)
        resource_entity = ResourceCreateEntity(**resource.model_dump())
        created_resource = service.create_resource(resource_entity)
        return ResourceResponse.model_validate(created_resource)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("", response_model=list[ResourceResponse])
def list_resources(current_user=Depends(get_current_user)):
    """Get all resources"""
    service = ResourceService(current_user)
    resources = service.list_all_resources()
    return [ResourceResponse.model_validate(r) for r in resources]
```

---

## 🔑 Key Concepts

### CamelCase Conversion

```python
# ✅ CORRECT: Define fields in snake_case
class CustomerCreate(CamelCaseSchema):
    phone_number: str  # API accepts "phoneNumber"
    email_address: str  # API accepts "emailAddress"

# ❌ WRONG: Don't use camelCase in schema
class CustomerCreate(CamelCaseSchema):
    phoneNumber: str  # Wrong!
    emailAddress: str  # Wrong!
```

### model_dump() Usage

```python
# Convert schema to dictionary for entity creation
schema_instance = ResourceCreate(field_one="value", field_two=123)
data_dict = schema_instance.model_dump()
# {'field_one': 'value', 'field_two': 123}

# Create entity from schema
entity = ResourceCreateEntity(**schema_instance.model_dump())
```

### model_validate() Usage

```python
# Convert entity to schema for response
entity = Resource(id=1, field_one="value", field_two=123, ...)
response = ResourceResponse.model_validate(entity)
# Converts snake_case → camelCase in JSON response
```

---

## 🎨 Common Patterns

### Pattern 1: Create Endpoint

```python
@router.post("", response_model=ResourceResponse, status_code=201)
def create_resource(
    resource: ResourceCreate,  # Schema (API layer)
    current_user=Depends(get_current_user)
):
    service = ResourceService(current_user)
    # Convert: Schema → Entity
    entity = ResourceCreateEntity(**resource.model_dump())
    created = service.create_resource(entity)
    # Convert: Entity → Schema
    return ResourceResponse.model_validate(created)
```

### Pattern 2: List Endpoint

```python
@router.get("", response_model=list[ResourceResponse])
def list_resources(current_user=Depends(get_current_user)):
    service = ResourceService(current_user)
    resources = service.list_all_resources()
    # Convert each entity to response schema
    return [ResourceResponse.model_validate(r) for r in resources]
```

### Pattern 3: Get By ID Endpoint

```python
@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    current_user=Depends(get_current_user)
):
    service = ResourceService(current_user)
    resource = service.get_resource_by_id(resource_id)
    return ResourceResponse.model_validate(resource)
```

### Pattern 4: Update Endpoint

```python
@router.patch("/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    resource: ResourceUpdate,  # Schema
    current_user=Depends(get_current_user)
):
    service = ResourceService(current_user)
    # Convert: Schema → Entity
    entity = ResourceUpdateEntity(**resource.model_dump(exclude_unset=True))
    updated = service.update_resource(resource_id, entity)
    # Convert: Entity → Schema
    return ResourceResponse.model_validate(updated)
```

---

## ⚠️ Common Mistakes

### ❌ Mistake 1: Using camelCase in schema definitions

```python
# WRONG
class ResourceCreate(CamelCaseSchema):
    phoneNumber: str  # ❌

# CORRECT
class ResourceCreate(CamelCaseSchema):
    phone_number: str  # ✅
```

### ❌ Mistake 2: Passing schema to repository

```python
# WRONG
def create(self, resource: ResourceCreate):  # Schema type!
    new_resource = Resource.model_validate(resource)  # ❌

# CORRECT
def create(self, resource: ResourceCreate):  # Entity type!
    resource_data = resource.model_dump()
    new_resource = Resource(**resource_data)  # ✅
```

### ❌ Mistake 3: Forgetting model_dump()

```python
# WRONG
entity = ResourceCreateEntity(schema_instance)  # ❌

# CORRECT
entity = ResourceCreateEntity(**schema_instance.model_dump())  # ✅
```

### ❌ Mistake 4: Not setting response_model

```python
# WRONG - Returns snake_case
@router.post("")
def create_resource(...):
    return created_resource  # ❌

# CORRECT - Returns camelCase
@router.post("", response_model=ResourceResponse)
def create_resource(...):
    return ResourceResponse.model_validate(created_resource)  # ✅
```

### ❌ Mistake 5: Mixing entity and schema layers

```python
# WRONG - Service using schema type
def create_resource(self, resource: ResourceCreate):  # Schema in service!
    return self.repository.create(resource)  # ❌

# CORRECT - Service using entity type
def create_resource(self, resource: ResourceCreate) -> Resource:  # Entity type!
    return self.repository.create(resource)  # ✅
```

---

## 📝 Type Hints Cheatsheet

```python
# Imports
from app.schemas.resource_schema import ResourceCreate, ResourceResponse
from app.domain.entities.resource import ResourceCreate as ResourceCreateEntity
from app.domain.entities.resource import Resource

# Route
def create_resource(
    resource: ResourceCreate,  # Schema type for API
    current_user=Depends(get_current_user)
):
    entity = ResourceCreateEntity(**resource.model_dump())  # Entity type
    ...

# Service
def create_resource(
    self,
    resource_request: ResourceCreate  # Entity type, not schema!
) -> Resource:  # Returns entity
    ...

# Repository
def create(
    self,
    resource: ResourceCreate  # Entity type
) -> Resource:  # Returns entity
    ...
```

---

## 🧪 Testing Example

```python
def test_create_resource(client, auth_headers):
    """Test creating a resource with camelCase"""
    # Request with camelCase
    response = client.post(
        "/resources",
        headers=auth_headers,
        json={
            "fieldOne": "value",  # camelCase
            "fieldTwo": 123,
            "optionalField": "optional"
        }
    )

    assert response.status_code == 201
    data = response.json()

    # Response should be in camelCase
    assert "fieldOne" in data
    assert "fieldTwo" in data
    assert "createdAt" in data  # Not created_at
    assert "createdBy" in data  # Not created_by
```

---

## 📚 More Information

For detailed explanations, complete examples, and architectural decisions, see:

- **[Complete Guide](API_SCHEMA_ENTITY_GUIDE.md)** - Comprehensive developer guide

---

## 💡 Tips

1. **Always use snake_case** in Python code (fields, variables, functions)
2. **CamelCaseSchema handles conversion** automatically
3. **Use type hints** everywhere for better IDE support
4. **Check existing code** (Product, Account) for working examples
5. **Run linters** before committing: `ruff check app/ && black app/`

---

**Need help?** Check the [complete guide](API_SCHEMA_ENTITY_GUIDE.md) or review existing implementations.
