from app import app, db
from sqlalchemy import inspect

with app.app_context():
    # Drop existing tables
    db.drop_all()
    print("✅ Dropped existing tables!")
    
    # Create new tables
    db.create_all()
    print("✅ Database created with all columns!")
    
    # Check columns
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('question')]
    print("Columns in question table:", columns)
    
    print("\n✅ Database setup complete!")