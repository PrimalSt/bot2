import sqlite3

DB_PATH = "casino_bot.db"

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id TEXT UNIQUE,
        username TEXT,
        balance INTEGER DEFAULT 1000
        last_bonus TEXT DEFAULT NULL
    )
    ''')

    # Создание таблицы игр
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_name TEXT,
        bet_amount INTEGER,
        win_amount INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    conn.commit()
    conn.close()

def add_user(telegram_id, username):
    """Добавление нового пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO users (telegram_id, username) VALUES (?, ?)
        ''', (telegram_id, username))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Пользователь уже существует
    finally:
        conn.close()

def get_balance(telegram_id):
    """Получение баланса пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT balance FROM users WHERE telegram_id = ?
    ''', (telegram_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_balance(telegram_id, amount):
    """Обновление баланса пользователя"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE users SET balance = balance + ? WHERE telegram_id = ?
    ''', (amount, telegram_id))
    conn.commit()
    conn.close()