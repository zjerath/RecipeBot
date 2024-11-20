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
                step_num = self.question_handler.extract_step_number(user_query)
                print(f"request: {user_query} | step_num: {step_num}")
                if step_num > 0 and step_num <= len(self.recipe['steps']):
                    self.current_step = step_num - 1 # self.current_step is 0 indexed
                    return(f"Navigated to step {step_num} successfully.")
                else:
                    return(f"Invalid step number: this recipe has {len(self.recipe['steps'])} steps.")
            case _:
                return("Unknown navigation request type.")

    # Helper function to extract demonstrative references and their subjects
    def extract_demonstrative_reference(self, text):
        doc = self.nlp(text)
        for token in doc:
            # Check for demonstrative determiners/pronouns
            if token.lemma_ in ["this", "that", "these", "those", "it"]:
                # Look for the verb phrase that follows
                precursor_words = ["do", "make", "cook", "prepare", "get", "of", "replace"]
                if any(token.head.lemma_ == word for word in precursor_words):
                    # Get the full verb phrase including the demonstrative
                    verb_phrase = " ".join([token.head.text, token.text])
                    return (token.head.lemma_, verb_phrase)
                # Look for noun phrases
                else: 
                    return (token.head.lemma_, token.text)
        return (None, None)
    
    def extract_subject_ingredient(self, request):
        doc = self.nlp(request)
        for token in doc:
            if token.pos_ == "NOUN" and token.text.lower() in [ingredient['name'].lower() for ingredient in self.recipe['ingredients']]:
                return token.text
        return None
    
    def extract_subject_method(self, request):
        doc = self.nlp(request)
        for token in doc:
            if token.pos_ == "VERB" and token.text.lower() in [method.lower() for method in self.recipe['methods']]:
                return token.text
        return None
    
    def extract_subject_tool(self, request):
        doc = self.nlp(request)
        for token in doc:
            if token.pos_ == "NOUN" and token.text.lower() in [tool.lower() for tool in self.recipe['tools']]:
                return token.text
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
                    dem_word, dem_subject = self.extract_demonstrative_reference(request)
                    print(f"dem_word: {dem_word} | dem_subject: {dem_subject}")
                    
                    if dem_subject:
                        # Get the current step's text
                        current_step_text = self.recipe['steps'][self.current_step]['text']
                        # Replace the demonstrative reference with the subject from current step
                        if dem_word == "do":
                            return(current_step_text)
                        elif dem_word == "cook" or dem_word == "prepare" or dem_word == "get" or dem_word == "make" or dem_word == "of" or dem_word == "replace":
                            replacement = self.extract_subject_ingredient(current_step_text)
                            if replacement:
                                request = request.replace(dem_subject, dem_word + " " + replacement)
                        elif dem_word == "use":
                            replacement = self.extract_subject_tool(current_step_text)
                            if replacement:
                                request = request.replace(dem_subject, dem_word + " " + replacement)
                        else:
                            # Cannot determine what the user is asking for
                            return(f"I don't know what you're referring to by \"{dem_word}\". Please try asking again.")
                    if "how much" in request.lower() or "how many" in request.lower():
                        subject = self.extract_subject_ingredient(request)
                        print(f"subject: {subject}")
                        found = False
                        for ingredient in self.recipe['ingredients']:
                            if ingredient['name'] == subject:
                                if ingredient['measurement']:
                                    return(f"You need {ingredient['quantity']} {ingredient['measurement']} of {ingredient['name']}")
                                else:
                                    return(f"You need {ingredient['quantity']} {ingredient['name']}")
                                found = True
                        if not found:   
                            return("I don't know that ingredient. Please try asking again.")
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