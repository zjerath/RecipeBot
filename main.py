import re
import json
from conversation import Conversation
from parse import fetch_recipe, extract_json_ld, parse_recipe, recipe_to_json

def is_valid_allrecipes_url(url):
    """Validate if the URL is from allrecipes.com"""
    return re.match(r'^https?://(www\.)?allrecipes\.com/recipe/\d+/[^/]+/?$', url)

def main():
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
        jsn = recipe_to_json(recipe)
        conversation = Conversation(jsn) # Conversation() assumes recipe object in JSON format ATM

        print(f"Bot: Alright. So let's start working with \"{recipe.title}\". What do you want to do?")
        print("\n[1] Go over ingredients list")
        print("[2] Go over recipe steps.")
        # simulate user choice
        choice = input().strip()
        if choice == '1':
            print(conversation.handle_request("What are the ingredients?"))
        elif choice == '2':
            print(conversation.handle_request("Go over recipe steps"))
        else:
            print("Invalid choice. Please enter 1 or 2.")
        # simulate user choice
        while True:
            request = input().strip()
            print('\n')
            if request.lower() == "stop":
                break
            response = conversation.handle_request(request)
            print(response)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()