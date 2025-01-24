function as_Guest(){

}

document.addEventListener('DOMContentLoaded', function () {
    const characters = document.querySelectorAll('.character');
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const startDualChatButton = document.getElementById('start-dual-chat');
    const dualChatWindow = document.getElementById('dual-chat-window');

    let selectedPersonality = null;

    // Handle character selection for single chat
    characters.forEach(character => {
        character.addEventListener('click', function () {
            selectedPersonality = this.getAttribute('data-personality');
            
            // alert(`You selected the ${selectedPersonality}. Start chatting!`);
        });
    });
    // Handle sending messages in single chat
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
                        'X-CSRFToken': getCookie('csrftoken'),
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

    // Handle starting dual chat
    startDualChatButton.addEventListener('click', async function () {
        const personality1 = document.getElementById('personality1').value;
        const personality2 = document.getElementById('personality2').value;

        if (personality1 === personality2) {
            alert('Please select two different personalities.');
            return;
        }

        // Clear the dual chat window
        dualChatWindow.innerHTML = '';

        // Start the dual chat
        try {
            const response = await fetch('/accounts/chatbot-together/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: new URLSearchParams({
                    'personality1': personality1,
                    'personality2': personality2,
                    'n': 5,  // Number of exchanges
                }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.response === 'Conversation saved successfully') {
                // Fetch and display the dual chat history
                const historyResponse = await fetch('/accounts/getHistory/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: new URLSearchParams({
                        'username1': personality1,
                        'username2': personality2,
                    }),
                });

                if (!historyResponse.ok) {
                    throw new Error('Failed to fetch chat history');
                }

                const historyData = await historyResponse.json();
                historyData.response.forEach(message => {
                    const sender = message.onesay ? personality1 : personality2;
                    dualChatWindow.innerHTML += `<div style="display: flex; justify-content: ${message.onesay ? "end" : "start"}">
                        <div class="dual-message" style="background-color: ${message.onesay ? "#3498db" : "#2ecc71"};">${sender}: ${message.message}</div></div>`;
                });
            }
        } catch (error) {
            dualChatWindow.innerHTML += `<div class="error-message">Error: ${error.message}</div>`;
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