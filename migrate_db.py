from app import app, db
from sqlalchemy import text

with app.app_context():
    inspector = db.inspect(db.engine)
    
    # Check if table exists
    if 'question' not in inspector.get_table_names():
        print("⚠️ Table 'question' doesn't exist. Creating...")
        db.create_all()
        print("✅ Table created!")
    
    # Get existing columns
    columns = [col['name'] for col in inspector.get_columns('question')]
    print(f"📋 Existing columns: {columns}")
    
    # New columns to add
    new_columns = {
        'question_image': 'TEXT',
        'option_a_image': 'TEXT',
        'option_b_image': 'TEXT',
        'option_c_image': 'TEXT',
        'option_d_image': 'TEXT',
        'solution_image': 'TEXT'
    }
    
    # Add missing columns
    added = []
    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            print(f"➕ Adding column: {col_name}")
            db.session.execute(text(f'ALTER TABLE question ADD COLUMN {col_name} {col_type}'))
            added.append(col_name)
    
    db.session.commit()
    
    if added:
        print(f"✅ Added columns: {', '.join(added)}")
    else:
        print("✅ All columns already exist!")
    
    # Show final columns
    final_columns = [col['name'] for col in inspector.get_columns('question')]
    print(f"📋 Final columns: {final_columns}")