
import os
import psycopg2

def test_connection():
    # Получаем URL из переменных окружения
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("DATABASE_URL не найден в переменных окружения")
        return
    
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Выполняем простой запрос
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"Версия PostgreSQL: {version[0]}")
        
        # Проверяем наличие таблиц в нашей базе данных
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = cur.fetchall()
        if tables:
            print("Таблицы в базе данных:")
            for table in tables:
                print(f"- {table[0]}")
        else:
            print("В базе данных нет таблиц")
            
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
    finally:
        # Закрываем соединение
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_connection()
