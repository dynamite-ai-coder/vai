const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const statusBtn = document.getElementById('statusBtn');
const statusModal = document.getElementById('statusModal');
const browserToggle = document.getElementById('browserToggle');
const browserPanel = document.getElementById('browserPanel');
const closeBrowser = document.getElementById('closeBrowser');
const analysisPanel = document.getElementById('analysisPanel');
const analysisContent = document.getElementById('analysisContent');
const closeAnalysis = document.getElementById('closeAnalysis');

let ws = null;
let isProcessing = false;

function initWebSocket() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${location.host}/ws`);

    ws.onopen = () => console.log('WebSocket connected');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWSMessage(data);
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected, reconnecting...');
        setTimeout(initWebSocket, 3000);
    };

    ws.onerror = (err) => console.error('WebSocket error:', err);
}

function handleWSMessage(data) {
    switch (data.type) {
        case 'model_start':
            setModelState(data.model_index, 'active', 'thinking...');
            break;
        case 'model_done':
            setModelState(data.model_index, data.status === 'success' ? 'success' : 'error',
                data.status === 'success' ? `${data.time}s` : data.error || 'error');
            break;
        case 'synthesis_start':
            updateSynthesisStatus('synthesizing...');
            break;
        case 'final_reply':
            removeTypingIndicator();
            addMessage('assistant', data.data);
            setProcessing(false);
            resetModelStates();
            break;
        case 'error':
            removeTypingIndicator();
            addMessage('assistant', `Error: ${data.data}`);
            setProcessing(false);
            resetModelStates();
            break;
    }
}

function setModelState(index, state, text) {
    const indicator = document.querySelector(`.model-indicator[data-model="${index}"]`);
    if (!indicator) return;
    indicator.className = `model-indicator ${state}`;
    const stateEl = indicator.querySelector('.model-state');
    if (stateEl) stateEl.textContent = text;
}

function updateSynthesisStatus(text) {
    document.querySelectorAll('.model-indicator').forEach(el => {
        if (!el.classList.contains('success') && !el.classList.contains('error')) {
            const stateEl = el.querySelector('.model-state');
            if (stateEl) stateEl.textContent = text;
        }
    });
}

function resetModelStates() {
    document.querySelectorAll('.model-indicator').forEach(el => {
        el.className = 'model-indicator';
        const stateEl = el.querySelector('.model-state');
        if (stateEl) stateEl.textContent = 'ready';
    });
}

function addMessage(role, content) {
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = role === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = content;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function setProcessing(val) {
    isProcessing = val;
    sendBtn.disabled = val;
    messageInput.disabled = val;
}

function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isProcessing) return;

    addMessage('user', message);
    addTypingIndicator();
    messageInput.value = '';
    autoResize();
    setProcessing(true);

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            message: message,
            use_browser: browserToggle.checked
        }));
    } else {
        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, use_browser: browserToggle.checked })
        })
        .then(r => r.json())
        .then(data => {
            removeTypingIndicator();
            addMessage('assistant', data.reply);
            if (data.model_responses) showAnalysis(data.model_responses);
            setProcessing(false);
        })
        .catch(err => {
            removeTypingIndicator();
            addMessage('assistant', `Error: ${err.message}`);
            setProcessing(false);
        });
    }
}

function showAnalysis(responses) {
    analysisContent.innerHTML = '';
    for (const [key, resp] of Object.entries(responses)) {
        const modelDiv = document.createElement('div');
        modelDiv.className = 'analysis-model';
        const statusColor = resp.success ? 'var(--success)' : 'var(--error)';
        modelDiv.innerHTML = `
            <div class="analysis-model-header">
                <span class="status-dot" style="background:${statusColor}"></span>
                <span>${resp.role} (${resp.model})</span>
                <span style="color:${statusColor};font-size:12px;margin-left:auto">${resp.success ? resp.time + 's' : resp.error}</span>
            </div>
            <div class="analysis-model-body">${resp.success ? resp.response : 'Failed to respond'}</div>
        `;
        analysisContent.appendChild(modelDiv);
    }
    analysisPanel.classList.remove('hidden');
    analysisPanel.classList.add('visible');
}

async function loadStatus() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        let html = '';
        for (const [key, model] of Object.entries(data.models)) {
            const statusClass = model.configured ? 'configured' : 'missing';
            const statusText = model.configured ? 'Configured' : 'Missing';
            html += `<div class="status-item">
                <span class="status-label">${model.name}</span>
                <span class="status-value ${statusClass}">${statusText}</span>
            </div>`;
        }
        html += `<div class="status-item">
            <span class="status-label">Browser Agent</span>
            <span class="status-value ${data.browser_use ? 'configured' : 'missing'}">${data.browser_use ? 'Available' : 'Not installed'}</span>
        </div>`;
        document.getElementById('statusContent').innerHTML = html;
        statusModal.classList.remove('hidden');
    } catch (e) {
        console.error('Status error:', e);
    }
}

function autoResize() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
}

messageInput.addEventListener('input', autoResize);
messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);
clearBtn.addEventListener('click', async () => {
    if (isProcessing) return;
    chatMessages.innerHTML = `<div class="welcome-message">
        <div class="welcome-icon">🤖</div>
        <h2>Welcome to Virtual AI</h2>
        <p>A coordinated multi-model intelligence system. Ask anything and receive a synthesized answer from 5 specialized AI agents.</p>
    </div>`;
    analysisPanel.classList.remove('visible');
    analysisPanel.classList.add('hidden');
    try { await fetch('/api/clear', { method: 'POST' }); } catch (e) {}
});

statusBtn.addEventListener('click', loadStatus);
document.querySelector('.modal-close').addEventListener('click', () => statusModal.classList.add('hidden'));
statusModal.addEventListener('click', (e) => { if (e.target === statusModal) statusModal.classList.add('hidden'); });
closeBrowser.addEventListener('click', () => browserPanel.classList.remove('visible'));
closeAnalysis.addEventListener('click', () => {
    analysisPanel.classList.remove('visible');
    analysisPanel.classList.add('hidden');
});

initWebSocket();
