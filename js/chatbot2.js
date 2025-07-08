async function sendMessage(message) {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, model: 'llama3' })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let result = '';

    const chatbox = document.getElementById('chatbox');
    chatbox.innerHTML += '<div class="ai-msg"><span id="streaming">...</span></div>';
    const streamEl = document.getElementById('streaming');

    while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        result += chunk;
        streamEl.textContent = result;
    }

    streamEl.removeAttribute('id');
}
