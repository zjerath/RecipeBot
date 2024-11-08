import pandas as pd
import json
import re

def build_google_search_query(question):
    return f"https://www.google.com/search?q={question.replace(' ', '+')}"

# detect general recipe questions, or how to
# i.e. "show me the ingredients list", "how to preheat oven"
def is_general_question(response):
    return True

# detect navigation requests 
# i.e. "go to next step"
def is_navigation_request(response):
    return True

# detect whether question is asking about parameters for a particular step
# i.e. "what are the ingredients for this step"
def is_step_specific_question(response):
    return True

def return_steps(recipe):
    steps_str = f"Here are the steps to make {recipe['title']}: \n"
    for step in recipe['steps']:
        steps_str += f"{step['step_number']}. {step['text']}\n"
    return steps_str

def return_ingredients(recipe, step=None):
    match step:
        case None:
            ingredients_list = [f"{i+1}. {ingredient['name']}" for i, ingredient in enumerate(recipe['ingredients'])]
            return f"Here are the ingredients used in {recipe['title']}:\n" + "\n".join(ingredients_list)
        case _: # return ingredients for specific step
            ingredients_list = [f"{i+1}. {ingredient}" for i, ingredient in enumerate(recipe['steps'][step-1]['ingredients'])]
            return f"Here are the ingredients used in step {step} of {recipe['title']}:\n" + "\n".join(ingredients_list)

def return_tools(recipe, step=None):
    match step:
        case None:
            tools_list = [f"{i+1}. {tool}" for i, tool in enumerate(recipe['tools'])]
            return f"Here are the tools used in {recipe['title']}:\n" + "\n".join(tools_list)
        case _: # return tools for specific step
            tools_list = [f"{i+1}. {tool}" for i, tool in enumerate(recipe['steps'][step-1]['tools'])]
            return f"Here are the tools used in step {step} of {recipe['title']}:\n" + "\n".join(tools_list)
    
def return_methods(recipe, step=None):
    match step:
        case None:
            methods_list = [f"{i+1}. {method}" for i, method in enumerate(recipe['methods'])]
            return f"Here are the methods used in {recipe['title']}:\n" + "\n".join(methods_list)
        case _: # return methods for specific step 
            methods_list = [f"{i+1}. {method}" for i, method in enumerate(recipe['steps'][step-1]['methods'])]
            return f"Here are the methods used in step {step} of {recipe['title']}:\n" + "\n".join(methods_list)

# To do: format this better
def return_time(recipe, step):
    step_time_info = recipe['steps'][step-1]['time']
    return f"Carry out this step for {step_time_info['duration']} {step_time_info['unit']}{'s' if step_time_info['duration'] != 1 else ''}"
'''
Currently handles:
- recipe retrieval & display
- simple "what is"
- specific "how to"

To do:
- handle step navigation requests?
- return step specific parameters?
- handle both simultaneously?
'''
def handle_response(response, recipe):
    # Decide if the response is a question or a recipe flow statement
    if is_general_question(response):
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
        # TODO: Handle navigation statements 
        return response

def update_step(current_step, user_query, recipe_object):
    '''
    Given the current step and a user query, return the appropriate step to navigate to.
    
    Parameters:
        current_step: index of the current step in the recipe
        user_query: a user command specifying which step to navigate to
                    the navigation request may be classified into the following navigation types:
                        Current - stay at current step, typically used for repeat requests
                        Previous - navigate to previous step
                        Next - proceed to next step
                        Nth - navigate to any arbitrary step in the recipe
        recipe_object: recipe we are navigating through
    '''

    # TO DO: better logic for classifying requests, probably regex
    navigation_keywords = {
        'Current': ['repeat'],
        'Previous': ['back', 'previous'],
        'Next': ['next', 'proceed'],
        'Nth': ['th step', 'st step']
    }
    
    # categorize user_query
    navigation_type = None
    for type in navigation_keywords:
        if any(i.lower() in user_query.lower() for i in navigation_keywords[type]):
            navigation_type = type
            break
    
    # return appropriate index corresponding to user_query category
    match navigation_type:
        case 'Current':
            return current_step
        case 'Previous':
            if current_step == 0:
                return "there is no previous step"
            return current_step - 1
        case 'Next':
            if current_step == len(recipe_object['steps']) - 1: 
                return "there is no next step"
            return current_step + 1
        case 'Nth':
            # TO DO: better step_num extraction logic
            step_num = [int(s) for s in re.findall(r'\d+', user_query)][0] - 1
            if step_num < 0 or step_num >= len(recipe_object['steps']):
                return "specified step is out of range, cannot navigate to invalid step"
            return step_num

'''
To do/consider:
- separate Conversation class consisting of:
    - recipe object
    - question history
    - current step
    - response handling
'''
def main():
    recipe = json.load(open('example.json'))
    # print(recipe)

    # Basic recipe navigation
    current_step = 0
    print(recipe["steps"][current_step]["text"] +'\n')

    question_sequence = [
        "Go to the next step",
        "Please proceed",
        "Go back",
        "Repeat please",
        "Go to the 5th step"
        # "Go to the 25th step",
    ]

    for question in question_sequence:
        current_step = update_step(current_step, question, recipe)
        print(return_methods(recipe, current_step))
    
    # # Basic general question answering
    # question = "What is the recipe for lasagna?"
    # print(question)
    # # print(handle_response(question, recipe))
    # # Normally, the bot would find the recipe and parse, then move forward from here. 
    # print("I found a recipe for lasagna. What do you want to know about it?")
    # question = "What are the ingredients?"
    # print(question)
    # print(handle_response(question, recipe))
    # question = "How do I make this?"
    # print(question)
    # print(handle_response(question, recipe))
    # question = "What methods will I use?"
    # print(question)
    # print(handle_response(question, recipe))
    # question = "How do I preheat the oven?"
    # print(question)
    # print(handle_response(question, recipe))
    # question = "What is aluminum foil?"
    # print(question)
    # print(handle_response(question, recipe))
if __name__ == "__main__":
    main()
