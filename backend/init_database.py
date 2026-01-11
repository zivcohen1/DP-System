import sqlite3
import pandas as pd
import os

def init_database():
    """Initialize SQLite database from CSV files"""
    
    # Paths
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'root', 'databases')
    
    # Remove existing database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  Removed existing database")
    
    # Create connection
    conn = sqlite3.connect(db_path)
    print(f"📦 Creating database at: {db_path}")
    
    # Load employees.csv
    employees_path = os.path.join(csv_dir, 'employees.csv')
    if os.path.exists(employees_path):
        print(f"📊 Loading employees from {employees_path}...")
        df_employees = pd.read_csv(employees_path)
        df_employees.to_sql('employees', conn, if_exists='replace', index=False)
        print(f"   ✅ Loaded {len(df_employees)} employees")
    else:
        print(f"   ⚠️  Warning: {employees_path} not found")
    
    # Load projects.csv
    projects_path = os.path.join(csv_dir, 'projects.csv')
    if os.path.exists(projects_path):
        print(f"📊 Loading projects from {projects_path}...")
        df_projects = pd.read_csv(projects_path)
        df_projects.to_sql('projects', conn, if_exists='replace', index=False)
        print(f"   ✅ Loaded {len(df_projects)} projects")
    else:
        print(f"   ⚠️  Warning: {projects_path} not found")
    
    # Create indexes for better performance
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE INDEX idx_employee_id ON employees(id);")
        cursor.execute("CREATE INDEX idx_project_employee_id ON projects(employee_id);")
        print("🔍 Created indexes for better query performance")
    except:
        pass
    
    conn.commit()
    conn.close()
    
    print("=" * 70)
    print("✅ Database initialized successfully!")
    print(f"   Location: {db_path}")
    print("=" * 70)

if __name__ == "__main__":
    init_database()
