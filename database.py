import sqlite3


def get_conn():
    # Подключаемся к базе данных
    conn = sqlite3.connect('example.db')
    return conn


def create_table():
    conn = get_conn()
    # Создаем таблицу
    conn.execute('''CREATE TABLE IF NOT EXISTS users
    (
    id INTEGER
    );
    ''')
    conn.commit()
    conn.close()


def insert_table(id_):
    conn = get_conn()
    # Вставляем новые данные в таблицу
    conn.execute(f"INSERT INTO users VALUES ({id_})")
    # Фиксируем транзакцию
    conn.commit()
    conn.close()


def user_in_table(id_):
    conn = get_conn()
    user = conn.execute(f"SELECT * FROM users WHERE id={id_}")
    user = user.fetchone()
    conn.close()

    if user is not None:
        return True

    return False


if __name__ == "__main__":
    create_table()

