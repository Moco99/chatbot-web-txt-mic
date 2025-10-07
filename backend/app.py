"""
en caso de instalar otra paqueteria usar pip install 'nueva-paqueteria'
                                         pip freeze > backend/requirements.txt
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_firestore import FirestoreChatMessageHistory
from google.cloud import firestore


load_dotenv()

#firebase
PROJECT_ID = os.getenv("PROJECT_ID")
SESSION_ID = os.getenv("SESSION_ID")
COLLECTION_NAME = os.getenv("COLLECTION_NAME") 

#conexion a firestone
cliente = firestore.Client(project=PROJECT_ID)

chat_history = FirestoreChatMessageHistory(
    session_id=SESSION_ID,
    collection=COLLECTION_NAME,
    client=cliente,
)


#definimos el modelo
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)