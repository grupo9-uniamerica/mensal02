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
def carregar_excel_do_blob():
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=BLOB_CHATBOTDATA)

        stream = BytesIO(blob_client.download_blob().readall())
        return pd.read_excel(stream, sheet_name="pure_dataset")
    
    except Exception as e:
        print(f"Erro ao carregar Excel do Blob: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio caso haja erro

# Função para adicionar linha ao Excel no Blob Storage
def adicionar_linha_no_excel(nova_linha):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=BLOB_LOGS)

        try:
            # Baixa o arquivo existente
            stream = BytesIO(blob_client.download_blob().readall())
            existing_xls = pd.ExcelFile(stream)
            sheets = {sheet: existing_xls.parse(sheet) for sheet in existing_xls.sheet_names}
        except Exception:
            sheets = {}  # Se não existir, cria do zero

        # Atualiza a aba "logs" sem perder outras abas
        sheets["logs"] = pd.concat([sheets.get("logs", pd.DataFrame()), pd.DataFrame([nova_linha])], ignore_index=True)

        # Salva no Blob Storage
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet, data in sheets.items():
                data.to_excel(writer, sheet_name=sheet, index=False)
        output.seek(0)

        blob_client.upload_blob(output, overwrite=True)
    
    except Exception as e:
        print(f"Erro ao adicionar linha no Excel: {e}")

# Carrega o dataframe sem salvar o arquivo localmente
df = carregar_excel_do_blob()

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

# Modelo de embeddings
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

# Base de dados vetorial (FAISS)
dimension = 384
index = faiss.IndexFlatL2(dimension)

# Processamento dos dados
if not df.empty and "DATA" in df.columns:
    docs = df["DATA"].dropna().astype(str).tolist()
    docs = [doc.lower() for doc in docs]
else:
    docs = []

# Gera embeddings para os documentos e armazena no FAISS
if docs:
    doc_embeddings = embedding_model.encode(docs, convert_to_numpy=True)
    index.add(doc_embeddings)

# Função para buscar os documentos mais relevantes
def buscar_contexto(pergunta):
    if not docs:
        return "Problema ao executar o arquivo."

    pergunta_embedding = embedding_model.encode([pergunta], convert_to_numpy=True)
    _, indices = index.search(pergunta_embedding, k=min(3, len(docs)))  # Evita erro se docs for menor que 2
    return "\n".join([docs[i] for i in indices[0]])

# Função para gerar resposta com GPT
def gerar_resposta(pergunta, contexto):
    content = \
    """
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

# database
@app.route("/learningdatabase", methods=["GET"])
def database():
    return jsonify({"data": docs})

# Rota para perguntas
@app.route("/perguntar/", methods=["POST"])
def perguntar():
    if not verificar_origem_permitida():
        return jsonify({"error": "Origem não permitida"}), 403

    data = request.json
    pergunta = data.get("pergunta", "").strip().lower()
    if not pergunta:
        return jsonify({"error": "Pergunta vazia"}), 400
    
    contexto = buscar_contexto(pergunta)
    resposta = gerar_resposta(pergunta, contexto)

    print("Contexto: ", contexto)
    print("pergunta: ", pergunta)
    return jsonify({"resposta": resposta, "contexto": contexto})

# Rota para receber os dados e adicionar ao Excel
@app.route('/sentdata/', methods=['POST'])
def sentdata():
    if not verificar_origem_permitida():
        return jsonify({"error": "Origem não permitida"}), 403

    try:
        # Recebe os dados do frontend
        data = request.json

        # Coleta as colunas
        dtsent = data.get('dtsent')
        message = data.get('message')
        flag_fm = data.get('flag_fm')
        input_ai = data.get('input_ai')
        context_faiss = data.get('context_faiss')
        userid = data.get('userid')

        # Cria a nova linha com os dados recebidos
        nova_linha = {
            "dtsent": dtsent,
            "message": message,
            "flag_fm": flag_fm,
            "input_ai": input_ai,
            "context_faiss": context_faiss,
            "userid": userid
        }

        # Adiciona a nova linha ao Excel no Blob Storage
        adicionar_linha_no_excel(nova_linha)

        return jsonify({"message": "Dados salvos com sucesso"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))