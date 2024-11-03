import mysql.connector
import uuid
from main import get_secret

def check_and_fix_database():
    try:
        # Get credentials and connect
        secret_name = 'arn:aws:secretsmanager:us-east-1:035700659240:secret:rds!db-db12e38f-e948-4dd0-8cb5-6c599e31ae53-jEabKN'
        db_credentials = get_secret(secret_name)
        
        conn = mysql.connector.connect(
            host='database-1.c9e2eoe0qp8t.us-east-1.rds.amazonaws.com',
            database='megaton',
            user=db_credentials['username'],
            password=db_credentials['password']
        )
        
        cursor = conn.cursor()
        
        # 1. First, let's check the table structure
        cursor.execute("DESCRIBE api_uploads")
        table_structure = cursor.fetchall()
        print("Current table structure:")
        for column in table_structure:
            print(column)
            
        # 2. Create a temporary table with correct structure
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_uploads_new (
            id CHAR(36) NOT NULL PRIMARY KEY,
            data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 3. Copy data from old table to new table
        cursor.execute("""
        INSERT INTO api_uploads_new (id, data)
        SELECT 
            COALESCE(
                CASE 
                    WHEN id REGEXP '^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$' 
                    THEN id 
                    ELSE UUID()
                END,
                UUID()
            ) as id,
            data
        FROM api_uploads
        """)
        
        # 4. Backup old table
        cursor.execute("RENAME TABLE api_uploads TO api_uploads_backup")
        
        # 5. Rename new table to original name
        cursor.execute("RENAME TABLE api_uploads_new TO api_uploads")
        
        conn.commit()
        
        # 6. Verify the fix
        cursor.execute("SELECT id, data FROM api_uploads LIMIT 5")
        results = cursor.fetchall()
        print("\nSample records from new table:")
        for row in results:
            print(f"ID: {row[0]}")
            
        print("\nFix completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_and_fix_database()
