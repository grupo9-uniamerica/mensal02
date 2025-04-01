from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator  # Adicionei o validator aqui
from datetime import datetime
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from models import (
    add_room, add_reservation, 
    get_all_reservations, get_all_rooms,
    room_exists
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

class RoomResponse(BaseModel):
    id: int
    name: str
    capacity: int
    location: str
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
        room_id = add_room(room.name, room.capacity, room.location)
        return {
            "id": room_id,
            "name": room.name,
            "capacity": room.capacity,
            "location": room.location,
            "created_at": datetime.now()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/rooms/", response_model=List[RoomResponse])
def list_rooms():
    return get_all_rooms()

@app.post("/reservations/", response_model=dict)
async def create_reservation(reservation: ReservationRequest):
    try:
        # Remova as conversões - já foram feitas pelo validator
        success = add_reservation(
            room_id=reservation.room_id,
            user_name=reservation.user_name,
            start_time=reservation.start_time,  # Já é datetime
            end_time=reservation.end_time      # Já é datetime
        )
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Conflito de horário: sala já reservada neste período"
            )
            
        return {"message": "Reserva criada com sucesso"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/reservations/", response_model=List[ReservationResponse])
def list_reservations():
    return get_all_reservations()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)