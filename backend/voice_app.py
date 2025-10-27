import os
from dotenv import load_dotenv
import tempfile
import requests
import time
import base64
from google.cloud import texttospeech

load_dotenv()
hugging_token = os.getenv("HUGGING_TOKEN")
modelSTT = "openai/whisper-large-v3"
#modelTTS = "suno/bark"
"""
tuve que agregarle muchas cosas a esta parte porque el debug se me hacia mas facil si veia por terminal como iba el proceso
"""
def procesar_audio(file):
    #para que en terminal se vea bonito jaja
    print("=" * 50)
    print("INICIANDO PROCESAMIENTO DE AUDIO")
    print("=" * 50)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp:
        file.save(temp.name)
        temp_path = temp.name
        print(f"- Archivo temporal guardado como : {temp_path}")
    
    try:
        #verificando que el tamaño del archivo sea valido
        file_size = os.path.getsize(temp_path)
        print(f"- Tamaño del archivo: {file_size} bytes")
        
        if file_size == 0:
            print("ERROR!: El archivo está vacío")
            raise ValueError("El archivo de audio está vacío")
        
        if file_size < 5000:
            print("ADVERTENCIA: El archivo es muy pequeño (menos de 5KB)")
        
        #leemos el archivo
        with open(temp_path, "rb") as data:
            audio_data = data.read()
            print(f"- Audio leído: {len(audio_data)} bytes")
            print(f"-> Enviando a Whisper (modelo: {modelSTT})...")
            
            res = requests.post(
                f"https://api-inference.huggingface.co/models/{modelSTT}",
                headers={
                    "Authorization": f"Bearer {hugging_token}",
                    "Content-Type": "audio/webm"
                },
                data=audio_data,
                timeout=60
            )
            
            print(f"- Status code: {res.status_code}")
            
            #en caso de cold start (tener que esperar)
            if res.status_code == 503:
                result = res.json()
                print(f"Cargando modelo...")
                print(f"Respuesta: {result}")
                
                if "estimated_time" in result:
                    wait_time = min(result["estimated_time"], 30)
                    print(f"   Esperando {wait_time} segundos...")
                    time.sleep(wait_time + 2)
                    
                    #reintentamos con Content-Type
                    print("- Reintentando petición...")
                    res = requests.post(
                        f"https://api-inference.huggingface.co/models/{modelSTT}",
                        headers={
                            "Authorization": f"Bearer {hugging_token}",
                            "Content-Type": "audio/webm" 
                        },
                        data=audio_data,
                        timeout=60
                    )
                    print(f"- Nuevo status code: {res.status_code}")
            
            #verificamos si hubo error
            if res.status_code != 200:
                print(f"ERROR!: Status {res.status_code}")
                print(f"Respuesta: {res.text}")
                raise Exception(f"Error de API: {res.status_code} - {res.text}")
            
            #parsear respuesta
            result = res.json()
            print(f"- Respuesta JSON: {result}")
            
            #verificar si hay error en el resultado
            if "error" in result:
                print(f"ERROR! en resultado: {result['error']}")
                raise Exception(f"Error en transcripción: {result['error']}")
            
            #extraemos el texto
            texto = result.get("text", "").strip()
            print(f"- Texto transcrito: '{texto}'")
            print(f"- Longitud del texto: {len(texto)} caracteres")
            
            if not texto:
                print("ADVERTENCIA: Whisper retornó texto vacío")
                print(f"Respuesta completa: {result}")
            
            print("=" * 50)
            return texto
            
    #manejo de errores y excepciones
    except requests.exceptions.Timeout:
        print("ERROR!: Timeout al procesar el audio")
        raise Exception("Timeout al procesar el audio. El servicio tardó demasiado.")
    except requests.exceptions.RequestException as e:
        print(f"ERROR! de conexión: {str(e)}")
        raise Exception(f"Error de conexión: {str(e)}")
    except Exception as e:
        print(f"ERROR!: {str(e)}")
        raise Exception(f"Error al procesar audio: {str(e)}")
    finally:
        #eliminar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Archivo temporal eliminado")
            print("=" * 50)


def crear_audio(texto):
    """
    mostramos en terminal de flask como se hace el proceso en caso de necesitar depuracion en algun paso
    """
    print("="*50)
    print("INICIANDO PROCESAMIENTO DE AUDIO CON TTS")
    print("="*50)
    print(f"- Texto a transcribir: {texto}")
    print(f"- Longitud del texto: {len(texto)} caracteres")
    try:
        client = texttospeech.TextToSpeechClient()
        systhesis_input = texttospeech.SynthesisInput(text=texto)
        voice = texttospeech.VoiceSelectionParams(
            language_code="es-US",
            name="es-US-Studio-B"
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
        )
        #prints para debug
        print(f"Realizando solicitud de audio a google TTS...")
        response = client.synthesize_speech(input=systhesis_input, 
                                            voice=voice, 
                                            audio_config=audio_config
                                            )
        print("Audio generado y recibido de google")
        audio_bytes = response.audio_content
        print(f"Audio generado con longitud de {len(audio_bytes)} bytes")
        audio_64 = base64.b64encode(audio_bytes).decode("utf-8")
        print(f"Audio en base 64 con longitud de {len(audio_64)} caracteres codificado")
        print("="*50)
        return audio_64

    except Exception as e:
        print(f"ERROR! TTS: {str(e)}")
