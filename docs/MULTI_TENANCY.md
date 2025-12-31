# Multi-Tenancy Architecture

This document describes the multi-tenancy implementation in the Business Operations Backend API.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Data Scoping](#data-scoping)
- [Access Control](#access-control)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Migration Guide](#migration-guide)

## Overview

The application implements a **hierarchical multi-tenancy** model with three levels:

```
Organization (Accounting Firm)
    ├── Company 1 (Client)
    │   ├── Invoices
    │   ├── Journal Entries
    │   └── Reports
    ├── Company 2 (Client)
    │   ├── Invoices
    │   └── ...
    └── Shared Resources
        ├── Business Partners (Vendors/Customers)
        ├── Accounts (Chart of Accounts)
        ├── Products
        └── Categories
```

### Key Concepts

- **Organization**: Represents an accounting firm or business group
- **Company**: Represents individual clients managed by the organization
- **Organization-scoped**: Data shared across all companies in an organization
- **Company-scoped**: Data isolated to a specific company
- **User**: Belongs to one organization, can access multiple companies

## Architecture

### Tenant Hierarchy

```
┌─────────────────────────────────────────────┐
│          Organization (Tenant)              │
│  Example: "ABC Accounting Firm"             │
│                                             │
│  ┌─────────────┐  ┌─────────────┐         │
│  │ Company 1   │  │ Company 2   │  ...    │
│  │ (Client A)  │  │ (Client B)  │         │
│  └─────────────┘  └─────────────┘         │
│                                             │
│  Shared Across Companies:                  │
│  • Business Partners (Los 3 pollos hermanos)│
│  • Chart of Accounts (1101, 4101, etc.)    │
│  • Products                                 │
│  • Categories                               │
└─────────────────────────────────────────────┘
```

### Database Schema

All primary keys use **UUID** for security and distributed system compatibility.

#### Core Entities

**Organization**
```python
class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str  # "ABC Accounting Firm"
    slug: str = Field(unique=True, index=True)

    # Relationships
    companies: list["Company"]
    users: list["User"]
    business_partners: list["BusinessPartner"]
    accounts: list["Account"]
```

**User**
```python
class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    auth0_user_id: str = Field(unique=True, index=True)
    organization_id: UUID = Field(foreign_key="organizations.id")

    # Access to multiple companies via UserCompanyAccess
    company_accesses: list["UserCompanyAccess"]
```

**UserCompanyAccess** (Junction Table)
```python
class UserCompanyAccess(SQLModel, table=True):
    __tablename__ = "user_company_access"

    user_id: UUID = Field(foreign_key="users.id", primary_key=True)
    company_id: UUID = Field(foreign_key="companies.id", primary_key=True)
    role: str = "user"  # "owner", "admin", "accountant", "viewer"
```

**Company**
```python
class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id")
    name: str
    nit: str
```

## Data Scoping

### Organization-Scoped Entities

These entities are **shared across all companies** within an organization:

**BusinessPartner** (Vendors & Customers)
```python
class BusinessPartner(SQLModel, table=True):
    __tablename__ = "business_partner"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id")
    name: str
    nit: str
    is_vendor: bool
    is_customer: bool
```

**Why organization-scoped?**
- Same vendor can sell to multiple clients (e.g., "Los 3 pollos hermanos" supplies to Company A, B, and C)
- Avoids duplicate vendor/customer entries
- Simplifies reporting across companies

**Account** (Chart of Accounts)
```python
class Account(SQLModel, table=True):
    __tablename__ = "accounts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organizations.id")
    account_number: str  # "1101"
    name: str  # "Cash"
    type: str  # "asset", "liability", etc.
```

**Why organization-scoped?**
- Accounting firms use standardized charts of accounts
- Same account structure across all clients
- Easier to maintain and update

**Product** and **Category**
- Organization-scoped for similar reasons
- Shared product catalog across companies

### Company-Scoped Entities

These entities are **isolated to a specific company**:

**Invoice**
```python
class Invoice(SQLModel, table=True):
    __tablename__ = "invoice"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_id: UUID = Field(foreign_key="companies.id")
    business_partner_id: UUID = Field(foreign_key="business_partner.id")
    invoice_type: str  # "income" or "expense"
    total_amount: float
```

**JournalEntry**
```python
class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entry"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    company_id: UUID = Field(foreign_key="companies.id")
    invoice_id: UUID = Field(foreign_key="invoice.id")
    account_id: UUID = Field(foreign_key="accounts.id")  # Org-scoped
    debit: float
    credit: float
```

**Why company-scoped?**
- Financial data must be isolated per client
- Regulatory compliance requirements
- Data privacy and security

## Access Control

### Authentication Flow

```
1. User logs in via Auth0 → JWT token issued
2. Frontend sends JWT in Authorization header
3. Backend verifies token → extracts user info
4. User entity fetched from database
5. Access control checks applied
```

### Middleware Dependencies

**get_current_user**
```python
def get_current_user(
    token: str = Depends(get_credentials),
    session: Session = Depends(get_session),
) -> User:
    """Fetch User entity from database using Auth0 token."""
    auth0_user_id = verify_token(token)["sub"]
    user = session.query(User).filter_by(auth0_user_id=auth0_user_id).first()

    if not user:
        # Auto-create user on first login
        user = User(auth0_user_id=auth0_user_id, ...)

    return user
```

**verify_company_access**
```python
def verify_company_access(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Verify user has access to the requested company."""
    access = session.query(UserCompanyAccess).filter_by(
        user_id=current_user.id,
        company_id=company_id
    ).first()

    if not access:
        raise AuthorizationError("Access denied")
```

**verify_organization_access**
```python
def verify_organization_access(
    organization_id: UUID,
    current_user: User = Depends(get_current_user),
) -> None:
    """Verify user belongs to the organization."""
    if current_user.organization_id != organization_id:
        raise AuthorizationError("Access denied")
```

### Route Protection

**Company-scoped routes:**
```python
@router.get("/companies/{company_id}/invoices")
def list_invoices(
    company_id: UUID,
    current_user: User = Depends(get_current_user),
    _: None = Depends(verify_company_access),  # Access control
    session: Session = Depends(get_session),
):
    service = InvoiceService(session, current_user, company_id)
    return service.list_all_invoices()
```

**Organization-scoped routes:**
```python
@router.get("/customers")
def list_customers(
    current_user: User = Depends(get_current_user),
    # No explicit org check - extracted from current_user
    session: Session = Depends(get_session),
):
    service = BusinessPartnerService(session, current_user)
    # Service uses current_user.organization_id
    return service.list_all_customers()
```

### Repository-Level Filtering

All queries are automatically scoped:

```python
class InvoiceRepositoryImpl:
    def __init__(self, session: Session, current_user: User, company_id: UUID):
        self.db = session
        self.company_id = company_id  # Injected from route

    def get_all(self) -> list[Invoice]:
        # Automatically scoped to company
        return self.db.query(Invoice).filter_by(
            company_id=self.company_id
        ).all()
```

```python
class BusinessPartnerRepositoryImpl:
    def __init__(self, session: Session, current_user: User, organization_id: UUID):
        self.db = session
        self.organization_id = organization_id

    def get_all(self) -> list[BusinessPartner]:
        # Automatically scoped to organization
        return self.db.query(BusinessPartner).filter_by(
            organization_id=self.organization_id
        ).all()
```

## Usage Examples

### Creating an Invoice

**Frontend Request:**
```http
POST /api/v1/companies/{company_id}/invoices
Authorization: Bearer <JWT_TOKEN>

{
  "businessPartnerId": "uuid-of-vendor",
  "invoiceType": "expense",
  "totalAmount": 1000.00
}
```

**Backend Flow:**
```python
# 1. Route extracts company_id from URL path
# 2. verify_company_access checks UserCompanyAccess
# 3. Service created with company_id
service = InvoiceService(session, current_user, company_id)

# 4. Service extracts organization_id from company
company = session.get(Company, company_id)
organization_id = company.organization_id

# 5. Service initializes repositories with correct scoping
self.invoice_repo = InvoiceRepositoryImpl(session, user, company_id)  # Company-scoped
self.bp_repo = BusinessPartnerRepositoryImpl(session, user, organization_id)  # Org-scoped

# 6. Create invoice (automatically scoped to company)
invoice = self.invoice_repo.create(invoice_data)
```

### Listing Business Partners

**Frontend Request:**
```http
GET /api/v1/customers
Authorization: Bearer <JWT_TOKEN>
```

**Backend Flow:**
```python
# 1. get_current_user fetches User entity
# 2. Service extracts organization_id from user
service = BusinessPartnerService(session, current_user)

# 3. Repository automatically filters by organization_id
self.repository = BusinessPartnerRepositoryImpl(
    session,
    current_user,
    current_user.organization_id  # From user
)

# 4. Returns only business partners in user's organization
return service.list_all_customers()
```

### SAT Invoice Upload

**How company_id Works:**

```python
@router.post("/companies/{company_id}/invoices/upload")
async def upload_file(
    company_id: UUID,  # The tenant company (from URL)
    file: UploadFile,
    invoice_type: str,  # "incomes" or "expenses"
    ...
):
    service = InvoiceService(session, current_user, company_id)

    # Parse SAT Excel file
    for row in rows:
        # Extract business partner from SAT data
        if invoice_type == "expenses":
            partner_nit = row.emisor_nit  # Vendor
        else:
            partner_nit = row.receptor_nit  # Customer

        # Get or create business partner (organization-scoped)
        partner = service.get_or_create_business_partner(
            nit=partner_nit,
            name=partner_name,
            is_vendor=(invoice_type == "expenses")
        )

        # Create invoice (company-scoped)
        invoice = service.create_invoice(
            company_id=company_id,  # Tenant from URL
            business_partner_id=partner.id,  # Org-scoped partner
            ...
        )
```

## Best Practices

### 1. Always Pass company_id in URL Path for Company-Scoped Resources

```python
# ✅ Correct
@router.get("/companies/{company_id}/invoices")

# ❌ Wrong
@router.get("/invoices?company_id={company_id}")
```

### 2. Service Layer Extracts organization_id from Company

```python
class InvoiceService:
    def __init__(self, session: Session, current_user: User, company_id: UUID):
        # Get company to extract organization_id
        company = session.get(Company, company_id)
        if not company:
            raise NotFoundError("Company", company_id)

        self.organization_id = company.organization_id

        # Company-scoped repos
        self.invoice_repo = InvoiceRepositoryImpl(session, user, company_id)

        # Organization-scoped repos
        self.bp_repo = BusinessPartnerRepositoryImpl(session, user, self.organization_id)
```

### 3. Repository Constructor Enforces Scoping

```python
# Company-scoped
class InvoiceRepositoryImpl:
    def __init__(self, session: Session, current_user: User, company_id: UUID):
        self.company_id = company_id  # Required parameter

# Organization-scoped
class BusinessPartnerRepositoryImpl:
    def __init__(self, session: Session, current_user: User, organization_id: UUID):
        self.organization_id = organization_id  # Required parameter
```

### 4. Never Trust Client-Provided Tenant IDs

```python
# ✅ Correct - company_id from URL path, verified by middleware
def create_invoice(company_id: UUID, ...):
    ...

# ❌ Wrong - company_id from request body (can be manipulated)
def create_invoice(data: InvoiceCreate):
    company_id = data.company_id  # SECURITY RISK!
```

### 5. Use Explicit Table Names

```python
class BusinessPartner(SQLModel, table=True):
    __tablename__ = "business_partner"  # Explicit

    # Not: __tablename__ = "businesspartner" (auto-generated)
```

## Migration Guide

### Migrating Existing Data

If you have an existing single-company database:

#### Step 1: Create Organization

```sql
INSERT INTO organizations (id, name, slug)
VALUES (gen_random_uuid(), 'Default Organization', 'default-org');
```

#### Step 2: Update Company with organization_id

```sql
UPDATE companies
SET organization_id = (SELECT id FROM organizations WHERE slug = 'default-org');
```

#### Step 3: Migrate Business Partners

```sql
-- Add organization_id column
ALTER TABLE business_partner
ADD COLUMN organization_id UUID;

-- Backfill from company
UPDATE business_partner bp
SET organization_id = (
    SELECT c.organization_id
    FROM companies c
    LIMIT 1
);

-- Make non-nullable
ALTER TABLE business_partner
ALTER COLUMN organization_id SET NOT NULL;

-- Add foreign key
ALTER TABLE business_partner
ADD CONSTRAINT fk_business_partner_organization
FOREIGN KEY (organization_id) REFERENCES organizations(id);
```

#### Step 4: Migrate Accounts, Products, Categories

Same process as Step 3 for each entity.

#### Step 5: Create User Company Access

```sql
-- Grant all users access to all companies (can refine later)
INSERT INTO user_company_access (user_id, company_id, role)
SELECT u.id, c.id, 'admin'
FROM users u
CROSS JOIN companies c
WHERE u.organization_id = c.organization_id;
```

### Converting from Int IDs to UUID

See [Alembic Migration Guide](./ALEMBIC_MIGRATIONS.md#migration-from-existing-database) for detailed instructions.

## Troubleshooting

### Common Issues

**Issue: "User does not have access to company"**
- Cause: Missing UserCompanyAccess record
- Solution: Create access record via admin endpoint or database

**Issue: "Organization-scoped entity not found"**
- Cause: Entity belongs to different organization
- Solution: Verify user's organization_id matches entity's organization_id

**Issue: "Can't create business partner"**
- Cause: Missing organization_id or user not in organization
- Solution: Ensure user belongs to an organization

### Testing Multi-Tenancy

```python
# Create test organization
org = Organization(name="Test Org", slug="test-org")

# Create test companies
company1 = Company(name="Company A", organization_id=org.id)
company2 = Company(name="Company B", organization_id=org.id)

# Create test user
user = User(organization_id=org.id, ...)

# Grant access to specific companies
access1 = UserCompanyAccess(user_id=user.id, company_id=company1.id)

# Test isolation
# User should only see data for company1, not company2
```

## Security Considerations

1. **Always verify company access** via middleware
2. **Never expose organization_id to frontend** (derive from user)
3. **Use UUID for all primary keys** (prevents enumeration attacks)
4. **Audit trail**: All creates/updates store `created_by`/`updated_by`
5. **Row-level filtering** enforced at repository layer

## Additional Resources

- [Alembic Migration Guide](./ALEMBIC_MIGRATIONS.md)
- [API Schema Entity Guide](./API_SCHEMA_ENTITY_GUIDE.md)
- [Auth0 Documentation](https://auth0.com/docs)
