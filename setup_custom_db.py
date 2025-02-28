
import os
import sys
import getpass

def setup_custom_db():
    print("=== Настройка подключения к вашей базе данных PostgreSQL ===\n")
    
    # Получаем информацию о базе данных от пользователя
    host = input("Введите хост (например, localhost или IP-адрес): ")
    port = input("Введите порт (обычно 5432): ")
    db_name = input("Введите имя базы данных: ")
    user = input("Введите имя пользователя: ")
    password = getpass.getpass("Введите пароль: ")
    
    # Формируем строку подключения
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    
    # Сохраняем в .env файл
    with open(".env", "w") as f:
        f.write(f"DATABASE_URL={db_url}\n")
    
    print("\nНастройка завершена! Строка подключения сохранена в файл .env")
    print("Теперь перезапустите приложение, чтобы использовать вашу базу данных.")

if __name__ == "__main__":
    setup_custom_db()
