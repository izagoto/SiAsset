from sqlalchemy.orm import Session
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password
import uuid

def seed_users(db: Session):
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    user_role = db.query(Role).filter(Role.name == "user").first()
    
    if not super_admin_role or not user_role:
        print("⚠ Roles not found. Please run role seeder first!")
        return
    
    users_data = [
        {
            "id": uuid.UUID("00000000-0000-0000-0000-000000000010"),
            "username": "superadmin",
            "email": "superadmin@example.com",
            "password": "admin123",
            "role_id": super_admin_role.id,
            "is_active": True
        },
        {
            "id": uuid.UUID("00000000-0000-0000-0000-000000000011"),
            "username": "user",
            "email": "user@example.com",
            "password": "user123",
            "role_id": user_role.id,
            "is_active": True
        }
    ]
    
    for user_data in users_data:
        existing_user = db.query(User).filter(
            (User.username == user_data["username"]) | 
            (User.email == user_data["email"])
        ).first()
        
        if not existing_user:
            password = user_data.pop("password")
            user_data["password_hash"] = hash_password(password)
            
            user = User(**user_data)
            db.add(user)
            print(f"✓ Created user: {user_data['username']} ({user_data['email']})")
        else:
            print(f"⊘ User already exists: {user_data['username']}")
    
    db.commit()
    print("Users seeding completed!")

