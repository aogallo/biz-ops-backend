# API Schema & Entity Development Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Layer Responsibilities](#layer-responsibilities)
3. [Creating a New API Endpoint - Step by Step](#creating-a-new-api-endpoint---step-by-step)
4. [CamelCase Conversion Flow](#camelcase-conversion-flow)
5. [Understanding model_dump()](#understanding-model_dump)
6. [Validation Error Handling](#validation-error-handling)
7. [Best Practices](#best-practices)
8. [Complete Example](#complete-example)

---

## Architecture Overview

Our backend uses a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│  API Layer (Routes)                                     │
│  - Receives camelCase JSON from frontend                │
│  - Uses Pydantic schemas for validation                 │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Service Layer                                          │
│  - Business logic                                       │
│  - Uses domain entities (snake_case)                    │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Repository Layer                                       │
│  - Database operations                                  │
│  - Uses SQLModel entities                               │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────┐
│  Database (PostgreSQL)                                  │
│  - Stores data in snake_case columns                    │
└─────────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### 1. **Schema Layer** (`app/schemas/`)
- **Purpose**: Define API contracts (request/response formats)
- **Naming**: Uses `CamelCaseSchema` base class
- **Convention**: Inherits from `CamelCaseSchema` for automatic camelCase conversion
- **Location**: `app/schemas/{resource}_schema.py`

**Types of Schemas:**
- `{Resource}Create`: For POST requests (creating new resources)
- `{Resource}Update`: For PUT/PATCH requests (updating resources)
- `{Resource}Response`: For API responses
- `{Resource}ListResponse`: For list endpoints

### 2. **Entity Layer** (`app/domain/entities/`)
- **Purpose**: Define business domain models
- **Naming**: Uses snake_case (Python convention)
- **Convention**: Inherits from `SQLModel`
- **Location**: `app/domain/entities/{resource}.py`

**Types of Entities:**
- `{Resource}Base`: Base fields shared across entities
- `{Resource}Create`: For creation operations (excludes auto-generated fields)
- `{Resource}`: Table model with all fields including id, timestamps, etc.

### 3. **Service Layer** (`app/services/`)
- **Purpose**: Business logic and validation
- **Responsibilities**:
  - Orchestrate repository operations
  - Apply business rules
  - Handle exceptions

### 4. **Repository Layer** (`app/infrastructure/repositories/`)
- **Purpose**: Database operations
- **Responsibilities**:
  - CRUD operations
  - Query building
  - Data persistence

---

## Creating a New API Endpoint - Step by Step

Let's create a complete example for a `Customer` resource.

### Step 1: Create the Entity (`app/domain/entities/customer.py`)

```python
from datetime import UTC, datetime
from sqlmodel import Field, SQLModel


class CustomerBase(SQLModel):
    """
    Base customer fields shared across operations
    """
    name: str
    email: str
    phone: str | None = None
    address: str | None = None


class CustomerCreate(CustomerBase):
    """
    Entity for creating a customer.
    Contains only fields that can be provided during creation.
    """
    pass


class Customer(CustomerBase, table=True):
    """
    Customer database table model.
    Includes auto-generated fields like id and timestamps.
    """
    id: int | None = Field(default=None, primary_key=True)

    created_by: str = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_by: str | None = Field(default=None, index=True)
    updated_at: datetime | None = Field(default=None)
```

**Key Points:**
- ✅ Use `{Resource}Base` for shared fields
- ✅ Use `{Resource}Create` for creation operations (no id, no timestamps)
- ✅ Use `{Resource}` for the full table model
- ✅ Use snake_case for all field names

---

### Step 2: Create Schemas (`app/schemas/customer_schema.py`)

```python
"""Customer API schemas for requests and responses."""

from datetime import datetime
from app.schemas.base import CamelCaseSchema


class CustomerCreate(CamelCaseSchema):
    """
    Schema for creating a new customer.
    API accepts camelCase, internally converts to snake_case.

    Example Request:
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phoneNumber": "555-0100",  // camelCase
        "address": "123 Main St"
    }
    """
    name: str
    email: str
    phone_number: str | None = None  # Defined as snake_case
    address: str | None = None


class CustomerUpdate(CamelCaseSchema):
    """
    Schema for updating a customer.
    All fields optional to allow partial updates.
    """
    name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    address: str | None = None


class CustomerResponse(CamelCaseSchema):
    """
    Schema for customer response.
    Automatically converts snake_case to camelCase in JSON.

    Example Response:
    {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phoneNumber": "555-0100",  // Converted to camelCase
        "address": "123 Main St",
        "createdBy": "user123",
        "createdAt": "2024-01-01T00:00:00Z"
    }
    """
    id: int
    name: str
    email: str
    phone_number: str | None
    address: str | None
    created_by: str
    created_at: datetime
    updated_by: str | None
    updated_at: datetime | None


class CustomerListResponse(CamelCaseSchema):
    """Schema for list of customers response."""
    customers: list[CustomerResponse]
    total: int
```

**Key Points:**
- ✅ Define fields in snake_case (e.g., `phone_number`)
- ✅ `CamelCaseSchema` automatically converts to camelCase in JSON (e.g., `phoneNumber`)
- ✅ Create separate schemas for Create, Update, Response, and List operations
- ✅ Add docstrings with example JSON for clarity

---

### Step 3: Create Repository (`app/infrastructure/repositories/customer_repository_impl.py`)

```python
from sqlmodel import select

from app.domain.entities.customer import Customer, CustomerCreate
from app.domain.entities.user import User
from app.domain.repositories.customer_repository import CustomerRepository
from app.infrastructure.database import get_current_session


class CustomerRepositoryImpl(CustomerRepository):
    """Implementation of Customer Repository"""

    def __init__(self, current_user: User) -> None:
        self.db = get_current_session()
        self.current_user = current_user

    def get_all(self) -> list[Customer]:
        """Get all customers"""
        statement = select(Customer)
        result: list[Customer] = list(self.db.exec(statement))
        return result

    def get_by_id(self, customer_id: int) -> Customer | None:
        """Get a customer by ID"""
        return self.db.get(Customer, customer_id)

    def create(self, customer: CustomerCreate) -> Customer:
        """Create a new customer"""
        # Convert entity to dict and add created_by
        customer_data = customer.model_dump()
        customer_data["created_by"] = self.current_user.auth_id

        # Create Customer instance
        new_customer = Customer(**customer_data)
        self.db.add(new_customer)
        self.db.commit()
        self.db.refresh(new_customer)
        return new_customer

    def get_by_email(self, email: str) -> Customer | None:
        """Get a customer by email"""
        statement = select(Customer).where(Customer.email == email)
        customer: Customer | None = self.db.exec(statement).one_or_none()
        return customer
```

**Key Points:**
- ✅ Accept `current_user` in constructor to inject `created_by`
- ✅ Use `model_dump()` to convert entity to dictionary
- ✅ Add audit fields (`created_by`, `updated_by`) at repository level
- ✅ Return the full `Customer` entity after creation

---

### Step 4: Create Service (`app/services/customer_service.py`)

```python
from fastapi import HTTPException, status

from app.domain.entities.customer import Customer, CustomerCreate
from app.domain.entities.user import User
from app.infrastructure.repositories.customer_repository_impl import (
    CustomerRepositoryImpl,
)


class CustomerService:
    """Service for managing customers."""

    def __init__(self, current_user: User):
        self.repository = CustomerRepositoryImpl(current_user)

    def create_customer(self, customer_request: CustomerCreate) -> Customer:
        """
        Create a new customer.
        Raises error if customer with same email exists.
        """
        # Check if customer with same email already exists
        existing_customer = self.repository.get_by_email(
            email=customer_request.email
        )

        if existing_customer is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Customer with this email already exists",
            )

        # Create the new customer
        return self.repository.create(customer=customer_request)

    def list_all_customers(self) -> list[Customer]:
        """Get all customers."""
        return self.repository.get_all()

    def get_customer_by_id(self, customer_id: int) -> Customer:
        """Get a customer by ID. Raises 404 if not found."""
        customer = self.repository.get_by_id(customer_id)

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found",
            )

        return customer
```

**Key Points:**
- ✅ Accept `current_user` and pass to repository
- ✅ Implement business logic (e.g., check for duplicates)
- ✅ Raise appropriate HTTPExceptions
- ✅ Use entity types (`CustomerCreate`, `Customer`) not schemas

---

### Step 5: Create Routes (`app/routes/customer_routes.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user, verify_token
from app.domain.entities.customer import CustomerCreate as CustomerCreateEntity
from app.infrastructure.database import get_session
from app.schemas.customer_schema import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
)
from app.services.customer_service import CustomerService

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
    dependencies=[
        Depends(verify_token),
        Depends(get_session),
    ],
)


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer: CustomerCreate, current_user=Depends(get_current_user)
):
    """
    Create a new customer.

    Accepts camelCase JSON and returns camelCase JSON.

    Example Request:
    ```json
    {
        "name": "John Doe",
        "email": "john@example.com",
        "phoneNumber": "555-0100"
    }
    ```
    """
    try:
        service = CustomerService(current_user)
        # Convert schema to entity
        customer_entity = CustomerCreateEntity(**customer.model_dump())
        created_customer = service.create_customer(customer_entity)
        return CustomerResponse.model_validate(created_customer)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("", response_model=CustomerListResponse)
def list_customers(current_user=Depends(get_current_user)):
    """
    Get all customers.

    Returns a list of all customers in the system.
    """
    service = CustomerService(current_user)
    customers = service.list_all_customers()
    return CustomerListResponse(
        customers=[CustomerResponse.model_validate(c) for c in customers],
        total=len(customers),
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int, current_user=Depends(get_current_user)
):
    """Get a specific customer by ID."""
    service = CustomerService(current_user)
    customer = service.get_customer_by_id(customer_id)
    return CustomerResponse.model_validate(customer)
```

**Key Points:**
- ✅ Import schema as `CustomerCreate` (for API validation)
- ✅ Import entity as `CustomerCreateEntity` (aliased to avoid naming conflict)
- ✅ Use `customer.model_dump()` to convert schema → dict → entity
- ✅ Set `response_model` to ensure camelCase response
- ✅ Use `CustomerResponse.model_validate()` to convert entity → schema
- ✅ Add proper error handling with try/except

---

## CamelCase Conversion Flow

### Request Flow (Frontend → Backend)

```
Frontend sends:                    Backend receives:
{                                  customer: CustomerCreate(
  "name": "John Doe",               name="John Doe",
  "phoneNumber": "555-0100"   →     phone_number="555-0100"
}                                  )
     ↓                                   ↓
  camelCase                          snake_case
```

**How it works:**
1. FastAPI receives JSON with camelCase keys: `{"phoneNumber": "555-0100"}`
2. `CamelCaseSchema` automatically maps camelCase → snake_case
3. Pydantic creates `CustomerCreate` instance with snake_case attributes
4. Validation errors show camelCase field names in error messages

### Response Flow (Backend → Frontend)

```
Backend returns:                   Frontend receives:
customer: Customer(                {
  name="John Doe",                   "name": "John Doe",
  phone_number="555-0100"     →      "phoneNumber": "555-0100"
)                                  }
     ↓                                   ↓
  snake_case                          camelCase
```

**How it works:**
1. Repository returns `Customer` entity (SQLModel) with snake_case
2. Route converts to `CustomerResponse` using `model_validate()`
3. `CamelCaseSchema` automatically converts snake_case → camelCase
4. FastAPI serializes to JSON with camelCase keys

---

## Understanding model_dump()

`model_dump()` is a Pydantic v2 method that converts a model instance into a Python dictionary.

### Basic Usage

```python
# Create a schema instance
customer_schema = CustomerCreate(
    name="John Doe",
    email="john@example.com",
    phone_number="555-0100"
)

# Convert to dictionary
customer_dict = customer_schema.model_dump()
# Result: {
#     'name': 'John Doe',
#     'email': 'john@example.com',
#     'phone_number': '555-0100'
# }
```

### Why We Use It

#### 1. **Converting Schema → Entity** (in Routes)

```python
# customer is a Pydantic schema (CustomerCreate from app.schemas)
customer_entity = CustomerCreateEntity(**customer.model_dump())
```

**What happens:**
1. `customer` is a schema with camelCase conversion features
2. `customer.model_dump()` extracts the data as a dictionary
3. `**customer.model_dump()` unpacks the dictionary as keyword arguments
4. `CustomerCreateEntity(...)` creates the SQLModel entity

**Why not just pass the schema directly?**
- Schemas and entities are different types
- Entities don't have camelCase conversion logic
- Clear separation between API layer and domain layer

#### 2. **Adding Extra Fields** (in Repository)

```python
# Convert entity to dict so we can modify it
customer_data = customer.model_dump()
customer_data["created_by"] = self.current_user.auth_id

# Create final database model
new_customer = Customer(**customer_data)
```

**What happens:**
1. Convert entity to dictionary: `{'name': '...', 'email': '...'}`
2. Add fields not in the request: `created_by`, `updated_by`, etc.
3. Create the full `Customer` model with all required fields

#### 3. **Converting Entity → Schema** (in Routes)

```python
created_customer = service.create_customer(customer_entity)
return CustomerResponse.model_validate(created_customer)
```

**What `model_validate()` does:**
- Converts a SQLModel entity to a Pydantic schema
- Validates all fields
- Applies camelCase conversion for response

---

## Validation Error Handling

### ✅ Good: Schema-Level Validation (What We Want)

When using schemas correctly, FastAPI validates at the API layer:

```json
POST /customers
{
  "name": "John Doe"
  // Missing email field
}

Response (400 Bad Request):
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {"name": "John Doe"}
    }
  ]
}
```

**Benefits:**
- ✅ Clear, user-friendly error messages
- ✅ Shows camelCase field names
- ✅ FastAPI handles it automatically
- ✅ Error occurs before business logic runs

### ❌ Bad: Entity-Level Validation (What We Avoid)

If you pass schemas directly to repositories without conversion:

```python
# DON'T DO THIS
def create(self, customer: CustomerCreate):  # Schema type!
    new_customer = Customer.model_validate(customer)  # ❌ Wrong!
```

This causes cryptic SQLModel validation errors:

```
ValidationError: 1 validation error for Customer
created_by
  Field required [type=missing, input_value=CustomerCreate(...), input_type=CustomerCreate]
```

**Problems:**
- ❌ Confusing error message
- ❌ Mentions internal fields (`created_by`)
- ❌ Shows entity type instead of request data
- ❌ Not user-friendly

---

## Best Practices

### ✅ DO

1. **Always use two separate types:**
   - Schema (`app.schemas.{resource}_schema.py`) for API layer
   - Entity (`app.domain.entities/{resource}.py`) for business layer

2. **Use descriptive variable names:**
   ```python
   # Good
   customer_entity = CustomerCreateEntity(**customer.model_dump())

   # Avoid
   c = CustomerCreateEntity(**customer.model_dump())
   ```

3. **Add docstrings with examples:**
   ```python
   class CustomerCreate(CamelCaseSchema):
       """
       Schema for creating a new customer.

       Example Request:
       {
           "name": "John Doe",
           "email": "john@example.com"
       }
       """
   ```

4. **Use type hints everywhere:**
   ```python
   def create_customer(self, customer_request: CustomerCreate) -> Customer:
       """Create a new customer."""
   ```

5. **Set response_model on all endpoints:**
   ```python
   @router.post("", response_model=CustomerResponse)
   ```

6. **Handle exceptions properly:**
   ```python
   try:
       service.create_customer(customer_entity)
   except ValueError as e:
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail=str(e),
       ) from e
   ```

### ❌ DON'T

1. **Don't mix schemas and entities:**
   ```python
   # Bad
   def create(self, customer: CustomerCreate):  # Schema in repository!
       new_customer = Customer.model_validate(customer)
   ```

2. **Don't skip model_dump():**
   ```python
   # Bad
   customer_entity = CustomerCreateEntity(customer)  # ❌ Wrong type!

   # Good
   customer_entity = CustomerCreateEntity(**customer.model_dump())
   ```

3. **Don't forget to validate responses:**
   ```python
   # Bad
   return created_customer  # Raw entity

   # Good
   return CustomerResponse.model_validate(created_customer)
   ```

4. **Don't define fields in camelCase:**
   ```python
   # Bad
   class CustomerCreate(CamelCaseSchema):
       phoneNumber: str  # ❌ Should be snake_case

   # Good
   class CustomerCreate(CamelCaseSchema):
       phone_number: str  # ✅ CamelCaseSchema converts it
   ```

---

## Complete Example

Here's the complete data flow for creating a customer:

### 1. Frontend sends request:
```javascript
POST /api/customers
{
  "name": "John Doe",
  "email": "john@example.com",
  "phoneNumber": "555-0100"  // camelCase
}
```

### 2. Route receives and validates:
```python
def create_customer(customer: CustomerCreate, current_user=...):
    # customer.phone_number = "555-0100"  (converted to snake_case)

    # Convert schema to entity
    customer_entity = CustomerCreateEntity(**customer.model_dump())
    # customer_entity = CustomerCreateEntity(
    #     name="John Doe",
    #     email="john@example.com",
    #     phone_number="555-0100"
    # )
```

### 3. Service applies business logic:
```python
def create_customer(self, customer_request: CustomerCreate) -> Customer:
    # Check if email already exists
    existing = self.repository.get_by_email(customer_request.email)
    if existing:
        raise HTTPException(409, "Email already exists")

    # Create customer
    return self.repository.create(customer_request)
```

### 4. Repository saves to database:
```python
def create(self, customer: CustomerCreate) -> Customer:
    # Convert to dict and add audit fields
    customer_data = customer.model_dump()
    # customer_data = {
    #     'name': 'John Doe',
    #     'email': 'john@example.com',
    #     'phone_number': '555-0100'
    # }

    customer_data["created_by"] = self.current_user.auth_id
    # customer_data = {
    #     'name': 'John Doe',
    #     'email': 'john@example.com',
    #     'phone_number': '555-0100',
    #     'created_by': 'user_123'
    # }

    new_customer = Customer(**customer_data)
    # Save to database...
    return new_customer
```

### 5. Route returns response:
```python
    created_customer = service.create_customer(customer_entity)
    return CustomerResponse.model_validate(created_customer)
    # Converts snake_case → camelCase for response
```

### 6. Frontend receives response:
```javascript
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phoneNumber": "555-0100",  // Back to camelCase
  "address": null,
  "createdBy": "user_123",
  "createdAt": "2024-01-01T00:00:00Z",
  "updatedBy": null,
  "updatedAt": null
}
```

---

## Summary Checklist

When creating a new API endpoint, follow these steps:

- [ ] Create entity in `app/domain/entities/{resource}.py`
  - [ ] `{Resource}Base` - shared fields
  - [ ] `{Resource}Create` - for creation
  - [ ] `{Resource}` - full table model

- [ ] Create schemas in `app/schemas/{resource}_schema.py`
  - [ ] `{Resource}Create` - inherits `CamelCaseSchema`
  - [ ] `{Resource}Update` - inherits `CamelCaseSchema`
  - [ ] `{Resource}Response` - inherits `CamelCaseSchema`
  - [ ] Add docstrings with JSON examples

- [ ] Create repository in `app/infrastructure/repositories/{resource}_repository_impl.py`
  - [ ] Accept `current_user` in `__init__`
  - [ ] Use `model_dump()` to convert entities
  - [ ] Add audit fields (`created_by`, `updated_by`)

- [ ] Create service in `app/services/{resource}_service.py`
  - [ ] Accept `current_user` in `__init__`
  - [ ] Implement business logic
  - [ ] Raise appropriate HTTPExceptions

- [ ] Create routes in `app/routes/{resource}_routes.py`
  - [ ] Import schema and entity (alias entity to avoid conflicts)
  - [ ] Use `model_dump()` to convert schema → entity
  - [ ] Set `response_model` for all endpoints
  - [ ] Use `model_validate()` to convert entity → schema
  - [ ] Add error handling

---

**Questions?** Review the existing `Product` and `Account` implementations for working examples.
