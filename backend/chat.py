import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_firestore import FirestoreChatMessageHistory
from google.cloud import firestore
from langchain.schema import SystemMessage
from voice_app import procesar_audio

load_dotenv()

app = Flask(__name__)
CORS(app)

# config de firebase
PROJECT_ID = os.getenv("PROJECT_ID")
SESSION_ID = "chat-session"
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

cliente = firestore.Client(project=PROJECT_ID)


#chat history
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

#prompt de nuestro chatbot, lo pondre publico porque tampoco es la gran cosa
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

#agregamos headers cors a todas las respuestas (si no da error)
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:5500"
    response.headers["Access-Control-Allow-Credentials"] = "true" #indica que el fron puede incluir cookies o headers de autorizacion
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization" #lista los header que el front puede enviar
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS" #lista de los metodos que el front puede usar
    return response


#nos aseguramos que despues de cada solicitud la funcion se ejecute para añadir las header cors a la respuesta (tenga exito o falle)
@app.after_request
def after_request_func(response):
    return add_cors_headers(response)

#endpoint principal aca
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        # preflight del navegador 
        response = make_response()
        return add_cors_headers(response)
    data = request.get_json()
    msg_user = data.get("message", "").strip()

    if not msg_user: #manejo de mensajes vacios
        return jsonify({"response": "Mensaje vacío"}), 400

    #invocamos al modelo y le pasamos el historial
    chat_history.add_user_message(msg_user)
    messages_andp_prompt = [SystemMessage(content=system_prompt)]+ chat_history.messages # agregamos el prompt al historial para mantenerlo
    modelo_respuesta = model.invoke(messages_andp_prompt)
    chat_history.add_ai_message(modelo_respuesta.content)

    respuesta = jsonify({"response": modelo_respuesta.content})
    return add_cors_headers(respuesta) #devolvemos la respuesta

#endpoint del modo de voz
@app.route("/voice",methods=["POST", "OPTIONS"])
def voice():
    if request.method == "OPTIONS":
        # preflight del navegador 
        response = make_response()
        return add_cors_headers(response)
    
    if "file" not in request.files:
        return jsonify({"error": "No se encontro el archivo de audio"}), 400
    
    file = request.files["file"]

    try:
        #procesamos el audio recibido del frontend
        texto_procesado = procesar_audio(file)
        #agregar el texto procesado al historial y pasarselo al modelo para obtener una respuesta
        chat_history.add_ai_message(texto_procesado)
        messages_andp_prompt = [SystemMessage(content=system_prompt)]+ chat_history.messages # agregamos el prompt al historial para mantenerlo
        modelo_respuesta = model.invoke(messages_andp_prompt)
        chat_history.add_ai_message(modelo_respuesta.content)

        return jsonify({"text":texto_procesado,"response":modelo_respuesta.content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
