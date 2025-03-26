from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
import faiss
from openai import OpenAI
from config import Config
import os
import pandas as pd
from azure.storage.blob import BlobServiceClient
from io import BytesIO

# Configurações do Azure Blob Storage
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
BLOB_CONTAINER_NAME = "mylocalfiles"

# Arquivos
BLOB_CHATBOTDATA = "chatbotdata.xlsx"
BLOB_LOGS = "logs.xlsx"

# Função para carregar o Excel diretamente do Blob


# Função para adicionar linha ao Excel no Blob Storage


# Inicializa o Flask
app = Flask(__name__)
# Permite CORS apenas para as origens especificadas
allowed_origins = [
    "http://viniciuscasseb.com",
    "https://viniciuscasseb.com/perguntar",
    "https://viniciuscasseb.com/",
    "https://viniciuscasseb.com/perguntar/",
    "https://viniciuscasseb.com",
    "https://jolly-smoke-098e91f0f.4.azurestaticapps.net",
    "http://localhost:3000",
    "http://localhost",
]

CORS(app, resources={r"/*": {"origins": allowed_origins}})









# Função para gerar resposta com GPT
def gerar_resposta(pergunta):
    content = \
    """
    ##vamos mudar para algo relacionado ao processo
        Use the tag and content below to provide an accurate response, you can receive more than one.
        You are only allowed to answer questions about Vini/Vinicius/Casseb.  
        If the provided context does not have relevant information, politely ask the user for more details.  
        If the user asks something outside this scope, respond humorously by saying that you are an AI and just a bunch of mathematical calculations.
        Do not use "Vini/Vinicius/Casseb" to ask the message.  
    """

    conten2 = f"### Contexts:\n{contexto}\n\n### User Question:\n{pergunta}\n\n### Instructions:\n- If the context has relevant information, answer naturally, clearly, you can use emojis and separate by topics.\n- If the context is weak or irrelevant, ask the user for clarification. Example: 'I couldn't find relevant details about this. Could you provide more context?'\n- If the question is outside the allowed topics, use a fun, AI-related response."
    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": content
                },
                {
                    "role": "user", 
                    "content": conten2
                }
            ]
        )
        return resposta.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar OpenAI: {e}")
        return "Erro ao gerar resposta."

# Função para verificar a origem da requisição
def verificar_origem_permitida():
    origem = request.headers.get('Origin') or request.headers.get('Referer')
    if not origem:
        return False  # Bloqueia requisições sem cabeçalho de origem
    if 'jolly-smoke-098e91f0f.4.azurestaticapps.net' in origem or 'localhost' in origem or 'viniciuscasseb.com' in origem:
        return True
    return False

# Rota de teste para verificar status
@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "app_online_v4"})



# Rota para perguntas
@app.route("/perguntar/", methods=["POST"])
def perguntar():
    if not verificar_origem_permitida():
        return jsonify({"error": "Origem não permitida"}), 403

    data = request.json
    pergunta = data.get("pergunta", "").strip().lower()
    if not pergunta:
        return jsonify({"error": "Pergunta vazia"}), 400
    
    
    resposta = gerar_resposta(pergunta)

   
    
    return jsonify({"resposta": resposta})

# Rota para receber os dados e adicionar ao Excel


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))