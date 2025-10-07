const btnEnviar = document.getElementById('btn');
const btnVoz = document.getElementById('btn-voz');
const input = document.getElementById('input');
const messages = document.getElementById('messages');

function enviarMensaje(){
  const texto = input.value.trim();
  if (texto!=="") {
    const msg = document.createElement('div');
    msg.className = "msg user";
    msg.textContent = texto;
    messages.appendChild(msg);
    input.value = "";
    messages.scrollTop = messages.scrollHeight;
  }
};

btnEnviar.addEventListener('click', enviarMensaje);
input.addEventListener('keypress', (event) => {
  if (event.key === 'Enter') {
    event.preventDefault(); // evita salto de línea
    enviarMensaje();
  }
});