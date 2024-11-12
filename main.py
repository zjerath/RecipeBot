import re
import json
from conversation import Conversation
from parse import fetch_recipe, extract_json_ld, parse_recipe

def is_valid_allrecipes_url(url):
    """Validate if the URL is from allrecipes.com"""
    return re.match(r'^https?://(www\.)?allrecipes\.com/recipe/\d+/[^/]+/?$', url)

def main():
    '''
    recipe = json.load(open('example.json'))
    # print(recipe)
    conversation = Conversation(recipe)

    # Question type classification (General, Navigation, Step-specific) logic assumes specific question format
    # Check question_handler.determine_request_type() for details  
    question_sequence = [
        "What is the recipe for lasagna?",
        # "What are the ingredients?",
        # "How do I preheat the oven?",
        "Tell me the ingredients for this step.",
        "Go to the next step",
        "What are the ingredients for this step?",
        "Proceed to the next step",
        "what are the methods for this step?",
        "Go to the 5th step",
        "What tools do I need for this step?",
        "Go to the 25th step"
    ]

    for question in question_sequence:
        print(f"QUESTION: {question}")
        conversation.handle_request(question)
        print('\n')'''
    # prompt for user input
    print("Please specify a URL.")
    url = input().strip()
    # validate url
    if not is_valid_allrecipes_url(url):
        print("The URL must be from allrecipes.com.")
        return
    # attempt to fetch and parse url
    try:
        soup = fetch_recipe(url)
        json_data = extract_json_ld(soup)
        if not json_data:
            print("Could not find a valid recipe in the provided URL.")
            return
        # parse recipe
        recipe = parse_recipe(json_data)
        # if json easier to work with, add line below and refer to jsn in convo
        # jsn = recipe_to_json(recipe)
        print(f"Bot: Alright. So let's start working with \"{recipe.title}\". What do you want to do?")
        print("\n[1] Go over ingredients list")
        print("[2] Go over recipe steps.")
        # simulate user choice
        choice = input().strip()
        conversation = Conversation(recipe)
        if choice == '1':
            conversation.handle_request("What are the ingredients?")
        elif choice == '2':
            conversation.handle_request("Go over recipe steps")
        else:
            print("Invalid choice. Please enter 1 or 2.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()