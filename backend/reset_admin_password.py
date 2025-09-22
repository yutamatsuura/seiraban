#!/usr/bin/env python3
"""Reset admin password for testing"""

import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database URL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL not set")
    exit(1)

# New password for testing
NEW_PASSWORD = "testpass123"

# Create engine
engine = create_engine(DATABASE_URL)

# Hash the new password
hashed_password = pwd_context.hash(NEW_PASSWORD)

# Update admin user password
with engine.connect() as conn:
    result = conn.execute(text("""
        UPDATE users
        SET hashed_password = :password
        WHERE email = 'matsuura.yuta@gmail.com'
        RETURNING email, is_superuser
    """), {"password": hashed_password})

    conn.commit()

    updated = result.fetchone()
    if updated:
        print(f"✅ Password updated for {updated[0]} (is_superuser: {updated[1]})")
        print(f"   New password: {NEW_PASSWORD}")
    else:
        print("❌ User not found")