from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from config import Config
import os
import requests

# Configurações do Flask
app = Flask(__name__)
API_KEY = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
# Lista de origens permitidas para CORS
allowed_origins = [
    "http://viniciuscasseb.com",
    "https://viniciuscasseb.com/perguntar",
    "https://viniciuscasseb.com/",
    "https://jolly-smoke-098e91f0f.4.azurestaticapps.net",
    "http://localhost:3000",
    "http://localhost",
]

CORS(app, resources={r"/*": {"origins": allowed_origins}})


# Função para verificar se a origem da requisição é permitida
def verificar_origem_permitida():
    origem = request.headers.get("Origin") or request.headers.get("Referer")
    if not origem:
        return False  # Bloqueia requisições sem cabeçalho de origem
    return any(o in origem for o in allowed_origins)


# Função para validar se a pergunta está no escopo de Justiça e Tribunais
def validar_pergunta(pergunta):
    palavras_chave = ["processo", "justiça", "tribunal", "ação", "sentença", "juiz", "jurisdição"]
    return any(palavra in pergunta for palavra in palavras_chave)


# Função para gerar resposta com GPT
def gerar_resposta(pergunta):
    if not validar_pergunta(pergunta):
        return "Só posso responder perguntas relacionadas à Justiça e Tribunais Federais/Estaduais."

    content = """
    ## Informações sobre processos judiciais
        Use as informações abaixo para fornecer uma resposta precisa. Você pode receber mais de um contexto.  
        Você só pode responder perguntas relacionadas à Justiça e Tribunais Federais/Estaduais.  
        Se o contexto fornecido não contiver informações relevantes, peça educadamente mais detalhes ao usuário.  
        Se a pergunta não for sobre esse tema, responda informando que só pode fornecer informações sobre Justiça e Tribunais.  
        Não invente informações nem forneça respostas especulativas.  
    """

    conten2 = f"### Pergunta do Usuário:\n{pergunta}\n\n### Instruções:\n- Se o contexto tiver informações relevantes, responda de forma clara e objetiva, podendo usar emojis e tópicos.\n- Se o contexto for fraco ou irrelevante, peça esclarecimentos ao usuário. Exemplo: 'Não encontrei detalhes suficientes sobre isso. Poderia fornecer mais informações?'\n- Se a pergunta não for sobre Justiça ou Tribunais, informe educadamente que só responde sobre esse tema."

    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": conten2},
            ],
        )
        return resposta.choices[0].message.content
    except Exception as e:
        print(f"Erro ao chamar OpenAI: {e}")
        return "Erro ao gerar resposta."


# Função para consultar processos no DataJud
def consultar_processo(tribunal, numero_processo):
    url = f"https://api-publica.datajud.cnj.jus.br/{tribunal}/processo/{numero_processo}"
    
    headers = {
        "Authorization": f"APIKey {API_KEY}",  # Adiciona a API Key no cabeçalho
        "Content-Type": "application/json"
    }
    
    try:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            return resposta.json()
        elif resposta.status_code == 401:
            return {"error": "Acesso negado à API do DataJud. Verifique sua chave de API."}, 401
        else:
            return {"error": "Processo não encontrado ou erro na API do DataJud."}, resposta.status_code
    except Exception as e:
        return {"error": f"Erro ao consultar o processo: {e}"}, 500

# Rota de teste para verificar status
@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "app_online_v5"})


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


# Rota para consulta de processos judiciais
@app.route("/processo/", methods=["POST"])
def obter_processo():
    print("Headers recebidos:", request.headers)
    print("Body recebido:", request.json)

    data = request.json
    tribunal = data.get("tribunal", "").strip().lower()
    numero_processo = data.get("numero_processo", "").strip()

    if not tribunal or not numero_processo:
        return jsonify({"error": "Tribunal e número do processo são obrigatórios."}), 400

    resultado = consultar_processo(tribunal, numero_processo)
    return jsonify(resultado)


# Iniciar o aplicativo Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
