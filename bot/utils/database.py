import os
import psycopg2

def get_connection():
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    
    connection = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    return connection

def execute_query(query, params=None):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            connection.commit()
    except Exception as e:
        print(f"Error executing query: {e}")
        connection.rollback()
    finally:
        connection.close()

def fetch_data(query, params=None):
    connection = get_connection()
    data = []
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        connection.close()
    return data