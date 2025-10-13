const btnConversation = document.getElementById('microfono');
const btnVolver = document.getElementById('btn-volver');
const textoCapturado = document.getElementById('texto-capturado');

//configuracion de webSpeech y controlamos activacion de la grabacion
let grabacion = false;
let recognition = new SpeechRecognition();
let textoFinal = "";
let mediaRecorder;
let chunks = [];

recognition.lang = "es-MX";
recognition.continuous = true;
recognition.interimResults = true;

recognition.onresult = (event)=>{
    let textoInter = "";
//solo procesa los resultados nuevos o actualizados desde resultIndex hasta el final para evitar el duplicado de texto o mezclar resultados nuevos con viejos
    for (let i = event.resultIndex; i < event.results.length; ++i){ 
        if(event.results[i].isFinal){
            // si es final se agrega el texto al texto final que se mandara al backend
            textoFinal += event.results[i][0].transcript;   
        }else{
            //de no serlo simplemente se agrega al texto intermedio
            textoInter += event.results[i][0].transcript;
        }
    }
    //se va actualizando el texto capturado para mostrarlo en la UI
    document.getElementById("texto-capturado").innerText = textoFinal + textoInter;
}


async function iniciarConversacion(){
    console.log("conversacion iniciada con exito");
    grabacion = !grabacion;
    console.log(grabacion);
    btnConversation.classList.toggle("grabando");
    if(!grabacion){
        recognition.stop();
        document.getElementById("texto-capturado").innerText = "procesando...";
        mediaRecorder.stop();
    }else{
        try{
            textoFinal = "";
            recognition.start();
            const stream = await navigator.mediaDevices.getUserMedia({audio:true});
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            chunks = [];

            mediaRecorder.ondataavailable = (e)=>{
            chunks.push(e.data);
            }

            mediaRecorder.onstop = async ()=>{
            const blob = new Blob(chunks,{type: chunks[0]?.type || "audio/webm"}); 
            stream.getTracks().forEach(track => track.stop()); //liberamos el micro despues de grabar
            await enviarAudio(blob);
            }
        }catch(err){
            console.error("error al iniciar grabacion ",err);
            textoCapturado.innerText = "Error! Permite el acceso a tu microfono";
        }
    }
};
//enviamos el audio al backend al terminar la grabacion
async function enviarAudio(blob){
    try{
        let dataForm = new FormData();
        dataForm.append("file",blob,"audio.webm");

        let res = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            body : dataForm
        });
        const data = await res.json();
        console.log(data.text);
        textoCapturado.innerText = data.text;
    }catch(err){
        console.error("error al enviar audio ",err);
        textoCapturado.innerText = "Error al enviar audio";
    }
    
};

btnConversation.addEventListener('click', iniciarConversacion);


//volver al chat con isac
function volver(){
    window.location.href = "index.html";
};
btnVolver.addEventListener('click', volver);