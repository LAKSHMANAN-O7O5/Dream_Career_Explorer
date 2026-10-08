// --- Chatbot JS Controller ---

document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatMessages = document.getElementById('chat-messages');

    if (!chatMessages) return; // Exit if not on chatbot page

    // Focus input on page load
    chatInput.focus();

    // Event listener for Send button click
    sendBtn.addEventListener('click', sendMessage);

    // Event listener for Enter keypress
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // 1. Append User Message
        appendMessage('user', text);
        chatInput.value = '';
        chatInput.focus();

        // 2. Append Loading Indicator
        const loadingId = appendMessage('bot', '<div class="spinner-grow spinner-grow-sm text-indigo" role="status"></div> Thinking...', true);

        // 3. Post to API Endpoint
        fetch('/student/chatbot/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: text })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loader
            removeLoader(loadingId);
            
            // Format markdown response to simple HTML
            appendMessage('bot', data.response, true);
        })
        .catch(err => {
            removeLoader(loadingId);
            appendMessage('bot', "Sorry, I'm having trouble connecting to the counselor core. Please try again.");
            console.error('Chatbot error:', err);
        });
    }

    function appendMessage(sender, content, isHTML = false) {
        const messageNode = document.createElement('div');
        messageNode.className = `chat-bubble ${sender}`;
        
        if (isHTML) {
            messageNode.innerHTML = content;
        } else {
            // Parse text
            messageNode.innerHTML = parseMarkdown(content);
        }
        
        // Generate a random ID for loaders
        const id = 'msg_' + Math.random().toString(36).substr(2, 9);
        messageNode.setAttribute('id', id);
        
        chatMessages.appendChild(messageNode);
        scrollToBottom();
        return id;
    }

    function removeLoader(id) {
        const loader = document.getElementById(id);
        if (loader) {
            loader.remove();
        }
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Helper: Basic Markdown Parser for Bot Responses
    function parseMarkdown(text) {
        let raw = text;
        // Escape HTML
        raw = raw.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        
        // Convert Bold (**text** -> <strong>text</strong>)
        raw = raw.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert Bullets/Lists
        raw = raw.replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>');
        raw = raw.replace(/(<li>.*?<\/li>)+/gs, '<ul>$&</ul>');
        
        // Convert Linebreaks
        raw = raw.replace(/\n/g, '<br>');
        
        return raw;
    }
});
