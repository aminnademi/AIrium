document.addEventListener('DOMContentLoaded', function () {
    const characters = document.querySelectorAll('.character');
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');

    let selectedPersonality = null;

    // Handle character selection
    characters.forEach(character => {
        character.addEventListener('click', function () {
            selectedPersonality = this.getAttribute('data-personality');
            alert(`You selected the ${selectedPersonality}. Start chatting!`);
        });
    });

    // Handle sending messages
    sendButton.addEventListener('click', async function () {
        const message = chatInput.value.trim();
        if (message && selectedPersonality) {
            // Add user message to chat window
            chatWindow.innerHTML += `<div class="user-message">You: ${message}</div>`;

            // Send message to the backend
            try {
                const response = await fetch('/accounts/chatbot/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'), // Include CSRF token
                    },
                    body: new URLSearchParams({
                        'input': message,
                        'personality': selectedPersonality,
                    }),
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                if (data.response) {
                    // Add bot response to chat window
                    chatWindow.innerHTML += `<div class="bot-message">${selectedPersonality}: ${data.response}</div>`;
                } else if (data.error) {
                    chatWindow.innerHTML += `<div class="error-message">Error: ${data.error}</div>`;
                }
            } catch (error) {
                chatWindow.innerHTML += `<div class="error-message">Error: ${error.message}</div>`;
            }

            // Clear input
            chatInput.value = '';

            // Scroll to bottom of chat window
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    });

    // Function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});