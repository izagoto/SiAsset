from sqlalchemy.orm import Session
from app.models.role import Role
import uuid

def seed_roles(db: Session):
    """Seed roles data"""
    roles_data = [
        {
            "id": uuid.UUID("00000000-0000-0000-0000-000000000001"),
            "name": "super_admin",
            "description": "Super Administrator with full access to all features including user management, roles, assets, categories, loans, and audit logs"
        },
        {
            "id": uuid.UUID("00000000-0000-0000-0000-000000000002"),
            "name": "user",
            "description": "Regular user with limited access - can view assets, borrow/return assets, and view own loan history"
        }
    ]
    
    for role_data in roles_data:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing_role:
            role = Role(**role_data)
            db.add(role)
            print(f"✓ Created role: {role_data['name']}")
        else:
            print(f"⊘ Role already exists: {role_data['name']}")
    
    db.commit()
    print("Roles seeding completed!")

