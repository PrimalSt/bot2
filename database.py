import psycopg2
from psycopg2.extras import DictCursor
import os

# Получаем URL из переменной окружения
DATABASE_URL = os.getenv('DATABASE_URL')

def init_db():
    """Инициализация базы данных"""
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    # Создание таблицы пользователей (синтаксис PostgreSQL)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        telegram_id TEXT UNIQUE,
        username TEXT,
        balance INTEGER DEFAULT 1000,
        last_bonus TEXT 
    )
    ''')

    # Создание таблицы товаров
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shop_items (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        description TEXT
    )
    ''')

    # Добавление тестовых товаров
    cursor.execute("SELECT COUNT(*) FROM shop_items")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
                INSERT INTO shop_items (name, price, description)
                VALUES (%s, %s, %s)
        ''', [
            ("Увеличение выигрыша", 500, "Увеличивает все выигрыши на 20%"),
            ("Дополнительные монеты", 300, "Получите 100 монет сразу")
        ])

    # Создание таблицы игр
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
        game_name TEXT,
        bet_amount INTEGER,
        win_amount INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Проверка наличия столбца last_bonus
    cursor.execute('''
    ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS last_bonus TEXT
    ''')

    conn.commit()
    conn.close()

def add_user(telegram_id, username):
    """Добавление нового пользователя"""
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO users (telegram_id, username) VALUES (%s, %s)
        ''', (telegram_id, username))
        conn.commit()
    except psycopg2.IntegrityError:
        pass  # Пользователь уже существует
    finally:
        conn.close()

def get_balance(telegram_id):
    """Получение баланса пользователя"""
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT balance FROM users WHERE telegram_id = %s
    ''', (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_balance(telegram_id, amount):
    """Обновление баланса пользователя"""
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE users SET balance = balance + %s WHERE telegram_id = %s
    ''', (amount, telegram_id))
    conn.commit()
    conn.close()