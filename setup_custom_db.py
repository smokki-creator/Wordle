
import os
import getpass

def setup_custom_db():
    print("=== Настройка подключения к PostgreSQL базе данных ===\n")
    
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
    print("\nОбновляем конфигурацию приложения...")
    
    # Обновляем app.py для использования .env файла
    with open("app.py", "r") as f:
        content = f.read()
    
    # Проверяем, содержит ли файл уже код для загрузки .env
    if "if os.path.exists(\".env\"):" not in content:
        # Находим строку с DATABASE_URL
        db_config_line = "app.config[\"SQLALCHEMY_DATABASE_URI\"] = os.environ.get(\"DATABASE_URL\")"
        
        # Добавляем код для загрузки .env перед настройкой DATABASE_URL
        env_loader_code = """# Проверяем существование .env файла и загружаем из него DATABASE_URL
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("DATABASE_URL="):
                os.environ["DATABASE_URL"] = line.split("=", 1)[1].strip()

"""
        # Заменяем строку конфигурации на новую с загрузкой .env
        new_content = content.replace(db_config_line, env_loader_code + db_config_line)
        
        # Записываем обновленный контент
        with open("app.py", "w") as f:
            f.write(new_content)
    
    print("\nПриложение настроено для использования вашей базы данных!")
    print("Теперь вы можете перезапустить приложение, и оно будет использовать вашу базу данных.")
    print("\nЕсли у вас есть pgAdmin, используйте те же параметры подключения (хост, порт, имя БД, пользователь, пароль).")

if __name__ == "__main__":
    setup_custom_db()
