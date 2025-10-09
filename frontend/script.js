const btnEnviar = document.getElementById('btn');
const btnVoz = document.getElementById('btn-voz');
const input = document.getElementById('input');
const messages = document.getElementById('messages');

async function enviarMensaje() {
    const texto = input.value.trim();
    if(!texto) return;

    //aca se muestra el mensaje del usuario en la UI
    const msg = document.createElement('div');
    msg.className = 'msg user';
    msg.textContent = texto;
    messages.appendChild(msg);
    input.value = '';
    messages.scrollTop = messages.scrollHeight;

    //se envia el msj al backend (python con flask)
    try {
        const res = await fetch("http://127.0.0.1:5000/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: texto })
        });

        const data = await res.json();
        //modelMessage.innerHTML = marked.parse(mensaje); es para darle formato a los mensajes y que se vea bonito para el usuario
        if (data.response) {
            const modelMsg = document.createElement('div');
            modelMsg.className = "msg bot";
            modelMsg.innerHTML = marked.parse(data.response);
            messages.appendChild(modelMsg);
            messages.scrollTop = messages.scrollHeight;
        }
    } catch (err) {
        console.error("Error al enviar mensaje:", err);
    }
};

btnEnviar.addEventListener('click', enviarMensaje);
input.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault(); // evita salto de línea
        enviarMensaje();
    }
});