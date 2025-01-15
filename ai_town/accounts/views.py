from django.shortcuts import render, redirect
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from .models import PERSONALITIES, Message
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize the Groq client
client = Groq(api_key=api_key)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main')  # Redirect to the main page after registration
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required


def main(request):
    return render(request, 'main.html')

@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        user_input = request.POST.get('input')
        personality = request.POST.get('personality')

        if personality not in PERSONALITIES:
            return JsonResponse({'error': 'Invalid personality'}, status=400)

        # Get the personality's nuances
        nuances = PERSONALITIES[personality]['nuances']

        # Prepare the prompt
        prompt = f"{nuances} Respond to the following input: {user_input}"

        try:
            # Generate the chatbot's response using Groq
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="llama3-70b-8192",  # Use the appropriate Groq model
            )
            response = chat_completion.choices[0].message.content
            return JsonResponse({'response': response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        
    # add message in data base
    message = Message(
    username1=request.POST.get('username1'),  # Assuming the user is logged in
    username2="chatbot",  # Assuming the chatbot is the other party
    message=f"User: {user_input}\nChatbot: {response}"
)
    message.save()


    return JsonResponse({'error': 'Invalid request method'}, status=400)


def getHistory(request):
    if request.method == 'POST':
        u1 = request.POST.get('username1')
        u2 = request.POST.get('username2')

        return JsonResponse({'response': getMessage(u1, u2)})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def getMessage(u1, u2):
    if u2 < u1:
        u1, u2 = u2, u1

    chat_history = Message.objects.filter(username1=u1, username2=u2)

    return list(map(lambda i : i.message, chat_history))

