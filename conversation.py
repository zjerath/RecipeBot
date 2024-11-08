import re
from question_handler import QuestionHandler

'''
Conversation class consisting of:
    - recipe object
    - question history
    - current step
    - response handling -> delegate to QuestionHandler()
'''

class Conversation:
    def __init__(self, recipe):
        self.recipe = recipe
        self.current_step = 0
        self.question_history = []
        self.question_handler = QuestionHandler(recipe)

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
                step_num = [int(s) for s in re.findall(r'\d+', user_query)][0]
                if step_num > 0 and step_num <= len(self.recipe['steps']):
                    self.current_step = step_num - 1 # self.current_step is 0 indexed
                    print(f"Navigated to step {step_num} successfully.")
                else:
                    print(f"Unable to navigate to step {step_num} as it is not within the range of 1 to {len(self.recipe['steps'])}.")
    
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