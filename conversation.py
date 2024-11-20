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

    # Function to extract step number
    def extract_step_number(self, request):
        '''
        TO DO:
            implement extraction of ordinal numbers & conversion to corresponding numeric values
        Example usage:
            print(extract_step_number("Go to step 42"))  # Output: 42
            print(extract_step_number("navigate to the 5th step"))  # Output: 5
        '''
        # Regular expressions to capture the nth step
        navigation_patterns = [
            r"\b(?:go to|navigate to|move to|proceed to|take me to)\b.*\b(\d+)(?:st|nd|rd|th)?\b.*\b(?:step|instruction)\b.*",
            r"\b(?:go to|navigate to|move to|proceed to|take me to)\b \b(?:step|instruction)\b \b(\d+)\b.*", #[a-zA-Z]+
        ]

        for pattern in navigation_patterns:
            match = re.search(pattern, request, re.IGNORECASE)
            if match:
                step = match.group(1)  # Capture the step part
                print(f"Request: {request} | Step: {int(step)}")
                return int(step)
                # # Check if it's a digit and return as an integer
                # if step.isdigit():
                #     return int(step)
                # # Otherwise, attempt to convert ordinal to a number
                # return self.ordinal_to_number(step.lower())
        return None  # Return None if no step is found

    
    def detect_navigation_type(self, user_query):
        '''
        Given a user (navigation) request, determine whether they are asking to proceed to:
        - the next step
        - previous step
        - current step (repeat)
        - Nth step

        Example usage:
            user_input = "Can we go to the next step?"
            print(detect_navigation(user_input))  # Output: "Next Step"
        '''
        if re.search(r"\b(?:go to|navigate to|move to|proceed to|take me to)\b.*\b(\d+)(?:st|nd|rd|th)?\b.*\b(?:step|instruction)?\b.*", user_query, re.IGNORECASE) or re.search(r"\b(?:go to|navigate to|move to|proceed to|take me to)\b \b(?:step|instruction)\b \b(\d+)\b.*", user_query, re.IGNORECASE):
            return "Nth"
        elif re.search(r".*\b(next|proceed|move|advance)\b.*", user_query, re.IGNORECASE):
            return "Next"
        elif re.search(r".*\b(previous|go back|return|back to|last|prior)\b.*", user_query, re.IGNORECASE):
            return "Previous"
        elif re.search(r".*\b(repeat|redo|again|once more|do over)\b.*", user_query, re.IGNORECASE):
            return "Current"
        else:
            return "Unknown"

    
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
        
        navigation_type = self.detect_navigation_type(user_query)
        
        # return appropriate index corresponding to user_query category
        match navigation_type:
            case 'Current':
                pass
            case 'Previous':
                if self.current_step > 0:
                    self.current_step -= 1
                    return(f"Navigated to step {self.current_step + 1} successfully.")
                else:
                    return(f"Unable to navigate to previous step as we're already at the first step.")
            case 'Next':
                if self.current_step < len(self.recipe['steps']) - 1: 
                    self.current_step += 1
                    return(f"Navigated to step {self.current_step + 1} successfully.")
                else:
                    return(f"Unable to navigate to next step as we're already at the last step.")
            case 'Nth':
                # TO DO: better step_num extraction logic
                # step_num = [int(s) for s in re.findall(r'\d+', user_query)][0]
                step_num = self.extract_step_number(user_query)
                if step_num > 0 and step_num <= len(self.recipe['steps']):
                    self.current_step = step_num - 1 # self.current_step is 0 indexed
                    return(f"Navigated to step {step_num} successfully.")
                else:
                    return(f"Unable to navigate to step {step_num} as it is not within the range of 1 to {len(self.recipe['steps'])}.")
            case _:
                return("Unknown navigation request type.")
    
    '''
    Basic request handling for:
    - General requests 
    - Recipe navigation requests
    - Requesting step-specific parameters

    To do:
    - handle step navigation and step specific parameters simultaneously?
    '''
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
                    phrase = f"{precursor} {demonstrative} {reference}"
                    print(f"precursor: {precursor} | demonstrative: {demonstrative} | reference: {reference}")
                    
                    if demonstrative:
                        # Get the current step's text
                        current_step_text = self.recipe['steps'][self.current_step]['text']

                        
                        if not reference: 
                            reference = ""
                        if not precursor:
                            precursor = ""

# Reference replacements
                        if reference == "ingredient":
                            replacement = self.extract_subject_ingredient(current_step_text)
                            request = request.replace(phrase, precursor + " " + replacement)
                        elif reference == "tool":
                            replacement = self.extract_subject_tool(current_step_text)
                            request = request.replace(phrase, precursor + " " + replacement)
                        elif reference == "method":
                            replacement = self.extract_subject_method(current_step_text)
                            request = request.replace(phrase, precursor + " " + replacement)
                        
                        # Precursor replacements
                        elif precursor == "do":
                            return(current_step_text)
                        elif precursor == "of":
                            replacement = self.extract_subject_ingredient(current_step_text)
                            second_replacement = self.extract_subject_tool(current_step_text)
                            if replacement: 
                                request = request.replace(phrase, precursor + " " + replacement)
                            elif second_replacement:
                                request = request.replace(phrase, precursor + " " + second_replacement)
                        elif precursor == "cook" or precursor == "prepare" or precursor == "get" or precursor == "make" or precursor == "replace":
                            replacement = self.extract_subject_ingredient(current_step_text)
                            if len(replacement) > 1:
                                return(f"Which of the following ingredients are you referring to? {', '.join(replacement)}?")
                            elif replacement:
                                request = request.replace(phrase, precursor + " " + replacement)
                        elif precursor == "use":
                            replacement = self.extract_subject_tool(current_step_text)
                            if len(replacement) > 1:
                                return(f"Which of the following tools are you referring to? {', '.join(replacement)}?")
                            elif replacement:
                                request = request.replace(phrase, precursor + " " + replacement)
                        else:
                            # Cannot determine what the user is asking for
                            return(f"I don't know what you're referring to by \"{phrase}\". Please try asking again.")
                        

                    print(f"request: {request}")
                    if "how much" in request.lower():
                        subject = self.extract_subject_ingredient(request)
                        if len(subject) > 1:
                            return(f"Which of the following ingredients are you referring to? {', '.join(subject)}?")
                        elif subject:
                            print(f"subject: {subject}")
                            for ingredient in self.recipe['ingredients']:
                                if ingredient['name'] == subject:
                                    found = True
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
                self.update_step(request)
                return(f"Step {self.current_step + 1}: {self.recipe['steps'][self.current_step]['text']}")
            
            case "Step":
                if any(word in request for word in method_words):
                    return(self.question_handler.return_methods(self.current_step))
                elif any(word in request for word in ingredient_words):
                    return(self.question_handler.return_ingredients(self.current_step))
                elif any(word in request for word in time_words):
                    return(self.question_handler.return_steps(self.current_step))
                elif any(word in request for word in tools_words):
                    return(self.question_handler.return_tools(self.current_step))
                else:
                    return("I don't know that information for the current step of this recipe. Please try asking again.")