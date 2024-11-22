import re
from question_handler import QuestionHandler
import spacy

"""
Conversation module contains relevant state variables for recipe navigation, 
and logic for how to update those state variables depending on a user's request.
Generic question-answering logic is delegated to the QuestionHandler module.

A Conversation object consists of:
    - recipe of interest
    - question history
    - current step in the recipe
    - QuestionHandler object for handling user requests
"""

class Conversation:
    def __init__(self, recipe):
        self.recipe = recipe
        self.current_step = 0
        self.question_history = []
        self.question_handler = QuestionHandler(recipe)
        self.nlp = spacy.load("en_core_web_lg")
    
    def update_step(self, user_query):
        """
        Update the current step accordingly given the user query.
        
        Parameters:
            user_query: a user command specifying which step to navigate to
                        the navigation request may be classified into the following navigation types:
                            Current - stay at current step
                            Previous - go to previous step
                            Next - go to next step
                            Nth - go to any arbitrary step in the recipe
        """
        
        navigation_type = self.question_handler.detect_navigation_type(user_query)
        
        # return appropriate index corresponding to user_query category
        match navigation_type:
            case 'Current':
                pass
            case 'Previous':
                if self.current_step > 0:
                    self.current_step -= 1
                else:
                    return(f"You're already at the first step.")
            case 'Next':
                if self.current_step < len(self.recipe['steps']) - 1: 
                    self.current_step += 1
                else:
                    return(f"You've reached the end of the recipe.")
            case 'Nth':
                step_num = self.question_handler.extract_step_number(user_query)
                print(f"request: {user_query} | step_num: {step_num}")
                if step_num > 0 and step_num <= len(self.recipe['steps']):
                    self.current_step = step_num - 1 # self.current_step is 0 indexed
                else:
                    return(f"Invalid step number: this recipe has {len(self.recipe['steps'])} steps.")
            case _:
                return("Unknown navigation request type.")
    
    def handle_request(self, request):
        """
        This function receives all user requests, 
        classifies the user request, 
        and delegates the request to the appropriate function (in QuestionHandler) to respond to the user request appropriately.
        """
        # Define keywords for identifying question type
        ingredient_words = ['ingredients']
        step_words = ['steps', 'instructions', 'make this', 'make it', 'cook this', 'cook it']
        tools_words = ['tools', 'equipment']
        method_words = ['methods']
        # directions_words = ['directions', 'requirements']
        time_words = ['time', 'long', 'duration']
        all_words = ingredient_words + step_words + tools_words + method_words

        # Add user request to question history
        self.question_history.append(request)

        # identify type of user request
        user_request_type = self.question_handler.determine_request_type(request)
        print(f"request type: {user_request_type}")

        match user_request_type:
            case "General":
                if any(word in request for word in all_words):
                    if any(word in request for word in ingredient_words):
                        return(self.question_handler.return_ingredients())
                    elif any(word in request for word in step_words):
                        return(self.question_handler.return_steps())
                    elif any(word in request for word in tools_words):
                        return(self.question_handler.return_tools())
                    elif any(word in request for word in method_words):
                        return(self.question_handler.return_methods())
                    else:
                        return("I don't know that information about this recipe. Please try asking again.")
                # If the question is not about the recipe, search Google
                else:
                    # Deal with vague queries (How to cook that, How to make that, etc.)
                    precursor, demonstrative, reference = self.question_handler.extract_demonstrative_reference(request)
                    if reference is None: 
                        reference = ""
                    if precursor is None:
                        precursor = ""
                    phrase = f"{precursor} {demonstrative} {reference}".strip()
                    print(f"precursor: {precursor} | demonstrative: {demonstrative} | reference: {reference}")
                    
                    if demonstrative is not None:
                        # Get the current step's text
                        current_step_text = self.recipe['steps'][self.current_step]['text']

                        ingredients = self.question_handler.extract_subject_ingredient(current_step_text)
                        methods = self.question_handler.extract_subject_method(current_step_text)
                        tools = self.question_handler.extract_subject_tool(current_step_text)

                        # Reference replacements
                        if reference == "ingredient":
                            replacement = ingredients
                            if len(replacement) > 1:
                                return(f"Which of the following ingredients are you referring to? \n{', '.join(replacement)} \nPlease clarify your request.")
                            elif replacement:
                                replacement = replacement[0]
                                request = request.replace(phrase, precursor + " " + replacement)
                        elif reference == "tool":
                            replacement = tools
                            if len(replacement) > 1:
                                return(f"Which of the following tools are you referring to? \n{', '.join(replacement)} \nPlease clarify your request.")
                            elif replacement:
                                replacement = replacement[0]
                                request = request.replace(phrase, precursor + " " + replacement)
                        elif reference == "method":
                            replacement = methods
                            if len(replacement) > 1:
                                return(f"Which of the following methods are you referring to? \n{', '.join(replacement)} \nPlease clarify your request.")
                            elif replacement:
                                replacement = replacement[0]
                                request = request.replace(phrase, precursor + " " + replacement)
                        
                        # Precursor replacements
                        elif precursor == "do":
                            return(current_step_text)
                        elif precursor == "of":
                            replacement = ingredients
                            second_replacement = tools
                            if replacement: 
                                if len(replacement) > 1:
                                    return(f"Which of the following ingredients are you referring to? \n{', '.join(replacement)} \nPlease clarify your request.")
                                elif replacement:
                                    replacement = replacement[0]
                                    request = request.replace(phrase, precursor + " " + replacement)
                            elif second_replacement:
                                if len(second_replacement) > 1:
                                    return(f"Which of the following tools are you referring to? \n{', '.join(second_replacement)} \nPlease clarify your request.")
                                elif second_replacement:
                                    second_replacement = second_replacement[0]
                                    request = request.replace(phrase, precursor + " " + second_replacement)
                        elif precursor == "cook" or precursor == "prepare" or precursor == "get" or precursor == "make" or precursor == "replace":
                            replacement = ingredients
                            if len(replacement) > 1:
                                return(f"Which of the following ingredients are you referring to? \n{', '.join(replacement)} \nPlease clarify your request.")
                            elif replacement:
                                replacement = replacement[0]
                                request = request.replace(phrase, precursor + " " + replacement)
                        elif precursor == "use":
                            replacement = tools
                            if len(replacement) > 1:
                                return(f"Which of the following tools are you referring to? \n{', '.join(replacement)} \nPlease clarify your request.")
                            elif replacement:
                                replacement = replacement[0]
                                request = request.replace(phrase, precursor + " " + replacement)
                        else:
                            # Cannot determine what the user is asking for
                            return(f"I don't know what you're referring to by \"{phrase}\". Please try asking again.")
                        

                    print(f"request: {request}")
                    if "how much" in request.lower():
                        subject = self.question_handler.extract_subject_ingredient(request)
                        if not subject: 
                            return("I don't know what ingredient you're referring to. Please try asking again.")
                        if len(subject) > 1:
                            return(f"Which of the following ingredients are you referring to? \n{', '.join(subject)} \nPlease clarify your request.")
                        elif subject:
                            print(f"subject: {subject}")
                            for ingredient in self.recipe['ingredients']:
                                if ingredient['name'] == subject[0]:
                                    if ingredient['measurement']:
                                        return(f"You need {ingredient['quantity']} {ingredient['measurement']} of {ingredient['name']}")
                                    else:
                                        return(f"You need {ingredient['quantity']} {ingredient['name']}")
                            return("I don't know that ingredient. Please try asking again.")
                    elif "how long" in request.lower():
                        if self.recipe['steps'][self.current_step]['time']['duration'] != "N/A":
                            return(f"{self.recipe['steps'][self.current_step]['time']['duration']} {self.recipe['steps'][self.current_step]['time']['unit']}")
                        else:
                            return("I don't know the time required for this step.")
                    else:
                        # Actually deal with the query now
                        return(self.question_handler.build_google_search_query(request))

            case "Navigation":
                msg = self.update_step(request)
                if msg:
                    return(f"{msg}\nStep {self.current_step + 1}: {self.recipe['steps'][self.current_step]['text']}")
                else:
                    return(f"Step {self.current_step + 1}: {self.recipe['steps'][self.current_step]['text']}")
            
            case "Step":
                if any(word in request for word in method_words):
                    return(self.question_handler.return_methods(self.current_step))
                elif any(word in request for word in ingredient_words):
                    return(self.question_handler.return_ingredients(self.current_step))
                elif any(word in request for word in time_words):
                    return(self.question_handler.return_time(self.current_step))
                elif any(word in request for word in tools_words):
                    return(self.question_handler.return_tools(self.current_step))
                else:
                    return(self.question_handler.return_directions(self.current_step))