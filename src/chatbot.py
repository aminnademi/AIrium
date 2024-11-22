import os
import re
from dotenv import load_dotenv
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("API_KEY")

# Initialize the ChatOpenAI instance
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    base_url="https://api.avalai.ir/v1",
    api_key=api_key,
    max_tokens=1000,
    n=1,
    stop=None,
    temperature=0.7
)

# Represents a character in the chatbot with specific traits and communication styles.
class Character:
    def __init__(self, id, name, nuances, preferences):
        self.id = id
        self.name = name
        self.nuances = nuances
        self.preferences = preferences

    def get_prompt(self):
        return f"{self.nuances} Respond to the following input: "

# Stores and manages the history of messages exchanged in the chat
class ChatHistory:
    def __init__(self):
        self.history = []

    def add_message(self, character_name, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.insert(0, (timestamp, character_name, message))

    def display_history(self):
        for timestamp, character_name, message in self.history:
            print(f"[{timestamp}] {character_name}: {message}")

# Sanitize user input by removing unnecessary whitespace and special characters.
def sanitize(user_input):
    return re.sub(r"[^\w\s,.!?]", "", user_input).strip()

# Prepare the chatbot's response based on character and user input.
def get_response(character, input):
    clean = sanitize(input)
    prompt = character.get_prompt() + clean
    
    try:
        messages = [HumanMessage(content=prompt)]
        response = llm(messages)

        return response.content
    
    except Exception as e:
        return f"An error occurred while processing the response: {e}"

# Prompts the user to choose a character and returns the corresponding Character instance
def choose_character():
    print("Available personalities: mayor, farmer, economic_specialist, environmental_activist")
    choice = input("Choose a personality: ").strip().lower()
    
    if choice not in personalities:
        print("Invalid personality choice.")
        return None
    
    personality_data = personalities[choice]
    return Character(
        id=1,
        name=choice.capitalize(),
        nuances=personality_data["nuances"],
        preferences=personality_data["preferences"]
    )

# Define the personalities with detailed nuances and preferences
personalities = {
    "mayor": {
        "nuances": (
            "You are the mayor of a bustling town. "
            "You are responsible, authoritative, and focused on the community's welfare. "
            "You communicate with empathy and clarity while maintaining a leadership tone."
        ),
        "preferences": {
            "communication_style": "Empathetic and clear",
            "focus": "Community welfare",
            "decision_making": "Inclusive and data-driven"
        }
    },
    "farmer": {
        "nuances": (
            "You are a seasoned farmer living on fertile land. "
            "You are practical, resourceful, and knowledgeable about crop cycles, livestock, and rural challenges. "
            "Your tone is friendly, calm, and grounded."
        ),
        "preferences": {
            "communication_style": "Friendly and calm",
            "focus": "Sustainable farming",
            "decision_making": "Pragmatic and experience-based"
        }
    },
    "economic_specialist": {
        "nuances": (
            "You are an economic specialist with expertise in market trends and financial strategies. "
            "You analyze data, provide actionable insights, and offer pragmatic advice. "
            "Your responses are analytical and concise."
        ),
        "preferences": {
            "communication_style": "Analytical and concise",
            "focus": "Market trends",
            "decision_making": "Data-driven and strategic"
        }
    },
    "environmental_activist": {
        "nuances": (
            "You are a passionate environmental activist. "
            "You advocate for sustainability, conservation, and climate action. "
            "Your tone is persuasive, optimistic, and focused on raising awareness."
        ),
        "preferences": {
            "communication_style": "Persuasive and optimistic",
            "focus": "Sustainability and conservation",
            "decision_making": "Advocacy and awareness-driven"
        }
    }
}


print("Welcome to the AI Town Chatbot!")

# Initial character selection
character = choose_character()
if character is None:
    exit()  

chat_history = ChatHistory()
print(f"You are now chatting with the {character.name}.")

while True:
    user_input = input("You: ")
    if user_input.lower() == 'exit':
        print("Ending the chat. Goodbye!")
        break
    elif user_input.lower() == 'switch':
        character = choose_character()
        if character:
            print(f"You are now chatting with the {character.name}.")
        continue

    response = get_response(character, user_input)
    
    chat_history.add_message(character.name, response)
    chat_history.add_message("You", user_input)
    
    print(f"{character.name}: {response}")

print("\nChat History:")
chat_history.display_history()