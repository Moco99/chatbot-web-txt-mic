import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_firestore import FirestoreChatMessageHistory
from google.cloud import firestore
from langchain.schema import SystemMessage
from voice_app import procesar_audio, crear_audio

load_dotenv()

app = Flask(__name__)

# CORS simplificado - permite todo desde 127.0.0.1:5500
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5500')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# config de firebase
PROJECT_ID = os.getenv("PROJECT_ID")
SESSION_ID = "chat-session"
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

cliente = firestore.Client(project=PROJECT_ID)

# chat history
chat_history = FirestoreChatMessageHistory(
    session_id=SESSION_ID,
    collection=COLLECTION_NAME,
    client=cliente,
)

# Modelo
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# prompt de nuestro chatbot
system_prompt = """
                Eres un asistente conversacional llamado Isac.
                Eres un especialista en las siguientes areas:
                - Programación
                - Ingeniería
                - Matemáticas
                - Física
                - Química
                - Biología
                - Geología
                - Historia
                - Geografía
                - Arte
                - Lenguajes
                - Ciencias sociales
                - Ciencias naturales
                - Tecnología
                - Economía
                - Negocios
                Tu personalidad es relajada, amable y técnica, intenta no dar siempre la misma respuesta.
                Responde siempre con claridad y sin inventar información.
                Si no sabes algo simplemente contesta "no se".
                Siempre responde en español latino.
                A menos que se requiera una respuesta mas larga tus respuestas deben ser cortas y concisas, se considera respuesta larga aquella con mas de 20 palabras.
                Casos en los que una respuesta deberia ser corta:
                1. Si solo es un saludo.
                2. Si solo es un saludo y una pregunta.
                3. Si solo es una pregunta (la cual la respuesta no sea demasiado larga). ejemplo: ¿En que año inicio la segunda guerra mundial?
                """

# endpoint principal
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    print("=" * 50)
    print("INICIANDO PROCESAMIENTO DE MENSAJE")
    print("=" * 50)

    data = request.get_json()
    msg_user = data.get("message", "").strip()
    print(f"- Mensaje del usuario: {msg_user}")
    print(f"- Longitud del mensaje: {len(msg_user)}")

    if not msg_user:
        print("ERROR! Mensaje vacio!")
        return jsonify({"response": "Mensaje vacío"}), 400
    
    # invocamos al modelo y le pasamos el historial
    chat_history.add_user_message(msg_user)
    print("- Agregando mensaje al historial")
    messages_andp_prompt = [SystemMessage(content=system_prompt)] + chat_history.messages
    print("- Invocando modelo...")
    
    try:
        modelo_respuesta = model.invoke(messages_andp_prompt)
        print("- Obteniendo respuesta del modelo...")
        chat_history.add_ai_message(modelo_respuesta.content)
        print(f"- Respuesta de ISAC: {modelo_respuesta.content}")
        print("=" * 50)
        print("ISAC HA CONTESTADO EL MENSAJE")
        print("=" * 50)
        return jsonify({"response": modelo_respuesta.content})
    except Exception as e:
        print(f"- Error: {e}")
        return jsonify({"error": str(e)}), 500

# endpoint del modo de voz
@app.route("/voice", methods=["POST", "OPTIONS"])
def voice():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    if "file" not in request.files:
        return jsonify({"error": "No se encontró el archivo de audio"}), 400
    
    file = request.files["file"]

    try:
        texto_procesado = procesar_audio(file)
        
        if not texto_procesado:
            return jsonify({"error": "No se pudo transcribir el audio"}), 400
        
        chat_history.add_user_message(texto_procesado)
        messages_andp_prompt = [SystemMessage(content=system_prompt)] + chat_history.messages
        modelo_respuesta = model.invoke(messages_andp_prompt)
        chat_history.add_ai_message(modelo_respuesta.content)

        audio_base64 = crear_audio(modelo_respuesta.content)

        return jsonify({
            "text": texto_procesado,
            "response": modelo_respuesta.content,
            "audio": audio_base64
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)