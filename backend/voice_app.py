import os
from dotenv import load_dotenv
import tempfile
import requests 

load_dotenv()
hugging_token = os.getenv("HUGGING_TOKEN")
model = "openai/whisper-large-v3"

def procesar_audio(file):
    with tempfile.NamedTemporaryFile(delete=False,suffix=".webm") as temp:
        file.save(temp.name)
        temp_path = temp.name

        with open(temp_path,"rb") as data:
            res = requests.post(f"https://api-inference.huggingface.co/models/{model}",
                                headers={"Authorization": f"Bearer {hugging_token}"},
                                data=data
                                )
            result = res.json()
        os.remove(temp_path)
        return result.get("text","")
    
        



