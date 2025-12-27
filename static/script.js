const promptInput = document.getElementById("prompt");
const conversationBox = document.getElementById("conversation");
const statusBox = document.getElementById("status");
const sendButton = document.getElementById("send-btn");

const conversation = [];

function renderConversation() {
    conversationBox.innerHTML = "";
    conversation.forEach((message) => {
        const row = document.createElement("div");
        row.className = `message ${message.role}`;

        const label = document.createElement("span");
        label.className = "label";
        label.textContent = message.role === "user" ? "Tú" : "Asistente";

        const bubble = document.createElement("p");
        bubble.textContent = message.content;

        row.appendChild(label);
        row.appendChild(bubble);
        conversationBox.appendChild(row);
    });
    conversationBox.scrollTop = conversationBox.scrollHeight;
}

function setStatus(text = "") {
    statusBox.textContent = text;
}

async function sendPrompt() {
    const content = promptInput.value.trim();
    if (!content) {
        return;
    }

    conversation.push({ role: "user", content });
    renderConversation();
    promptInput.value = "";
    setStatus("Pensando...");
    sendButton.disabled = true;

    try {
        const res = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: conversation }),
        });

        if (!res.ok) {
            throw new Error(`Error ${res.status}`);
        }

        const data = await res.json();
        const reply = data.response?.trim() || "(Sin respuesta)";
        conversation.push({ role: "assistant", content: reply });
        renderConversation();
        setStatus("");
    } catch (error) {
        setStatus("Ocurrió un error. Intenta nuevamente.");
    } finally {
        sendButton.disabled = false;
        promptInput.focus();
    }
}

promptInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendPrompt();
    }
});