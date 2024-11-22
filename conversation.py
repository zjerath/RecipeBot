import re
from question_handler import QuestionHandler
from constants import ordinal_base, ordinal_tens
import spacy

'''
Conversation class consisting of:
    - recipe object
    - question history
    - current step
    - response handling -> delegate to QuestionHandler()
'''

class Conversation:
    # TO DO: track current subject for identifying subject when user specifies vague pronoun (this, that)
    # can start with extracting subject/relevant nouns in corresponding step[current_step].text
    def __init__(self, recipe):
        self.recipe = recipe
        self.current_step = 0
        self.question_history = []
        self.question_handler = QuestionHandler(recipe)
        self.nlp = spacy.load("en_core_web_lg")

    # Function to convert any ordinal word to a number
    def ordinal_to_number(self, ordinal):
        # Check for base ordinals (e.g., "third" or "sixteenth")
        if ordinal in ordinal_base:
            return ordinal_base[ordinal]
        # Check for tens ordinals (e.g., "twentieth")
        elif ordinal in ordinal_tens:
            return ordinal_tens[ordinal]
        # Handle composite ordinals like "twenty-first"
        else:
            # Split by hyphen, e.g., "twenty-first" -> ["twenty", "first"]
            parts = ordinal.split('-')
            if len(parts) == 2 and parts[0] in ordinal_tens and parts[1] in ordinal_base:
                return ordinal_tens[parts[0]] + ordinal_base[parts[1]]
        # Return None if no match is found
        return None
    
    def update_step(self, user_query):
        '''
        Update the current step accordingly given the user query.
        
        Parameters:
            user_query: a user command specifying which step to navigate to
                        the navigation request may be classified into the following navigation types:
                            Current - stay at current step, typically used for repeat requests
                            Previous - navigate to previous step
                            Next - proceed to next step
                            Nth - navigate to any arbitrary step in the recipe
        '''
        
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

    # Helper function to extract demonstrative references and their subjects
    def extract_demonstrative_reference(self, text):
        text = text.lower()
        precursor_words = ["do", "make", "cook", "prepare", "get", "of", "replace"]
        demonstratives = ["this", "that", "these", "those", "it"]
        reference_words = ["step", "ingredient", "tool", "method"]
        
        # Split text into words
        words = text.split()
        
        for i in range(len(words)):
            # Check if word is a demonstrative
            if words[i] in demonstratives:
                # Check word before for precursor
                if i > 0 and words[i-1] in precursor_words:
                    # Check if there's a reference word after
                    if i+1 < len(words) and words[i+1] in reference_words:
                        return (words[i-1], words[i], words[i+1])
                    return (words[i-1], words[i], None)
                # Check word after for precursor 
                elif i+1 < len(words) and words[i+1] in precursor_words:
                    # Check if there's a reference word after precursor
                    if i+2 < len(words) and words[i+2] in reference_words:
                        return (words[i+1], words[i], words[i+2])
                    return (words[i+1], words[i], None)
                # No precursor found
                else:
                    # Check if there's a reference word after
                    if i+1 < len(words) and words[i+1] in reference_words:
                        return (None, words[i], words[i+1])
                    return (None, words[i], None)
                    
        return (None, None, None)
    
    def extract_subject_ingredient(self, request):
        request = request.lower()
        ingredients = [ingredient['name'].lower() for ingredient in self.recipe['ingredients']]
        found_ingredients = []
        for ingredient in ingredients:
            if ingredient in request:
                found_ingredients.append(ingredient)
        if found_ingredients:
            return found_ingredients
        else:
            return None
    
    def extract_subject_method(self, request):
        request = request.lower()
        methods = [method.lower() for method in self.recipe['methods']]
        found_methods = []
        for method in methods:
            if method in request:
                found_methods.append(method)
        if found_methods:
            return found_methods
        else:
            return None
    
    def extract_subject_tool(self, request):
        request = request.lower()
        tools = [tool.lower() for tool in self.recipe['tools']]
        found_tools = []
        for tool in tools:
            if tool in request:
                found_tools.append(tool)
        if found_tools:
            return found_tools
        else:
            return None
    
    def handle_request(self, request):
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
                    precursor, demonstrative, reference = self.extract_demonstrative_reference(request)
                    if not reference: 
                        reference = ""
                    if not precursor:
                        precursor = ""
                    phrase = f"{precursor} {demonstrative} {reference}".strip()
                    print(f"precursor: {precursor} | demonstrative: {demonstrative} | reference: {reference}")
                    
                    if demonstrative:
                        # Get the current step's text
                        current_step_text = self.recipe['steps'][self.current_step]['text']

                        ingredients = self.extract_subject_ingredient(current_step_text)
                        methods = self.extract_subject_method(current_step_text)
                        tools = self.extract_subject_tool(current_step_text)

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
                        subject = self.extract_subject_ingredient(request)
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
                    '''
                    TO DO; check if user specified specific method in their time request
                    extract time info for that specific method
                        find method in method list, extract index, return time info at corresponding index
                    '''
                    return(self.question_handler.return_time(self.current_step))
                elif any(word in request for word in tools_words):
                    return(self.question_handler.return_tools(self.current_step))
                else:
                    return(self.question_handler.return_directions(self.current_step))
                    # return("I don't know that information for the current step of this recipe. Please try asking again.")