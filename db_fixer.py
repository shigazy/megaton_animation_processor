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
        
        # First, modify the table structure to ensure it can hold full UUIDs
        print("Modifying table structure...")
        cursor.execute("""
        ALTER TABLE api_uploads 
        MODIFY COLUMN id CHAR(36) NOT NULL
        """)
        conn.commit()
        
        # Show current table structure
        cursor.execute("DESCRIBE api_uploads")
        print("\nTable structure:")
        for row in cursor.fetchall():
            print(row)

        # Now fix the entries
        cursor.execute("""
        SELECT id, data 
        FROM api_uploads
        """)
        
        entries = cursor.fetchall()
        for entry in entries:
            old_id, data = entry
            new_uuid = str(uuid.uuid4())
            
            print(f"\nFixing entry:")
            print(f"Old ID: {old_id}")
            print(f"New UUID: {new_uuid}")
            
            # Delete and reinsert with new UUID
            cursor.execute("DELETE FROM api_uploads WHERE id = %s", (old_id,))
            cursor.execute("""
            INSERT INTO api_uploads (id, data)
            VALUES (%s, %s)
            """, (new_uuid, data))
        
        conn.commit()
        
        # Verify the fix
        cursor.execute("""
        SELECT id, LENGTH(id) as id_length
        FROM api_uploads
        """)
        
        print("\nFinal verification:")
        for row in cursor.fetchall():
            print(f"ID: {row[0]}, Length: {row[1]}")
        
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
