from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import PERSONALITIES, Message, User
from .forms import RegistrationForm
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize the Groq client
client = Groq(api_key=api_key)

def sort_users(u1, u2):
    if u2 < u1:
        u1, u2 = u2, u1
    return u1, u2

def save_message(u1, u2, onsay, message):
    message = Message(
        username1=u1,
        username2=u2,
        onesay=onsay,
        message=message
    )
    message.save()

def get_message(u1, u2):
    u1, u2 = sort_users(u1, u2)
    chat_history = Message.objects.filter(username1=u1, username2=u2).order_by('date')
    ans = []
    for message in chat_history:
        ans.append({
            "message": message.message,
            "onesay": message.onesay,
            "date": message.date
        })
    return ans

def chatgpt(personality, user_input, username, is_guest):
    # Fetch the last 10 messages from the database
    u1, u2 = sort_users(username, personality)
    chat_history = get_message(u1, u2)[-10:]

    # Prepare the conversation history for the prompt
    conversation_history = ""
    for message in chat_history:
        sender = "You" if message['onesay'] else personality
        conversation_history += f"{sender}: {message['message']}\n"

    # Get the personality's nuances
    nuances = PERSONALITIES[personality]['nuances']

    # Prepare the prompt with conversation history
    prompt = (
    f"{nuances}\n\n"
    f"Previous Conversation:\n{conversation_history}\n"
    f"Respond to the following input in 1-2 short sentences:\n{user_input}\n"
    f"Be concise and avoid unnecessary details."
    )

    # Generate the chatbot's response using Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",  # Use the desired Groq model
    )
    response = chat_completion.choices[0].message.content

    # Save the message to the database only if not in guest mode
    if not is_guest:
        save_message(username, personality, True, user_input)
        save_message(username, personality, False, response)
    
    return response


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.data.get('username'):
            user = User.objects.create_user(
                username=form.data.get('username'),
                email=form.data.get('email'),
                password=form.data.get('password1')
            )
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})

def main(request):
    return render(request, 'main.html')

@csrf_exempt
def chatbot(request):   # Handle chatbot interactions, Skip saving to the database if in guest mode.
    if request.method == 'POST':
        user_input = request.POST.get('input')
        personality = request.POST.get('personality')
        is_guest = request.session.get('is_guest', False)

        if personality not in PERSONALITIES:
            return JsonResponse({'error': 'Invalid personality'}, status=400)

        try:
            # Generate the chatbot's response
            response = chatgpt(personality, user_input, request.user.username if not is_guest else 'guest', is_guest)
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def guest_mode(request):    # Enable guest mode by setting a session variable.
    request.session['is_guest'] = True
    request.session['username'] = 'Guest_User'  # Set a placeholder username for guest mode
    return redirect('main')


@csrf_exempt
def get_chat_history(request):      # Fetch chat history for a specific user and character.
    if not request.user.is_authenticated and not request.session.get('is_guest', False):
        return JsonResponse({'error': 'User not authenticated'}, status=401)

    if request.method == 'POST':
        username1 = request.user.username if request.user.is_authenticated else 'guest'
        username2 = request.POST.get('character')

        sort_users(username1, username2)

        # Fetch chat history from the database
        chat_history = Message.objects.filter(username1=username1, username2=username2).order_by('date')

        # Prepare the response data
        history_data = []
        for message in chat_history:
            history_data.append({
                'message': message.message,
                'sender': 'You' if message.onesay else username2,
                'date': message.date.strftime("%Y-%m-%d %H:%M:%S")
            })

        return JsonResponse({'chat_history': history_data})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_history(request):
    if request.method == 'POST':
        u1 = request.POST.get('username1')
        u2 = request.POST.get('username2')

        return JsonResponse({'response': get_message(u1, u2)})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def chatbot_together(request):
    if request.method == 'POST':
        personality1 = request.POST.get('personality1')
        personality2 = request.POST.get('personality2')
        n = int(request.POST.get('n'))

        if personality1 not in PERSONALITIES or personality2 not in PERSONALITIES:
            return JsonResponse({'error': 'Invalid personality'}, status=400)

        u1, u2 = sort_users(personality1, personality2)
        message = 'Hi'
        for i in range(n):
            # Personality 1 responds
            response1 = chatgpt(personality1, message, personality1, True)  # Pass personality1 as username
            save_message(u1, u2, True, response1)
            message = response1

            # Personality 2 responds
            response2 = chatgpt(personality2, message, personality2, True)  # Pass personality2 as username
            save_message(u1, u2, False, response2)
            message = response2

        return JsonResponse({'response': 'Conversation saved successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)