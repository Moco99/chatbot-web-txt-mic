const btnConversation = document.getElementById('microfono');
const btnVolver = document.getElementById('btn-volver');
const textoCapturado = document.getElementById('texto-capturado');

//configuracion de webSpeech y controlamos activacion de la grabacion
let grabacion = false;
let recognition = new SpeechRecognition();
let textoFinal = "";

recognition.lang = "es-MX";
recognition.continuos = true;
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

function iniciarConversacion(){
    console.log("conversacion iniciada con exito");
    grabacion = !grabacion;
    console.log(grabacion);
    btnConversation.classList.toggle("grabando");
    if(!grabacion){
        recognition.stop();
        document.getElementById("texto-capturado").innerText = "procesando...";
    }else{
        recognition.start();
    }
};
btnConversation.addEventListener('click', iniciarConversacion);


//volver al chat con isac
function volver(){
    window.location.href = "index.html";
};
btnVolver.addEventListener('click', volver);