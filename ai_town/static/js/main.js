document.addEventListener('DOMContentLoaded', function () {
    // Function to toggle password visibility
    function togglePassword(fieldId) {
        const passwordField = document.getElementById(fieldId);
        const toggleButton = passwordField.nextElementSibling;
        const eyeIcon = toggleButton.querySelector('i');

        if (passwordField.type === "password") {
            passwordField.type = "text";
            eyeIcon.classList.remove('fa-eye');
            eyeIcon.classList.add('fa-eye-slash');
        } else {
            passwordField.type = "password";
            eyeIcon.classList.remove('fa-eye-slash');
            eyeIcon.classList.add('fa-eye');
        }
    }

    // Attach event listeners to all "Show Password" buttons
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const fieldId = this.getAttribute('data-field-id');
            togglePassword(fieldId);
        });
    });

    // Function to validate password and confirm password fields
    function validatePasswords() {
        const password1 = document.getElementById('id_password1').value;
        const password2 = document.getElementById('id_password2').value;
        const errorMessage = document.getElementById('password-error');

        if (password1 !== password2) {
            if (!errorMessage) {
                // Create and display the error message
                const errorDiv = document.createElement('div');
                errorDiv.id = 'password-error';
                errorDiv.style.color = 'red';
                errorDiv.style.marginTop = '10px';
                errorDiv.textContent = 'Passwords do not match. Please try again.';
                document.querySelector('.form_submit').before(errorDiv);
            }
            return false; // Prevent form submission
        } else {
            // Remove the error message if passwords match
            if (errorMessage) {
                errorMessage.remove();
            }
            return true; // Allow form submission
        }
    }

    // Attach event listener to the form submission
    const registerForm = document.querySelector('form');
    if (registerForm) {
        registerForm.addEventListener('submit', function (event) {
            if (!validatePasswords()) {
                event.preventDefault(); // Prevent form submission if passwords don't match
            }
        });
    }
});
document.addEventListener('DOMContentLoaded', function () {
    // Function to toggle password visibility
    function togglePassword(fieldId) {
        const passwordField = document.getElementById(fieldId);
        const toggleButton = passwordField.nextElementSibling;
        const eyeIcon = toggleButton.querySelector('i');

        if (passwordField.type === "password") {
            passwordField.type = "text";
            eyeIcon.classList.remove('fa-eye'); // Remove "eye" icon
            eyeIcon.classList.add('fa-eye-slash'); // Add "eye-slash" icon
        } else {
            passwordField.type = "password";
            eyeIcon.classList.remove('fa-eye-slash'); // Remove "eye-slash" icon
            eyeIcon.classList.add('fa-eye'); // Add "eye" icon
        }
    }

    // Attach event listeners to all "Show Password" buttons
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const fieldId = this.getAttribute('data-field-id');
            togglePassword(fieldId);
        });
    });
});
document.addEventListener('DOMContentLoaded', function () {
    const guestButton = document.querySelector('button[onclick="as_Guest()"]');

    function as_Guest() {
        fetch('/accounts/guest-mode/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        }).then(response => {
            if (response.ok) {
                window.location.href = '/accounts/main/';
            } else {
                console.error('Failed to enable guest mode');
            }
        });
    }

    if (guestButton) {
        guestButton.addEventListener('click', as_Guest);
    }

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

document.addEventListener('DOMContentLoaded', function () {
    const characters = document.querySelectorAll('.character');
    const chatWindow = document.getElementById('chat-window');

    characters.forEach(character => {
        character.addEventListener('click', async function () {
            const selectedPersonality = this.getAttribute('data-personality');

            chatWindow.innerHTML = '';

            try {
                const response = await fetch('/accounts/get-chat-history/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                    body: new URLSearchParams({
                        'character': selectedPersonality,
                    }),
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch chat history');
                }

                const data = await response.json();

                data.chat_history.forEach(message => {
                    const messageClass = message.sender === 'You' ? 'user-message' : 'bot-message';
                    chatWindow.innerHTML += `<div class="${messageClass}">${message.sender}: ${message.message}</div>`;
                });

                chatWindow.scrollTop = chatWindow.scrollHeight;

            } catch (error) {
                console.error('Error fetching chat history:', error);
                chatWindow.innerHTML += `<div class="error-message">Error: ${error.message}</div>`;
            }
        });
    });

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

document.addEventListener('DOMContentLoaded', function () {
    const characters = document.querySelectorAll('.character');
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const startDualChatButton = document.getElementById('start-dual-chat');
    const dualChatWindow = document.getElementById('dual-chat-window');

    let selectedPersonality = null;

    characters.forEach(character => {
        character.addEventListener('click', function () {
            selectedPersonality = this.getAttribute('data-personality');
        });
    });
    
    sendButton.addEventListener('click', async function () {
        const message = chatInput.value.trim();
        if (message && selectedPersonality) {
            chatWindow.innerHTML += `<div class="user-message">You: ${message}</div>`;

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
                    chatWindow.innerHTML += `<div class="bot-message">${selectedPersonality}: ${data.response}</div>`;
                } else if (data.error) {
                    chatWindow.innerHTML += `<div class="error-message">Error: ${data.error}</div>`;
                }
            } catch (error) {
                chatWindow.innerHTML += `<div class="error-message">Error: ${error.message}</div>`;
            }

            chatInput.value = '';
            chatWindow.scrollTop = chatWindow.scrollHeight;
        }
    });

    startDualChatButton.addEventListener('click', async function () {
        const personality1 = document.getElementById('personality1').value;
        const personality2 = document.getElementById('personality2').value;

        if (personality1 === personality2) {
            alert('Please select two different personalities.');
            return;
        }

        dualChatWindow.innerHTML = '';

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
                    'n': 5,
                }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            if (data.response === 'Conversation saved successfully') {
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