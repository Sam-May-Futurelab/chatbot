import re
import json
import random

def re_patterns():
    """static responses for our basic patterns"""
    precepts = {
        r"hello|hi|hiya|greetings|how are you": "How are you doing today?",
        r"bye|goodbye|see you later": "Goodbye! I hope you have a great day!",
        r"thank you|thanks": "You're welcome! Let me know if you need anything else!",
        r"how old are you": "I'm still quite young! Sam coded me recently.",
        }
    return precepts

def load_intents(file_path="intents.json"):
    """Loads the intents from a JSON file."""
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            return data['intents']
    except FileNotFoundError:
        print(f"Error: oops! The file {file_path} was not found!")
        return []
    except json.JSONDecodeError:
        print(f"Error: oops! The file {file_path} is not a valid JSON!")
        return []
    

def build_chatbot_data(intents):
    """Builds a dictionary of patterns and responses from the intents."""
    patterntointent = {}
    intenttoresponse = {}

    for intent in intents:
        tag = intent['tag']
        patterns = intent['patterns']
        responses = intent['responses']

        intenttoresponse[tag] = responses

        for pattern in patterns:
            patterntointent[pattern] = tag


    return patterntointent, intenttoresponse


def find_intent(user_input, patterntointent):
    """Finds the intent of the user input based on patterns."""
    for pattern, intent in patterntointent.items():
        if re.search(pattern, user_input, re.IGNORECASE):
            return intent, pattern
    return None, None

def generate_response(intent, pattern, user_input, intenttoresponse):
    """Generates a response based on the intent and user input."""
    if intent not in intenttoresponse:
        return "I'm sorry, I don't understand that."
    return random.choice(intenttoresponse[intent])

# dynamic pattern for food and drink
def get_dynamic_response(user_input):
    drink_pattern = r"(?:have|drink|want|like)\s+(?:to\s+)?(?:a\s+|some\s+)?(?P<drink>\w+)"
    match = re.search(drink_pattern, user_input, re.IGNORECASE)

    if match:
        drink_item = match.group("drink")
        food_item = "chips"
        template = "You can have a {food_item} and a {drink_item} with me!"
        return template.format(food_item=food_item, drink_item=drink_item)

    return None

# Main chatbot loop
def chatbot():
    print("Welcome! (Type 'exit' to to close the chat)")

    intents = load_intents()
    if not intents:
        print("Could not load intents. Using backup patterns...")
        predes = re_patterns()
    else:
        patterntointent, intenttoresponse = build_chatbot_data(intents)
        
        while True:
            user_input = input("You: ")
            
            # end chat if user says exit
            if user_input.lower() == "exit":
                print("Chatbot: Thank you for your interaction")
                break
            
            # Use JSON patterns
            intent, matched_pattern = find_intent(user_input, patterntointent)
            
            if intent:
                response = generate_response(intent, matched_pattern, user_input, intenttoresponse)
                print("Chatbot:", response)
                # if nothing matches
            else:
                print("Chatbot: I'm sorry, could you rephrase that?")

# Run the chatbot!
chatbot()