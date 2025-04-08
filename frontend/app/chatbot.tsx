"use client";

import { useState, useEffect } from "react";
import styled from "styled-components";
import { Calendar, Clock, User, ArrowLeft, Check } from "lucide-react";

// Estilos baseados no exemplo fornecido
const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background: linear-gradient(135deg, #0c101c, #171e32);
  font-family: system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  font-weight: 600;
  color: #f2ddcc;
`;

const MainContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  height: 100vh;
  padding: 1rem;

  @media (min-width: 768px) {
    padding-left: clamp(20px, 20vw, 600px);
    padding-right: clamp(20px, 20vw, 600px);
  }
`;

const Header = styled.div`
  padding: 1.5rem;
  text-align: center;
  font-weight: bold;
  font-size: 1.5rem;
  background: linear-gradient(90deg, #3182ce, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 1rem;
`;

const RoomListContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  padding-bottom: 120px;

  &::-webkit-scrollbar {
    width: 5px;
  }

  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
  }

  &::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #3182ce, #2563eb);
    border-radius: 10px;
  }
`;

const RoomCard = styled.div<{ $available: boolean }>`
  background: #171e32;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  opacity: ${({ $available }) => ($available ? 1 : 0.6)};
  cursor: ${({ $available }) => ($available ? 'pointer' : 'not-allowed')};

  &:hover {
    transform: ${({ $available }) => ($available ? 'translateY(-5px)' : 'none')};
    box-shadow: ${({ $available }) => ($available ? '0 10px 20px rgba(0, 0, 0, 0.2)' : 'none')};
    border-color: ${({ $available }) => ($available ? '#3182ce' : 'rgba(255, 255, 255, 0.1)')};
  }
`;

const RoomImage = styled.div`
  width: 100%;
  height: 120px;
  background: linear-gradient(135deg, #3182ce, #7c3aed);
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
`;

const RoomTitle = styled.h3`
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: #f2ddcc;
`;

const RoomMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #a0aec0;
  margin-bottom: 0.5rem;
`;

const AvailabilityBadge = styled.span<{ $available: boolean }>`
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  background: ${({ $available }) => ($available ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)')};
  color: ${({ $available }) => ($available ? '#10b981' : '#ef4444')};
`;

const BookButton = styled.button<{ $available: boolean }>`
  width: 100%;
  padding: 0.75rem;
  margin-top: 1rem;
  border-radius: 8px;
  border: none;
  background: ${({ $available }) => ($available ? 'linear-gradient(135deg, #3182ce, #2563eb)' : 'rgba(255, 255, 255, 0.05)')};
  color: ${({ $available }) => ($available ? 'white' : 'rgba(255, 255, 255, 0.3)')};
  cursor: ${({ $available }) => ($available ? 'pointer' : 'not-allowed')};
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  &:hover {
    transform: ${({ $available }) => ($available ? 'scale(1.02)' : 'none')};
    box-shadow: ${({ $available }) => ($available ? '0 4px 6px rgba(0, 0, 0, 0.1)' : 'none')};
  }
`;

const FormContainer = styled.div`
  background: #171e32;
  border-radius: 12px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 500px;
  margin: 0 auto;
  width: 100%;
  animation: fadeIn 0.4s ease-in-out;

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

const FormHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
`;

const FormTitle = styled.h2`
  font-size: 1.5rem;
  color: #f2ddcc;
`;

const FormGroup = styled.div`
  margin-bottom: 1.5rem;
`;

const FormLabel = styled.label`
  display: block;
  margin-bottom: 0.5rem;
  color: #a0aec0;
  font-size: 0.9rem;
`;

const FormInput = styled.input`
  width: 100%;
  padding: 0.75rem 1rem;
  background: #101524;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 1rem;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: #3182ce;
    box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.2);
  }
`;

const FormActions = styled.div`
  display: flex;
  justify-content: space-between;
  margin-top: 2rem;
`;

const ActionButton = styled.button<{ $primary?: boolean }>`
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  border: none;
  background: ${({ $primary }) => ($primary ? 'linear-gradient(135deg, #3182ce, #2563eb)' : 'rgba(255, 255, 255, 0.05)')};
  color: ${({ $primary }) => ($primary ? 'white' : '#a0aec0')};
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;

  &:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
`;

const LoadingIndicator = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  svg {
    animation: spin 1s linear infinite;
    color: #3182ce;
  }
`;

interface Room {
  id: number;
  name: string;
  capacity: number;
  location: string;
  available: boolean;
  created_at: string;
}

interface ReservationFormData {
  name: string;
  startTime: string;
  endTime: string;
}

export default function StudyRoomScheduler() {
  const [view, setView] = useState<'list' | 'form'>('list');
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRoom, setSelectedRoom] = useState<Room | null>(null);
  const [formData, setFormData] = useState<ReservationFormData>({
    name: '',
    startTime: '',
    endTime: '',
  });

  // Função para buscar as salas do endpoint
  const fetchRooms = async (): Promise<Room[]> => {
    try {
      const response = await fetch('/rooms/');
      if (!response.ok) throw new Error('Erro ao buscar salas');
      return await response.json();
    } catch (error) {
      console.error('Erro ao buscar salas:', error);
      return [];
    }
  };


  const loadRooms = async () => {
    setLoading(true);
    try {
      const fetchedRooms = await fetchRooms();
      setRooms(fetchedRooms);
    } catch (error) {
      console.error('Erro ao carregar salas:', error);
    } finally {
      setLoading(false);
    }
  };

  // UseEffect para carregar as salas
  useEffect(() => {
    loadRooms();
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleBookRoom = (room: Room) => {
    setSelectedRoom(room);
    
    // Define horários padrão (agora + 1h)
    const now = new Date();
    const defaultStart = new Date(now.getTime() + 60 * 60 * 1000);
    const defaultEnd = new Date(defaultStart.getTime() + 60 * 60 * 1000);
    
    setFormData({
      name: '',
      startTime: defaultStart.toISOString().slice(0, 16),
      endTime: defaultEnd.toISOString().slice(0, 16),
    });
    
    setView('form');
  };


   const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRoom) return;
    
    setLoading(true);

    try {
      // Validações básicas
      if (!formData.name.trim()) throw new Error('Informe seu nome');
      if (!formData.startTime || !formData.endTime) throw new Error('Informe os horários');
      
      const start = new Date(formData.startTime);
      const end = new Date(formData.endTime);
      if (start >= end) throw new Error('Horário final deve ser após o inicial');

      // Dados da reserva
      const reservation = {
        room_id: selectedRoom.id,
        user_name: formData.name,
        start_time: formData.startTime,
        end_time: formData.endTime
      };

      // Envia para o backend
      const response = await fetch('/reservations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(reservation)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao reservar');
      }

      // Atualiza a lista de salas
      await loadRooms();
      
      // Limpa e volta para a lista
      setFormData({ name: '', startTime: '', endTime: '' });
      setView('list');
      
      alert('Reserva realizada com sucesso!');
    } catch (error) {
      console.error('Erro na reserva:', error);
      alert(error instanceof Error ? error.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  };

    if (loading && view === 'list') {
    return (
      <Container>
        <MainContent>
          <Header>Salas de Estudo</Header>
          <LoadingIndicator>
            <Clock size={32} />
          </LoadingIndicator>
        </MainContent>
      </Container>
    );
  }

  return (
    <Container>
      <MainContent>
        <Header>Salas de Estudo</Header>
        
        {view === 'list' ? (
          <RoomListContainer>
            {rooms.map(room => (
              <RoomCard
                key={room.id}
                $available={room.available}
                onClick={() => handleBookRoom(room)}
              >
                <RoomImage>{room.name.charAt(0)}</RoomImage>
                <RoomTitle>{room.name}</RoomTitle>
                <RoomMeta>
                  <User size={16} /> {room.capacity} pessoas
                </RoomMeta>
                <AvailabilityBadge $available={room.available}>
                  {room.available ? 'Disponível' : 'Indisponível'}
                </AvailabilityBadge>
                <BookButton
                  $available={room.available}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleBookRoom(room);
                  }}
                >
                  <Calendar size={16} /> Reservar
                </BookButton>
              </RoomCard>
            ))}
          </RoomListContainer>
        ) : (
          <FormContainer>
            <FormHeader>
              <ActionButton onClick={() => setView('list')}>
                <ArrowLeft size={18} />
              </ActionButton>
              <FormTitle>Reservar {selectedRoom?.name}</FormTitle>
            </FormHeader>
            
            <form onSubmit={handleSubmit}>
              <FormGroup>
                <FormLabel>Seu Nome</FormLabel>
                <FormInput
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="Digite seu nome"
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <FormLabel>Data e Horário de Início</FormLabel>
                <FormInput
                  type="datetime-local"
                  name="startTime"
                  value={formData.startTime}
                  onChange={handleInputChange}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <FormLabel>Data e Horário de Término</FormLabel>
                <FormInput
                  type="datetime-local"
                  name="endTime"
                  value={formData.endTime}
                  onChange={handleInputChange}
                  required
                  min={formData.startTime}
                />
              </FormGroup>
              
              <FormActions>
                <ActionButton type="button" onClick={() => setView('list')}>
                  <ArrowLeft size={16} /> Voltar
                </ActionButton>
                <ActionButton $primary type="submit" disabled={loading}>
                  {loading ? (
                    <>
                      <Clock size={16} /> Processando...
                    </>
                  ) : (
                    <>
                      <Check size={16} /> Confirmar Reserva
                    </>
                  )}
                </ActionButton>
              </FormActions>
            </form>
          </FormContainer>
        )}
      </MainContent>
    </Container>
  );
}
