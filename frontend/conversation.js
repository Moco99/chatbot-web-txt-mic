const btnConversation = document.getElementById('microfono');
const btnVolver = document.getElementById('btn-volver');

//controlar activacion de la grabacion
let grabacion = false;

function iniciarConversacion(){
    console.log("conversacion iniciada con exito");
    grabacion = !grabacion;
    console.log(grabacion);
    btnConversation.classList.toggle("grabando");
};
btnConversation.addEventListener('click', iniciarConversacion);


//volver al chat con isac
function volver(){
    window.location.href = "index.html";
};
btnVolver.addEventListener('click', volver);