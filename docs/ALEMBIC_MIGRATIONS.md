# Alembic Database Migration Guide

This guide explains how to use Alembic for database migrations in the Business Operations Backend.

## Overview

Alembic is a database migration tool for SQLAlchemy. We use it to manage schema changes as the application evolves. Currently, the project is in local development, so migrations are **not required yet**. When you're ready to deploy to staging/production, follow this guide.

## Prerequisites

- PostgreSQL database running
- `DATABASE_URI` environment variable configured
- All dependencies installed: `uv pip install -r requirements.txt`

## Initial Setup (Already Configured)

The Alembic configuration is already set up:

```
alembic/
├── env.py                 # Environment configuration
├── script.py.mako         # Migration template
└── versions/              # Migration scripts go here

alembic.ini                # Alembic configuration file
```

## Creating Migrations

### 1. Verify Current Database State

Before creating migrations, ensure your database schema matches your SQLModel entities:

```bash
# Check if database exists
psql postgresql://postgres:123@localhost:5432/bizops_dev -c "\dt"

# If tables don't exist, create them manually first:
python -c "from app.database import engine; from sqlmodel import SQLModel; SQLModel.metadata.create_all(engine)"
```

### 2. Create Initial Migration

When you're ready to start using migrations (e.g., before deploying to production):

```bash
# Generate initial migration from current schema
alembic revision --autogenerate -m "Initial schema with multi-tenancy"

# This creates a file like:
# alembic/versions/20250126_1430_abc123_initial_schema_with_multi_tenancy.py
```

### 3. Review the Generated Migration

**IMPORTANT:** Always review auto-generated migrations before applying them!

```bash
# Open the generated migration file
cat alembic/versions/20250126_*_initial_schema*.py
```

Check for:
- Correct table names
- Correct column types (UUID vs int)
- Foreign key constraints
- Indexes on frequently queried columns
- Default values

### 4. Apply the Migration

```bash
# Apply migration to database
alembic upgrade head

# Check migration status
alembic current

# View migration history
alembic history --verbose
```

### 5. Rolling Back Migrations

If you need to revert a migration:

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade all migrations
alembic downgrade base
```

## Common Migration Scenarios

### Adding a New Column

```bash
# 1. Add field to entity (e.g., app/internal/company/entity.py)
# 2. Generate migration
alembic revision --autogenerate -m "Add email_verified to User"

# 3. Review and apply
alembic upgrade head
```

### Changing Column Type

```bash
# 1. Update entity field type
# 2. Generate migration
alembic revision --autogenerate -m "Change company.nit from string to integer"

# 3. Review migration - may need manual adjustments for data conversion
# 4. Apply migration
alembic upgrade head
```

### Adding a New Table

```bash
# 1. Create new entity file (e.g., app/internal/subscription/entity.py)
# 2. Import entity in alembic/env.py
# 3. Generate migration
alembic revision --autogenerate -m "Add subscription table"

# 4. Apply migration
alembic upgrade head
```

### Renaming a Column

**CAUTION:** Autogenerate detects this as DROP + ADD, causing data loss!

```bash
# 1. Create migration manually
alembic revision -m "Rename customer_id to business_partner_id"

# 2. Edit the migration file manually:
def upgrade():
    op.alter_column('invoice', 'customer_id',
                    new_column_name='business_partner_id')

def downgrade():
    op.alter_column('invoice', 'business_partner_id',
                    new_column_name='customer_id')
```

### Adding Indexes

```bash
# 1. Add Field(index=True) to entity
# 2. Generate migration
alembic revision --autogenerate -m "Add index on invoice.company_id"

# 3. Review and apply
alembic upgrade head
```

## Multi-Tenancy Migration Strategy

### Current Schema State (Post-Refactoring)

All entities now have proper multi-tenancy support:

**Organization-scoped** (shared across companies):
- `BusinessPartner` - has `organization_id`
- `Account` - has `organization_id`
- `Product` - has `organization_id`
- `Category` - has `organization_id`

**Company-scoped** (isolated per company):
- `Invoice` - has `company_id`
- `JournalEntry` - has `company_id`
- `AccountPayable` - has `company_id`
- `AccountReceivable` - has `company_id`

**All IDs are UUID** (not int)

### When to Create Migrations

You should create migrations when:

1. **Deploying to staging/production** for the first time
2. **Adding new features** that require schema changes
3. **Modifying existing tables** (adding/removing columns)
4. **Changing column types or constraints**

### Migration Order for Fresh Database

If starting fresh (no existing data), create migrations in this order:

```bash
# 1. Core tables (no dependencies)
alembic revision --autogenerate -m "Create organization and user tables"

# 2. Company and business partner tables (depend on organization)
alembic revision --autogenerate -m "Create company and business partner tables"

# 3. Master data tables (depend on organization)
alembic revision --autogenerate -m "Create account, product, category tables"

# 4. Transaction tables (depend on company)
alembic revision --autogenerate -m "Create invoice and journal entry tables"

# 5. Relationship tables
alembic revision --autogenerate -m "Create user company access table"
```

## Migration from Existing Database

If you have an existing database with data:

### Step 1: Backup Your Data

```bash
# Full database backup
pg_dump postgresql://postgres:123@localhost:5432/bizops_dev > backup_before_migration.sql

# Or backup specific tables
pg_dump -t invoice -t company postgresql://postgres:123@localhost:5432/bizops_dev > backup_critical_tables.sql
```

### Step 2: Create Custom Migration

Since autogenerate won't match your current schema exactly, create a custom migration:

```bash
# Create empty migration
alembic revision -m "Migrate to multi-tenancy schema"
```

### Step 3: Write Migration Script

Edit the generated file with manual migration steps:

```python
def upgrade():
    # 1. Add new columns
    op.add_column('business_partner', sa.Column('organization_id', sa.UUID(), nullable=True))
    op.add_column('product', sa.Column('organization_id', sa.UUID(), nullable=True))

    # 2. Backfill data (assign all to first organization)
    op.execute("""
        UPDATE business_partner
        SET organization_id = (SELECT id FROM organizations LIMIT 1)
    """)

    # 3. Make columns non-nullable
    op.alter_column('business_partner', 'organization_id', nullable=False)

    # 4. Add foreign keys
    op.create_foreign_key(
        'fk_business_partner_organization',
        'business_partner', 'organizations',
        ['organization_id'], ['id']
    )

    # 5. Add indexes
    op.create_index('ix_business_partner_organization_id', 'business_partner', ['organization_id'])

def downgrade():
    # Reverse all changes
    op.drop_index('ix_business_partner_organization_id')
    op.drop_constraint('fk_business_partner_organization', 'business_partner')
    op.drop_column('business_partner', 'organization_id')
```

### Step 4: Test Migration

```bash
# Apply migration to test database
alembic upgrade head

# Verify data integrity
psql postgresql://postgres:123@localhost:5432/bizops_dev -c "
    SELECT COUNT(*) FROM business_partner WHERE organization_id IS NULL;
"

# If issues found, rollback
alembic downgrade -1
```

## Best Practices

### 1. Always Review Autogenerated Migrations

```bash
# After generating:
alembic revision --autogenerate -m "Description"

# ALWAYS review the generated file before applying:
cat alembic/versions/latest_migration.py
```

### 2. Test Migrations on Development First

```bash
# Test on local database
alembic upgrade head

# Verify application works
uvicorn app.main:app --reload

# Test rollback
alembic downgrade -1
alembic upgrade head
```

### 3. Use Descriptive Migration Messages

```bash
# Good
alembic revision -m "Add organization_id to business_partner for multi-tenancy"

# Bad
alembic revision -m "Update database"
```

### 4. Keep Migrations Small and Focused

```bash
# Good: One logical change per migration
alembic revision -m "Add email field to User"
alembic revision -m "Add index on User.email"

# Bad: Multiple unrelated changes
alembic revision -m "Add email to User and change company schema"
```

### 5. Include Data Migrations When Needed

```python
def upgrade():
    # Schema change
    op.add_column('user', sa.Column('is_active', sa.Boolean(), default=True))

    # Data migration
    op.execute("UPDATE user SET is_active = true WHERE is_active IS NULL")

    # Make column non-nullable after backfill
    op.alter_column('user', 'is_active', nullable=False)
```

### 6. Document Complex Migrations

```python
def upgrade():
    """
    Migrate from single-company to multi-tenancy.

    Changes:
    1. Add organization_id to business_partner
    2. Backfill organization_id from existing companies
    3. Update foreign keys and indexes

    Data migration strategy:
    - All existing business partners assigned to first organization
    - Admin can reassign later via UI
    """
    # Migration code...
```

## Troubleshooting

### Migration Conflict

```bash
# Error: Multiple heads detected
# Solution: Merge heads
alembic merge heads -m "Merge migration branches"
```

### Migration Won't Apply

```bash
# Check current state
alembic current

# Check if migration already applied
alembic history

# Mark migration as applied without running (DANGEROUS - use carefully)
alembic stamp <revision_id>
```

### Autogenerate Misses Changes

If autogenerate doesn't detect changes:

1. Check that entity is imported in `alembic/env.py`
2. Verify `SQLModel.metadata` includes the table
3. Create migration manually: `alembic revision -m "Description"`

### Can't Downgrade

If downgrade fails:

```bash
# Check error message
alembic downgrade -1

# May need to manually fix database state
# Then mark migration as downgraded
alembic stamp <previous_revision_id>
```

## Production Deployment Checklist

Before deploying migrations to production:

- [ ] Migrations tested on development database
- [ ] Migrations tested on staging database
- [ ] Full database backup created
- [ ] Rollback procedure tested
- [ ] Downtime window scheduled (if needed)
- [ ] Migration reviewed by team
- [ ] Data integrity verified after migration
- [ ] Application tested after migration

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Multi-Tenancy Architecture](./MULTI_TENANCY.md)
