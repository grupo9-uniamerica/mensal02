"use client";

import { useRef, useEffect } from "react"; // Adicione useRef e useEffect
import { useState } from "react";
import styled from "styled-components";
import { Send } from "lucide-react";

const SuggestionsContainer = styled.div`
  display: flex;
  flex-direction: column; /* Organiza as sugestões em uma coluna */
  align-items: flex-end; /* Alinha as sugestões à esquerda */
  position: absolute; /* Alinha as sugestões dentro da posição relativa do input */
  bottom: 60px; /* Distância do fundo do input (ajuste conforme necessário) */
  left: 0; /* Alinha as sugestões à esquerda do container do input */
  width: 100%; /* Ocupa toda a largura do container */
  animation: fadeIn 0.4s ease-in-out forwards;
  
  @media (max-width: 768px) {
    font-size: 0.7rem;
  }
`;

const SuggestionBubble = styled.div`

  padding: 8px 12px;

  color: white;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s, transform 0.2s;
  margin-bottom: 8px; /* Distância entre as sugestões */
  background-color: rgba(0, 132, 255, 0.3); /* Use background-color em vez de background */
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);


  &:hover {
    background-color: #2563eb;
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.95);
  }
`;


// Estilos com Styled Components
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
  overflow: hidden; /* Evita overflow no layout */
  height: 100vh;

  @media (min-width: 768px) {
    padding-left: clamp(20px, 20vw, 600px);
    padding-right: clamp(20px, 20vw, 600px);
  }

  
`;

const Header = styled.div`
  padding: 0.3rem;
  text-align: center;
  font-weight: bold;
  font-size: 1.0rem;

  @media (min-width: 768px) {
    padding: 1.5rem;
    font-size: 1.5rem;
  }
`;

const ChatContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding-left: 1rem;
  padding-right: 1rem;
  padding-bottom: 120px; /* Reduz o padding-bottom para telas menores */
  display: flex;
  flex-direction: column;

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

const Message = styled.div<{ $isUser: boolean }>`
  max-width: 100%;
  padding: 12px 16px;
  border-radius: ${({ $isUser }) => ($isUser ? "12px 12px 0 12px" : "12px 12px 12px 0")};
  background: ${({ $isUser }) => $isUser && "linear-gradient(135deg, #3182ce, #2563eb)"};
  color: white;
  align-self: ${({ $isUser }) => ($isUser ? "flex-end" : "flex-start")};
  margin-bottom: 12px;
  transition: transform 0.2s, box-shadow 0.2s;
  color: #f2ddcc;
  
  /* Adicionando animação de fade-in */
  opacity: 0;
  animation: fadeIn 0.4s ease-in-out forwards;

  &:hover {
    transform: translateY(-2px);
    background: linear-gradient(135deg, #0c101c,rgb(18, 24, 41));
  }

  @media (max-width: 768px) {
    font-size: 0.8rem;
  }

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


const InputContainer = styled.div`
  display: flex;
  align-items: center;
  padding: 1rem;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  box-shadow: 0px 40px 40px 0px rgba(0, 0, 0, 0.2);
  background-color: #171e32;
  position: absolute; /* Permite posicionar com relação à tela */
  bottom: 2%; /* Distância do fundo da tela, ajustável */
  left: 50%; /* Centraliza horizontalmente */
  transform: translateX(-50%); /* Ajusta a posição para o centro */
  width: 40%;
  border-radius: 25px;
  border: 1px solid rgba(255, 255, 255, 0.1);

  @media (max-width: 768px) { 
    width: 90%; /* Reduz a largura para telas menores */
    bottom: 0.1%; /* Distância do fundo da tela, ajustável */
  }
`;


const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border-radius: 20px;
  outline: none;
  color: #2d3748;
  background-color: #101524;
  border-color: #101524;
  color: #e2e8f0;
  &::placeholder {
    color: #718096;
  }
`;


const Button = styled.button`
  margin-left: 1rem;
  padding: 0.75rem;
  background:  #2563eb;
  cursor: pointer;
  border: none;
  border-radius: 12px;
  transition: background 0.3s, transform 0.2s;
  backdrop-filter: blur(5px);

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.05);
  }

  &:active {
    transform: scale(0.95);
  }
`;

const LoadingMessage = styled.div`
  max-width: 60%;
  padding: 12px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1a202c, #2d3748);
  color: white;
  align-self: flex-start;
  margin-bottom: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
  animation: colorChange 0.9s infinite alternate, fadeIn 0.5s ease-in-out;

@keyframes colorChange {
  0% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(45, 55, 72));
  }
  5% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(48, 63, 85));
  }
  10% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(51, 70, 97));
  }
  15% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(55, 77, 108));
  }
  20% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(58, 84, 120));
  }
  25% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(61, 91, 132));
  }
  30% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(64, 98, 143));
  }
  35% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(67, 105, 154));
  }
  40% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(72, 112, 166));
  }
  45% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(75, 119, 178));
  }
  50% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(78, 126, 190));
  }
  55% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(81, 133, 201));
  }
  60% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(84, 140, 213));
  }
  65% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(87, 147, 225));
  }
  70% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(92, 154, 237));
  }
  75% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(95, 161, 248));
  }
  80% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(95, 161, 248));
  }
  85% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(95, 161, 248));
  }
  90% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(95, 161, 248));
  }
  95% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(95, 161, 248));
  }
  100% {
    background: linear-gradient(135deg, rgb(26, 32, 44), rgb(95, 161, 248));
  }
}





  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
`;


// Função para formatar a mensagem
const formatMessage = (message: string) => {
  // Substituir **texto** por <strong>texto</strong>
  let formattedMessage = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // Substituir ### por listas e adicionar <br> antes e depois
  formattedMessage = formattedMessage.replace(/### (.*?)\n/g, '<br><ul><li>$1</li></ul><br>');

  // Dividir o texto em linhas
  const lines = formattedMessage.split('\n');

  // Processar cada linha
  formattedMessage = lines.map((line, index) => {
    // Verificar se é a penúltima linha
    if (index === lines.length - 2) {
      return `<p>${line}</p><br>`; // Adiciona <br> no final da penúltima linha
    }

    // Adicionar <p> ao redor de outras linhas (exceto títulos e negrito)
    if (!line.startsWith('<ul>') && !line.startsWith('<strong>') && line.trim() !== '') {
      return `<p>${line}</p>`;
    }

    return line;
  }).join('');

  return formattedMessage;
};

let firstmessage = true;

function generateuserid() {
  return 'user-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

const userid = generateuserid();
console.log(userid);
// Garantir que o localStorage está acessível antes de usá-lo
if (typeof window !== "undefined" && window.localStorage) {
  localStorage.setItem('userid', userid);
}
//  Componente Principal do Chatbot
export default function Chatbot() {
  const [messages, setMessages] = useState<{ text: string; isUser: boolean }[]>([
    { text: "Hello! Before we get started, can you tell me your name or which company you're from?", isUser: false },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([
    "Summary of Vinicius",
    "What certifications does Vinicius have?",
    "About Vinicius",
    "How old is Vinicius?",
    "Tell me about graduation of Vinicius?",
    "What is vinicius's email?",
    "Which company does Vinicius work for?",
    "Tell me about experience projects of Vinicius?",
    "What hard skills does Vinicius have?",
    "Vinicius' hobbies?",
    "Vinicius' job role?",
    "Which languages does Vinicius speak?",
    "Where does Vinicius live?",
    "Full name of Vinicius?",
    "Where is Vinicius from?",
    "Vinicius' salary expectations?",
    "Has Vinicius ever worked with data streams?",
    "Tell me about this chatbot",
    "Who are you?",
  ]);
  
  const [showSuggestions, setShowSuggestions] = useState(false); // Estado para controlar a exibição das sugestões
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Efeito para rolar automaticamente para o final
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async (message?: string) => {
    const msg = message || input;
    if (!msg.trim() || isLoading) return;

    const currentTime = new Date();
    const formattedTime = currentTime.toISOString();

    const userMessage = { text: msg, isUser: true };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");



    if (firstmessage) {
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        const botMessage = { text: 'Thank you! Now you can start by asking anything about Vini, such as his age, current projects, job, and more! 😊', isUser: false };
        setMessages((prev) => [...prev, botMessage]);
        setShowSuggestions(true); // Exibe as sugestões após a primeira mensagem
      }, 1500);
      if (typeof window !== "undefined" && window.localStorage) {
      localStorage.setItem('dtsent', formattedTime);
      localStorage.setItem('message', msg);
      localStorage.setItem('flag_fm', "true");
      localStorage.setItem('input_ai', "");
      localStorage.setItem('contexto_faiss', "");
      }
      firstmessage = false;
    } else {

      try {
        setIsLoading(true);
        setShowSuggestions(false);
        const response = await fetch('https://privatechatbotia-dpbye3cdbmandchy.brazilsouth-01.azurewebsites.net/perguntar/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ pergunta: msg }),
        });

        if (!response.ok) throw new Error('Erro ao enviar mensagem');

        const data = await response.json();
        const botMessage = { text: data.resposta, isUser: false };

        setShowSuggestions(true);
        console.log(botMessage);
        if (typeof window !== "undefined" && window.localStorage) {
        localStorage.setItem('dtsent', formattedTime);
        localStorage.setItem('message', msg);
        localStorage.setItem('flag_fm', "false");
        localStorage.setItem('input_ai', data.resposta);
        localStorage.setItem('contexto_faiss', data.contexto);
        }
        setMessages((prev) => [...prev, botMessage]);
                      // Se a mensagem do usuário mencionar "LinkedIn", envie a imagem clicável
      if (msg.toLowerCase().includes("linkedin")) {
        const botMessage = {
          text: `<a href="https://www.linkedin.com/in/vinicius-cezar-casseb-a1b803189/" target="_blank" style="background: none !important; border: none !important; padding: 0 !important; display: inline-block;">
                  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/LinkedIn_icon.svg/2048px-LinkedIn_icon.svg.png" alt="LinkedIn" width="50" height="50" style="max-width: 50px; height: auto; background: none !important; border: none !important; padding: 0 !important;"/>
                </a>`,
          isUser: false,
        };
        setMessages((prev) => [...prev, botMessage]);
      }
      } catch (error) {
        console.error('Erro ao enviar mensagem:', error);
        const errorMessage = { text: 'Sorry, something is wrong :/', isUser: false };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }

    // Send to logs
    try {
      if (typeof window !== "undefined" && window.localStorage) {
      const dtsent = localStorage.getItem('dtsent');
      const message = localStorage.getItem('message');
      const flag_fm = localStorage.getItem('flag_fm');
      const input_ai = localStorage.getItem('input_ai');
      const context_faiss = localStorage.getItem('contexto_faiss');
      const userid = localStorage.getItem('userid');

      fetch('https://privatechatbotia-dpbye3cdbmandchy.brazilsouth-01.azurewebsites.net/sentdata/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dtsent,
          message,
          flag_fm,
          input_ai,
          context_faiss,
          userid
        }),
      })
        .then(response => {
          if (!response.ok) {
            throw new Error('Erro ao enviar mensagem');
          }
          return response.json();
        })
        .then(data => {
          console.log('Dados enviados com sucesso:', data);
        })
        .catch(error => {
          console.error('Erro ao enviar dados:', error);
        });
    }} catch (error) {
      console.error('Erro inesperado:', error);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion); // Envia a sugestão como mensagem
    setSuggestions((prev) => prev.filter((s) => s !== suggestion)); // Remove a sugestão usada
  };

  return (
    <Container>
      <MainContent>
        <Header>Vini AI Assistant</Header>
        <ChatContainer ref={chatContainerRef}>
          {messages.map((msg, index) => (
            <Message key={index} $isUser={msg.isUser}>
              <div dangerouslySetInnerHTML={{ __html: formatMessage(msg.text) }} />
            </Message>
          ))}
          {isLoading && <LoadingMessage>Thinking</LoadingMessage>}
        </ChatContainer>

        <InputContainer>
                {/* Exibe as sugestões apenas se showSuggestions for true */}
                {showSuggestions && suggestions.length > 0 && (
          <SuggestionsContainer>
            <SuggestionBubble onClick={() => handleSuggestionClick(suggestions[0])}>
              {suggestions[0]}
            </SuggestionBubble>
          </SuggestionsContainer>
        )}
          <Input
            type="text"
            placeholder="Type your message"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          />
          <Button onClick={() => sendMessage()}>
            <Send size={20} color="white" />
          </Button>
        </InputContainer>
      </MainContent>
    </Container>
  );
}