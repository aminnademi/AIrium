from django.shortcuts import render, redirect
from .forms import RegistrationForm, ProfileForm
from django.contrib.auth.decorators import login_required
from .models import PERSONALITIES
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PERSONALITIES
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
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {
        'form': form,
        'PERSONALITIES': PERSONALITIES
    })

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
    return JsonResponse({'error': 'Invalid request method'}, status=400)