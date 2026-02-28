# backend/seed.py
import os
import pandas as pd
from database import SessionLocal, engine, Base, init_db
import models

# Create tables
Base.metadata.create_all(bind=engine)
print("Tables created!")

# Initialize database
init_db()

# Get session
db = SessionLocal()

try:
    # Read CSV
    df_users = pd.read_csv("user.csv")
    
    print(f"\n Seeding {len(df_users)} users from CSV...")
    
    for _, row in df_users.iterrows():
        # Check if user already exists
        existing_user = db.query(models.User).filter_by(email=row["email"]).first()
        
        if existing_user:
            print(f"⚠️  User {row['email']} already exists, skipping...")
            continue
        
        # Create new user
        user = models.User(
            name=row["name"],
            email=row["email"],
            role=row.get("role", "farmer")
        )
        
        # IMPORTANT: Set password using the model method
        # You can set a default password or read from CSV
        default_password = "DefaultPassword123"  # Change this for production
        user.set_password(default_password)
        
        db.add(user)
        print(f"✓ Added user: {row['name']} ({row['email']})")
    
    db.commit()
    print("\n✓ Users seeded successfully!")
    
    # Display seeded users
    all_users = db.query(models.User).all()
    print(f"\n Total users in database: {len(all_users)}")
    for user in all_users:
        print(f"  - {user.name} ({user.email}) - Role: {user.role}")

except Exception as e:
    db.rollback()
    print(f"✗ Error during seeding: {e}")
    raise

finally:
    db.close()
