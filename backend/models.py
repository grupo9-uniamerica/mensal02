from database import get_db_connection
from datetime import datetime
import mysql.connector

def create_tables():
    """Cria as tabelas se não existirem"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tabela de salas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                capacity INT NOT NULL,
                location VARCHAR(255) NOT NULL,
                available BOOLEAN NOT NULL DEFAULT TRUE,  # <- Adicionei esta linha
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de reservas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_id INT NOT NULL,
                user_name VARCHAR(100) NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
                CONSTRAINT chk_time CHECK (start_time < end_time)
            )
        """)
        
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao criar tabelas: {err}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Inicializa as tabelas ao importar o módulo
create_tables()

def room_exists(room_id):
    """Verifica se uma sala existe"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM rooms WHERE id = %s", (room_id,))
        return cursor.fetchone() is not None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_room(name, capacity, location, available=True):  # Adicione o parâmetro default
    """Adiciona uma nova sala"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rooms (name, capacity, location, available) VALUES (%s, %s, %s, %s)",  # Adicione o campo
            (name, capacity, location, available)  # Adicione o valor
        )
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        raise ValueError(f"Erro ao adicionar sala: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def check_availability(room_id, start_time, end_time):
    """Verifica se a sala está disponível no período"""
    if start_time >= end_time:
        raise ValueError("O horário final deve ser após o horário inicial")
    
    if not room_exists(room_id):
        raise ValueError("Sala não encontrada")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM reservations 
            WHERE room_id = %s 
            AND NOT (%s >= end_time OR %s <= start_time)
        """, (room_id, end_time, start_time))
        return cursor.fetchone() is None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_reservation(room_id: int, user_name: str, start_time: datetime, end_time: datetime) -> bool:
    """Adiciona uma nova reserva com validação completa"""
    conn = None
    try:
        # Validação básica
        if start_time >= end_time:
            raise ValueError("O horário final deve ser após o horário inicial")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se a sala existe
        cursor.execute("SELECT id FROM rooms WHERE id = %s", (room_id,))
        if not cursor.fetchone():
            raise ValueError("Sala não encontrada")
        
        # Verifica conflitos de horário
        cursor.execute("""
            SELECT id FROM reservations 
            WHERE room_id = %s 
            AND NOT (%s >= end_time OR %s <= start_time)
        """, (room_id, end_time, start_time))
        
        if cursor.fetchone():
            return False
            
        # Insere a reserva
        cursor.execute("""
            INSERT INTO reservations 
            (room_id, user_name, start_time, end_time)
            VALUES (%s, %s, %s, %s)
        """, (room_id, user_name, start_time, end_time))
        
        conn.commit()
        return True
        
    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        raise ValueError(f"Erro no banco de dados: {err}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
def get_all_reservations():
    """Obtém todas as reservas"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Consulta atualizada sem created_at
        cursor.execute("""
            SELECT r.id, r.room_id, rm.name as room_name, 
                   r.user_name, r.start_time, r.end_time
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            ORDER BY r.start_time
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao buscar reservas: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_rooms():
    """Obtém todas as salas"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, capacity, location, 
                   COALESCE(available, TRUE) as available,  # Garante que sempre retorne um valor
                   COALESCE(created_at, NOW()) as created_at
            FROM rooms 
            ORDER BY name
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao buscar salas: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def check_room_availability(room_id: int, start_time: datetime = None, end_time: datetime = None) -> bool:
    """Verifica se a sala está disponível para reserva"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if start_time and end_time:
            # Verifica conflitos em um período específico
            cursor.execute("""
                SELECT id FROM reservations 
                WHERE room_id = %s 
                AND NOT (%s >= end_time OR %s <= start_time)
            """, (room_id, end_time, start_time))
        else:
            # Verifica se há qualquer reserva para a sala
            cursor.execute("SELECT id FROM reservations WHERE room_id = %s", (room_id,))
            
        return cursor.fetchone() is None
        
    except mysql.connector.Error as err:
        print(f"Erro ao verificar disponibilidade: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()