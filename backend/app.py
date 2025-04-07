from fastapi import FastAPI, HTTPException, Query  # Adicione Query aqui
from pydantic import BaseModel, validator  # Adicionei o validator aqui
from datetime import datetime
from typing import List
from mysql.connector import Error
from typing import Optional
from database import get_db_connection
from fastapi.middleware.cors import CORSMiddleware
from models import (
    add_room, 
    add_reservation, 
    get_all_reservations, 
    get_all_rooms,
    room_exists,
    check_room_availability  # Adicione esta importação
)

app = FastAPI(title="Sistema de Reserva de Salas",
              description="API para gerenciar salas e reservas",
              version="1.0.0")


# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Permite o frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)


# Modelos para Salas
class Room(BaseModel):
    name: str
    capacity: int
    location: str
    available: bool = True  # Valor padrão True se não for enviado


class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    location: str
    available: bool
    created_at: datetime

    class Config:
        orm_mode = True

# Modelos para Reservas
class ReservationRequest(BaseModel):
    room_id: int
    user_name: str
    start_time: str
    end_time: str

    @validator('start_time', 'end_time')
    def parse_datetime(cls, value):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise ValueError("Formato de data inválido. Use YYYY-MM-DDTHH:MM:SS")
        
class AvailabilityResponse(BaseModel):
    available: bool

class ReservationResponse(BaseModel):
    id: int
    room_id: int
    room_name: str
    user_name: str
    start_time: datetime
    end_time: datetime
    # Remova created_at se não existir no banco

    class Config:
        orm_mode = True

# Endpoints
@app.post("/rooms/", response_model=RoomResponse)
def create_room(room: Room):
    try:
        room_id = add_room(
            name=room.name,
            capacity=room.capacity,
            location=room.location,
            available=room.available  # Novo parâmetro
        )
        return {
            "id": room_id,
            "name": room.name,
            "capacity": room.capacity,
            "location": room.location,
            "available": room.available,  # Campo novo
            "created_at": datetime.now()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/rooms/", response_model=List[RoomResponse])
def list_rooms():
    try:
        rooms = get_all_rooms()
        rooms_with_availability = []
        for room in rooms:
            # Cria uma cópia do dicionário para não modificar o original
            room_data = {
                "id": room["id"],
                "name": room["name"],
                "capacity": room["capacity"],
                "location": room["location"],
                "created_at": room["created_at"],
                "available": check_room_availability(room["id"])
            }
            rooms_with_availability.append(room_data)
        return rooms_with_availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reservations/check")
async def check_availability(
    room_id: int = Query(..., description="ID da sala"),
    start_time: Optional[str] = Query(None, description="Horário de início (ISO format)"),
    end_time: Optional[str] = Query(None, description="Horário de término (ISO format)")
):
    try:
        # Converte strings para datetime se fornecidas
        start = datetime.fromisoformat(start_time) if start_time else None
        end = datetime.fromisoformat(end_time) if end_time else None
        
        available = check_room_availability(room_id, start, end)
        return {"available": available}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.post("/reservations/", response_model=dict)
async def create_reservation(reservation: ReservationRequest):
    try:
        print(f"Tentando criar reserva: {reservation.dict()}")  # Log
        
        if not room_exists(reservation.room_id):
            raise HTTPException(status_code=404, detail="Sala não encontrada")
        
        available = check_room_availability(
            reservation.room_id,
            reservation.start_time,
            reservation.end_time
        )
        print(f"Disponibilidade: {available}")  # Log
        
        if not available:
            raise HTTPException(
                status_code=400,
                detail="Sala já reservada neste período"
            )
            
        success = add_reservation(
            room_id=reservation.room_id,
            user_name=reservation.user_name,
            start_time=reservation.start_time,
            end_time=reservation.end_time
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Erro ao criar reserva")
            
        return {"message": "Reserva criada com sucesso"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/reservations/", response_model=List[ReservationResponse])
def list_reservations():
    return get_all_reservations()


def verify_database_connection():
    """Verifica se o banco de dados está ativo."""
    try:
        # Sua lógica de conexão ao banco
        connection = get_db_connection()  # Sua função de conexão ao banco
        if connection:
            print("Banco de dados conectado com sucesso!")
        else:
            print("Banco de dados indisponível. Inicializando backend sem banco.")
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")



if __name__ == "__main__":
    verify_database_connection()  # Verifica o banco antes de inicializar o servidor
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)