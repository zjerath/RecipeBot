import pandas as pd
import json

def build_google_search_query(question):
    return f"https://www.google.com/search?q={question.replace(' ', '+')}"

def is_question(response):
    return True

def return_ingredients(recipe):
    ingredients_list = [f"{i+1}. {ingredient['name']}" for i, ingredient in enumerate(recipe['ingredients'])]
    return f"Here are the ingredients used in {recipe['title']}:\n" + "\n".join(ingredients_list)

def return_steps(recipe):
    steps_str = f"Here are the steps to make {recipe['title']}: \n"
    for step in recipe['steps']:
        steps_str += f"{step['step_number']}. {step['text']}\n"
    return steps_str

def return_tools(recipe):
    tools_list = [f"{i+1}. {tool}" for i, tool in enumerate(recipe['tools'])]
    return f"Here are the tools used in {recipe['title']}:\n" + "\n".join(tools_list)

def return_methods(recipe):
    methods_list = [f"{i+1}. {method}" for i, method in enumerate(recipe['methods'])]
    return f"Here are the methods used in {recipe['title']}:\n" + "\n".join(methods_list)

def handle_response(response, recipe):
    # Decide if the response is a question or a recipe flow statement
    if is_question(response):
        # Decide if the question is about the recipe or about something else
        ingredient_words = ['ingredients']
        step_words = ['steps', 'instructions', 'make this', 'make it', 'cook this', 'cook it']
        tools_words = ['tools', 'equipment']
        method_words = ['methods']
        all_words = ingredient_words + step_words + tools_words + method_words
        if any(word in response for word in all_words):
            if any(word in response for word in ingredient_words):
                return return_ingredients(recipe)
            elif any(word in response for word in step_words):
                return return_steps(recipe)
            elif any(word in response for word in tools_words):
                return return_tools(recipe)
            elif any(word in response for word in method_words):
                return return_methods(recipe)
            else:
                return "I don't know that information about this recipe. Please try asking again."
        # If the question is not about the recipe, search Google
        else:
            google_search_query = build_google_search_query(response)
            return google_search_query
    else:
        # TODO: Handle statements 
        return response

def main():
    recipe = json.load(open('example.json'))
    # print(recipe)

    question = "What is the recipe for lasagna?"
    print(question)
    # print(handle_response(question, recipe))
    # Normally, the bot would find the recipe and parse, then move forward from here. 
    print("I found a recipe for lasagna. What do you want to know about it?")
    question = "What are the ingredients?"
    print(question)
    print(handle_response(question, recipe))
    question = "How do I make this?"
    print(question)
    print(handle_response(question, recipe))
    question = "What methods will I use?"
    print(question)
    print(handle_response(question, recipe))
    question = "How do I preheat the oven?"
    print(question)
    print(handle_response(question, recipe))
    question = "What is aluminum foil?"
    print(question)
    print(handle_response(question, recipe))
if __name__ == "__main__":
    main()
