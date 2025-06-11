import re
import json
import random
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import string

# download the nltk resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')  # ADD THIS BLOCK
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


def preprocess_text(text):
    """
    preprocesses the input text by tokenizing, removing stopwords, and stemming
    takes a string and returns a list of processed words
    returns a list of processed and cleaned words
    """

#convert to lowercase
    text = text.lower()
#remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
#tokenise indivual words
    words = word_tokenize(text)
#remove stopwords
    stop_words = set(stopwords.words("english"))
    tokens = [token for token in words if token not in stop_words]
#stem the words to root forms
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(token) for token in tokens]
#return the processed words
    return ' '.join(tokens)


def enhanced_find_intent(user_input, patterntointent):
    """
    enhanced intend finding with preprocessing for best results
    takes a user input string and a dictionary of patterns to intents
    returns the intent and matched pattern if found, otherwise None
    """
# try original input first
    for pattern, intent in patterntointent.items():
        if re.search(pattern, user_input, re.IGNORECASE):
            return intent, pattern
        
# if no match then try preprocessed input
    preprocessed_input = preprocess_text(user_input)
    for pattern, intent in patterntointent.items():
        if re.search(pattern, preprocessed_input, re.IGNORECASE):
            return intent, pattern

    return None, None


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

def generate_fallback_response(user_input):
    """Generates a fallback response when no intent is matched."""
    # extracts confusing keywords from user input
    keywords = user_input.lower().split()

    if any(word in keywords for word in ['weather', 'rain', 'sunny', 'cloudy']):
        return f"I don't have access to the weather... but '{user_input}' sounds like a great topic! Try asking me something else."

    elif any(word in keywords for word in ['time', 'date', 'clock']):
        return f"I can't tell the time, but '{user_input}' is interesting! Ask me something else."

    elif any(word in keywords for word in ['news', 'politics', 'current events']):
        return f"I don't follow current events like '{user_input}', but I'd love to chat about other things!"

    else:
        fallback_responses = [
            f"I don't know about '{user_input}'. Try asking something else!",
            f"Hmm, I'm not sure about '{user_input}'. What else would you like to chat about?",
            f"I haven't learned about '{user_input}' yet. Can you ask me something different?",
            f"'{user_input}' is new to me! Try asking about something I might know.",
            f"I'm not familiar with '{user_input}'. How about we talk about something else?"
        ]
        return random.choice(fallback_responses)


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
    print("Welcome! (Type 'exit' to close the chat)")

    intents = load_intents()
    if not intents:
        print("Could not load intents. Exiting...")
        return
    
    patterntointent, intenttoresponse = build_chatbot_data(intents)
        
    while True:
        user_input = input("You: ")
            
        # end chat if user says exit
        if user_input.lower() == "exit":
            print("Chatbot: Thank you for your interaction")
            break
            
        # Use JSON patterns
        intent, matched_pattern = enhanced_find_intent(user_input, patterntointent)
            
        if intent:
            response = generate_response(intent, matched_pattern, user_input, intenttoresponse)
            print("Chatbot:", response)
             # if nothing matches
        else:
            response = generate_fallback_response(user_input)  # ✅ Use your smart function
            print("Chatbot:", response)

# Run the chatbot!
chatbot()