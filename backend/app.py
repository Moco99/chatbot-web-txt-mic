import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS 
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_firestore import FirestoreChatMessageHistory
from google.cloud import firestore


load_dotenv()

app = Flask(__name__)
CORS(app)

# config de firebase
PROJECT_ID = os.getenv("PROJECT_ID")
SESSION_ID = os.getenv("SESSION_ID")
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
        # Preflight del navegador 
        response = make_response()
        return add_cors_headers(response)

    data = request.get_json()
    msg_user = data.get("message", "").strip()

    if not msg_user: #manejo de mensajes vacios
        return jsonify({"response": "Mensaje vacío"}), 400

    #invocamos al modelo y le pasamos el historial
    chat_history.add_user_message(msg_user)
    modelo_respuesta = model.invoke(chat_history.messages)
    chat_history.add_ai_message(modelo_respuesta.content)

    respuesta = jsonify({"response": modelo_respuesta.content})
    return add_cors_headers(respuesta) #devolvemos la respuesta


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
