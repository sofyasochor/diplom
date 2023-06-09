import sqlite3


class Database:

    def get_conn(self):
        # Подключаемся к базе данных
        conn = sqlite3.connect('example.db')
        return conn


    def create_table(self):
        conn = self.get_conn()
        # Создаем таблицу
        conn.execute('''CREATE TABLE IF NOT EXISTS users
        (
        id INTEGER
        );
        ''')
        conn.commit()
        conn.close()


    def insert_table(self, id_):
        conn = self.get_conn()
        # Вставляем новые данные в таблицу
        conn.execute(f"INSERT INTO users VALUES ({id_})")
        # Фиксируем транзакцию
        conn.commit()
        conn.close()


    def user_in_table(self, id_):
        conn = self.get_conn()
        user = conn.execute(f"SELECT * FROM users WHERE id={id_}")
        user = user.fetchone()
        conn.close()

        if user is not None:
            return True

        return False
