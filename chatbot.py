import re
import json
import random
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import string

# download the nltk resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger_eng')
except LookupError:
    nltk.download('averaged_perceptron_tagger_eng')


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

class ChatbotMemory:
    """
    stores the users information for personalised responses
    """
    def __init__(self):
        self.user_name = None
        self.user_preferences = {}

    def set_name(self, name):
        self.user_name = name

    def get_name(self):
        return self.user_name if self.user_name else "friend"

    def set_preference(self, key, value):
        self.user_preferences[key] = value

    def get_preference(self, key):
        return self.user_preferences.get(key, None)
    
# initialise the memory
memory = ChatbotMemory()

def extract_name_from_input(user_input):
    """
    extracts the name from the user input if it exists
    """
    # Check if it's just a single word (likely a name) - but not common words
    common_words = ['hello', 'hi', 'hey', 'good', 'bad', 'sad', 'happy', 'great', 'awesome', 'beans', 'food', 'drink', 'what', 'how', 'when', 'where', 'why']
    
    if re.match(r"^[A-Za-z]+!?$", user_input.strip()):
        name_candidate = user_input.strip().rstrip('!').lower()
        if name_candidate not in common_words:
            return name_candidate.capitalize()
    
    # Check for explicit name patterns
    name_patterns = [
        r"my name is\s+(\w+)",
        r"i'm\s+(\w+)",
        r"call me\s+(\w+)",
        r"i am\s+(\w+)",
        r"you can call me\s+(\w+)",
        r"i go by\s+(\w+)",
        r"name's\s+(\w+)",
    ]

    for pattern in name_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            name_candidate = match.group(1).lower()
            # make sure not to extract common emotion words as names
            if name_candidate not in common_words:
                return match.group(1).capitalize()
    return None

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
    """Generates a personalised response with sentiment and memory."""
    if intent not in intenttoresponse:
        return "I'm sorry, I don't understand that."
    
    # extracts and stores the name if mentioned by user
    name = extract_name_from_input(user_input)
    if name:
        memory.set_name(name)
    
    # Special handling for user name queries (if mentioned)
    if intent == "user_name_query":
        if memory.get_name() == "friend":
            return "I don't know your name yet! You can tell me by saying 'My name is...' or just tell me your name!"
        else:
            response = random.choice(intenttoresponse[intent])
            response = response.replace("{name}", memory.get_name())
            return response
    
    # generates the sentiment aware response
    response = generate_sentiment_aware_response(intent, intenttoresponse[intent], user_input)
    
    # Applies the template substitutions
    response = response.replace("{name}", memory.get_name())
    response = response.replace("{user_name}", memory.get_name())
    
    return response

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
    
def analyse_pos_and_respond(user_input):
    """analyses part of speech and generates a response based on it."""
    tokens = word_tokenize(user_input)
    pos_tags = pos_tag(tokens)
#extract key POS types
    nouns = [word for word, pos in pos_tags if pos.startswith('NN')]
    verbs = [word for word, pos in pos_tags if pos.startswith('VB')]
    adjectives = [word for word, pos in pos_tags if pos.startswith('JJ')]

#generate POS-based responses
    if nouns:
        food_nouns = [noun for noun in nouns if noun.lower() in ['pizza', 'chips', 'soup', 'pasta', 'beans', 'fries', 'burger', 'sandwich', 'salad', 'cookies']]
        if food_nouns:
            return f"I noticed you mentioned {', '.join(food_nouns)}. Those are tasty! Do you like them?"
    
    if verbs:
        cooking_verbs = [verb for verb in verbs if verb.lower() in ['cook', 'eat', 'drink', 'make', 'prepare']]
        if cooking_verbs:
            return f"I see you mentioned {', '.join(cooking_verbs)}. Sounds great! Do you need a recipe?"

    if adjectives:
        food_adjectives = [adj for adj in adjectives if adj.lower() in ['delicious', 'tasty', 'spicy', 'sweet', 'sour', 'savory']]
        if food_adjectives:
            return f"I see you mentioned {', '.join(food_adjectives)}. Those flavors sound amazing! What's your favorite?"
    
    return None

def analyze_sentiment(user_input):
    """basic sentiment analysis to determine positive or negative sentiment."""
    positive_words = ['good', 'great', 'happy', 'love', 'excellent', 'fantastic']
    negative_words = ['bad', 'sad', 'hate', 'terrible', 'awful']

    words = user_input.lower().split()

    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    if positive_count > negative_count:
        return "positive"
    elif negative_count > positive_count:
        return "negative"
    else:
        return "neutral"
    

def generate_sentiment_aware_response(intent, responses, user_input):
    """generate responsesd with sentiment awareness."""
    sentiment = analyze_sentiment(user_input)
    response = random.choice(responses)

#add the sentiment appropriate responses
    if sentiment == "positive":
        response += " I'm glad to hear that!"
    elif sentiment == "negative":
        response += " I'm sorry to hear that. How can I help?"

    return response

# dynamic pattern for food and drink
def get_dynamic_response(user_input):
    """Enhanced dynamic response for food and drinks."""
# tries to extract specific food/drink items
    drink_pattern = r"(?:have|drink|want|like)\s+(?:to\s+)?(?:a\s+|some\s+)?(?P<drink>\w+)"
    match = re.search(drink_pattern, user_input, re.IGNORECASE)

    foods = ["pizza", "pasta", "cookies", "sandwich", "burger", "salad"]
    drinks = ["water", "juice", "soda", "coffee", "tea", "milk"]

    if match:
        item = match.group("drink")
        if "food" in user_input.lower():
            food_item = random.choice(foods)
            drink_item = random.choice(drinks)
            return f"You can have {food_item} and {drink_item} with me!"
        elif "drink" in user_input.lower():
            drink_item = random.choice(drinks)
            food_item = random.choice(foods)
            return f"You can have {drink_item} and some {food_item} with me!"
        else:
            # default response
            food_item = random.choice(foods)
            drink_item = random.choice(drinks)
            return f"You can have {food_item} and {drink_item} with me!"

    return None

# Main chatbot loop
def chatbot():
    print("Beep Boop - Welcome to Sam's ChatBot - Your Personal Assistant!")
    print("I can help you with conversations, answer questions, and provide friendly chat.")
    print("I can discuss food, share jokes, remember your name, and much more!")
    print("(Tell me your name anytime, or type 'exit' to close)")
    print()

    intents = load_intents()
    if not intents:
        print("Could not load intents. Exiting...")
        return
    
    patterntointent, intenttoresponse = build_chatbot_data(intents)
        
    while True:
        user_input = input("You: ")
            
        if user_input.lower() == "exit":
            print(f"Chatbot: Goodbye {memory.get_name()}! Thanks for chatting with your personal assistant!")
            break
        
        # tries POS analysis first
        pos_response = analyse_pos_and_respond(user_input)
        if pos_response:
            print("Chatbot:", pos_response)
            continue
            
        intent, matched_pattern = enhanced_find_intent(user_input, patterntointent)
            
        if intent:
            if intent == "food_drink":
                dynamic_response = get_dynamic_response(user_input)
                if dynamic_response:
                    print("Chatbot:", dynamic_response)
                else:
                    response = generate_response(intent, matched_pattern, user_input, intenttoresponse)
                    print("Chatbot:", response)
            else:
                response = generate_response(intent, matched_pattern, user_input, intenttoresponse)
                print("Chatbot:", response)
        else:
            response = generate_fallback_response(user_input)
            print("Chatbot:", response)

# Run the chatbot!
chatbot()