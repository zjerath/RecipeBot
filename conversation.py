import re
from question_handler import QuestionHandler
from constants import ordinal_base, ordinal_tens

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
                    print(f"Navigated to step {self.current_step + 1} successfully.")
                else:
                    print(f"Unable to navigate to previous step as we're already at the first step.")
            case 'Next':
                if self.current_step < len(self.recipe['steps']) - 1: 
                    self.current_step += 1
                    print(f"Navigated to step {self.current_step + 1} successfully.")
                else:
                    print(f"Unable to navigate to next step as we're already at the last step.")
            case 'Nth':
                # TO DO: better step_num extraction logic
                # step_num = [int(s) for s in re.findall(r'\d+', user_query)][0]
                step_num = self.extract_step_number(user_query)
                if step_num > 0 and step_num <= len(self.recipe['steps']):
                    self.current_step = step_num - 1 # self.current_step is 0 indexed
                    print(f"Navigated to step {step_num} successfully.")
                else:
                    print(f"Unable to navigate to step {step_num} as it is not within the range of 1 to {len(self.recipe['steps'])}.")
            case _:
                print("Unknown navigation request type.")
    
    '''
    Basic request handling for:
    - General requests 
    - Recipe navigation requests
    - Requesting step-specific parameters

    To do:
    - handle step navigation and step specific parameters simultaneously?
    '''
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
                        print(self.question_handler.return_ingredients())
                    elif any(word in request for word in step_words):
                        print(self.question_handler.return_steps())
                    elif any(word in request for word in tools_words):
                        print(self.question_handler.return_tools())
                    elif any(word in request for word in method_words):
                        print(self.question_handler.return_methods())
                    else:
                        print("I don't know that information about this recipe. Please try asking again.")
                # If the question is not about the recipe, search Google
                else:
                    print(self.question_handler.build_google_search_query(request))
            case "Navigation":
                self.update_step(request)
            case "Step":
                if any(word in request for word in method_words):
                    print(self.question_handler.return_methods(self.current_step))
                elif any(word in request for word in ingredient_words):
                    print(self.question_handler.return_ingredients(self.current_step))
                elif any(word in request for word in time_words):
                    print(self.question_handler.return_steps(self.current_step))
                elif any(word in request for word in tools_words):
                    print(self.question_handler.return_tools(self.current_step))
                else:
                    print("I don't know that information for the current step of this recipe. Please try asking again.")