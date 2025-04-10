from fastapi import FastAPI, HTTPException, Query, Depends, Security # Adicione Query aqui
from pydantic import BaseModel, validator  # Adicionei o validator aqui
from datetime import datetime, timedelta
from typing import List
from mysql.connector import Error
from typing import Optional
from database import get_db_connection, get_user_by_username
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from models import (
    add_room, 
    delete_room,
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
    allow_origins=["http://10.0.0.3:80", "http://35.199.127.220:80"],  # Permite o frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os headers
)


# Begin Login
SECRET_KEY = "geladeiratsunami"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, password_hash):
    """Verifica se a senha fornecida corresponde à senha hash armazenada."""
    is_valid = pwd_context.verify(plain_password, password_hash)
    return is_valid

def get_password_hash(password):
    """Gera um hash para a senha fornecida."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Cria um token de acesso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        return None  # Melhor que False
    return user

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code = 401,
            detail = "Usuário ou senha inválidos",
            headers = {"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    

# End Login


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
def create_room(room: Room, current_user: str = Depends(get_current_user)):
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
    
@app.delete("/rooms/{room_id}", response_model=dict)
def excluir_sala(room_id: int, current_user: str = Depends(get_current_user)):
    """Deleta uma sala pelo ID."""
    try:
        deleted = delete_room(room_id)  # Supondo que você tenha uma função para remover do banco
        if not deleted:
            raise HTTPException(status_code=404, detail="Sala não encontrada")
        return {"message": "Sala deletada com sucesso"}
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
    uvicorn.run(app, host="0.0.0.0", port=8080)
