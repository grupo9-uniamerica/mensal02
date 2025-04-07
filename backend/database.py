import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Função que retorna uma conexão com o banco de dados MySQL."""
    try:
        conn = mysql.connector.connect(
            host='host.docker.internal',
            user='root',
            password='kappa110520',
            database='salasdb',
            port=3306,
            auth_plugin='mysql_native_password'  # Adicione esta linha
        )
        return conn
    except Error as err:
        print(f"Erro ao conectar ao MySQL: {err}")
        raise