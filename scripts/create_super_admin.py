#!/usr/bin/env python3
"""Script to create the initial super admin user.

This script creates a super admin user with full permissions.
Should be run once after database setup.

Usage:
    python scripts/create_super_admin.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import getpass
from uuid import uuid4

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.core.security import hash_password
from app.database import create_db_and_tables
from app.internal.user.entity import User


def create_super_admin():
    """Create the initial super admin user."""
    print("=" * 60)
    print("Create Super Admin User")
    print("=" * 60)
    print()

    # Default email from migration plan
    default_email = "allan.gallo.guerra@gmail.com"

    email = input(f"Enter super admin email [{default_email}]: ").strip()
    if not email:
        email = default_email

    # Get password securely
    password = getpass.getpass("Enter password: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        print("❌ Error: Passwords do not match!")
        sys.exit(1)

    if len(password) < 8:
        print("❌ Error: Password must be at least 8 characters long!")
        sys.exit(1)

    # Optional: Get first and last name
    first_name = input("Enter first name (optional): ").strip() or None
    last_name = input("Enter last name (optional): ").strip() or None

    print()
    print("Creating database tables...")

    # Create database tables
    create_db_and_tables()

    # Create engine and session
    engine = create_engine(settings.DATABASE_URI)

    with Session(engine) as session:
        # Check if user already exists
        statement = select(User).where(User.email == email)
        existing_user = session.exec(statement).first()

        if existing_user:
            print(f"❌ Error: User with email '{email}' already exists!")
            sys.exit(1)

        # Hash password
        hashed_pwd = hash_password(password)

        # Create super admin user
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=hashed_pwd,
            is_active=True,
            is_superuser=True,
            is_verified=True,
            first_name=first_name,
            last_name=last_name,
            # Temporary Auth0 fields (will be removed in Phase 7)
            auth_id=f"local|{uuid4()}",
            auth0_user_id=f"auth0|{uuid4()}",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        print()
        print("✅ Super admin user created successfully!")
        print()
        print("User Details:")
        print(f"  - Email: {user.email}")
        print(f"  - ID: {user.id}")
        print(f"  - First Name: {user.first_name or 'N/A'}")
        print(f"  - Last Name: {user.last_name or 'N/A'}")
        print(f"  - Is Superuser: {user.is_superuser}")
        print(f"  - Is Active: {user.is_active}")
        print(f"  - Is Verified: {user.is_verified}")
        print()
        print("You can now:")
        print("  1. Log in with this account")
        print("  2. Send invitations to other users")
        print("  3. Manage permissions and roles")
        print()

    engine.dispose()


if __name__ == "__main__":
    try:
        create_super_admin()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
