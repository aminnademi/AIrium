from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from .models import PERSONALITIES, Message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from groq import Groq
import os
from dotenv import load_dotenv
from accounts.models import User

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize the Groq client
client = Groq(api_key=api_key)

def sort_users(u1, u2):
    if u2 < u1:
        u1, u2 = u2, u1

    return u1, u2

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
        # if form.is_valid():
        #     form.save()
        #     return redirect('main')  # Redirect to the main page after registration
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def save_message(u1, u2, onsay, message):
    message = Message(
        username1=u1,
        username2=u2,
        onesay=onsay,
        message=message
    )
    message.save()

def chatgpt2(personality, user_input):
    # Get the personality's nuances
    nuances = PERSONALITIES[personality]['nuances']

    # Prepare the prompt
    prompt = f"{nuances} Respond to the following input: {user_input}"
        
    chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-70b-8192",  # Use the appropriate Groq model
            )
    return chat_completion.choices[0].message.content


def chatgpt(personality, user_input):
    # Get the personality's nuances
    nuances = PERSONALITIES[personality]['nuances']

    # Prepare the prompt
    prompt = f"{nuances} Respond to the following input: {user_input}"
    return "chat gpt say cose Nanat: " + prompt


@login_required
def main(request):
    return render(request, 'main.html')


@csrf_exempt
@login_required
def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('input')
        personality = request.POST.get('personality')

        if personality not in PERSONALITIES:
            return JsonResponse({'error': 'Invalid personality'}, status=400)

        try:
            # Generate the chatbot's response using Groq
            response = chatgpt(personality, user_input)
            # Save user message and chatbot response in the database
            u1 = request.user.username  # Replace with the logged-in user's username
            u2 = personality
            username1, username2 = sort_users(u1, u2)
            save_message(username1, username2, True, user_input)
            save_message(username1, username2, False, response)

            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def getHistory(request):
    if request.method == 'POST':
        u1 = request.POST.get('username1')
        u2 = request.POST.get('username2')

        return JsonResponse({'response': getMessage(u1, u2)})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def getMessage(u1, u2):
    u1, u2 = sort_users(u1, u2)

    chat_history = Message.objects.filter(username1=u1, username2=u2)
    ans = []
    for message in chat_history:
        ans.append({
            "message": message.message,
            "onesay": message.onesay,
            "date": message.date
        })
    # print(ans)
    return ans

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
            response1 = chatgpt(personality1, message)
            save_message(u1, u2, True, response1)
            message = response1

            # Personality 2 responds
            response2 = chatgpt(personality2, message)
            save_message(u1, u2, False, response2)
            message = response2

        return JsonResponse({'response': 'Conversation saved successfully'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)