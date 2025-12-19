"""
Script to run database seeders
Usage: python -m app.db.seeders.run_seeder
"""
from app.db.session import SessionLocal
from app.db.seeders.role_seeder import seed_roles
from app.db.seeders.user_seeder import seed_users

def run_seeders():
    """Run all seeders"""
    db = SessionLocal()
    try:
        print("=" * 50)
        print("Starting database seeding...")
        print("=" * 50)
        
        # Seed roles first (required for users)
        print("\n[1/2] Seeding roles...")
        seed_roles(db)
        
        # Seed users
        print("\n[2/2] Seeding users...")
        seed_users(db)
        
        print("\n" + "=" * 50)
        print("Database seeding completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_seeders()

