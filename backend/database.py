import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Função que retorna uma conexão com o banco de dados MySQL."""
    try:
        conn = mysql.connector.connect(
            #host='10.0.0.5',
            host='127.0.0.1',
            user='root',
            #password='kappa110520',
            password ='root',
            database='salasdb',
            port=3306,
            auth_plugin='mysql_native_password'  # Adicione esta linha
        )
        return conn
    except Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        raise

def get_user_by_username(username: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT username, password_hash FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Error as err:
        print(f"Erro ao buscar usuário: {err}")
        return None
