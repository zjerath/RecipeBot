import re

class QuestionHandler:
    """
    QuestionHandler module contains generic functions for handling user requests about a recipe.
    This module contains general question-answering logic not specific to conversation state (i.e. no step updating or conversation history)
    Conversation-specific logic is handled in the Conversation module.
    """
    def __init__(self, recipe):
        self.recipe = recipe
    
    def build_google_search_query(self, question):
        """
        Build appropriate search query for a user's request.
        """
        return f"https://www.google.com/search?q={question.replace(' ', '+')}"

    # Function to extract step number from user navigation request
    def extract_step_number(self, request):
        """
        Extract the step number from a user request.
        Assumes step number is specified numerically, or first/last keyword is specified.
        Example usage:
            print(extract_step_number("Go to step 42"))  # Output: 42
            print(extract_step_number("navigate to the 5th step"))  # Output: 5
            print(extract_step_number("go to the first step"))  # Output: 1
        """

        # This function will only be called for Nth step navigation requests
        # So, just extract number, or first/last keywords
        if 'first' in request.lower():
            return 1
        if 'last' in request.lower():
            return len(self.recipe["steps"])
        step_numbers = re.findall(r'\d+', request)
        if step_numbers:
            return int(step_numbers[0])
        return None
    
    def detect_navigation_type(self, user_query):
        """
        Given a user navigation request, determine whether they are asking to proceed to:
        - the next step
        - previous step
        - current step (repeat)
        - Nth step

        Example usage:
            user_input = "Can we go to the next step?"
            print(detect_navigation(user_input))  # Output: "Next"
        """
        nth_step_patterns = [
            r"\b(?:go to|navigate to|move to|proceed to|take me to)\b.*\b((\d+)(?:st|nd|rd|th)?|first|last)\b.*\b(?:step|instruction)?\b.*",
            r"\b(?:go to|navigate to|move to|proceed to|take me to)\b \b(?:step|instruction)\b \b(\d+)\b.*",
            r"step \d+"
        ]
        for pattern in nth_step_patterns:
            if re.search(pattern, user_query, re.IGNORECASE):
                return "Nth"
        if re.search(r".*\b(next|proceed|move|advance)\b.*", user_query, re.IGNORECASE):
            return "Next"
        elif re.search(r".*\b(previous|go back|return|back to|last|prior)\b.*", user_query, re.IGNORECASE):
            return "Previous"
        elif re.search(r".*\b(repeat|redo|again|once more|do over)\b.*", user_query, re.IGNORECASE):
            return "Current"
        else:
            return "Unknown"

    
    def determine_request_type(self, request):
        """
        Determine whether a user request is one of the following:
            General
            Navigation
            Step-specific
        """
        request_type_keywords = {
            "General": ["how to", "how do", "what is", "steps"],
            "Navigation": ["go", "proceed", "take me", "move", "navigate", "next", "previous", 'repeat', 'again'],
            "Step": ["step", "long", "time"] # time requests typically ask about step-specific methods  
        }

        for request_type in request_type_keywords:
            if any(i.lower() in request.lower() for i in request_type_keywords[request_type]):
                if request_type == "Step" and re.search(r"step \d+", request, re.IGNORECASE): # any request involving step & number should be navigation
                    return "Navigation"
                return request_type
        # if no request type match found, classify as general request
        return "General"
        

    def return_steps(self):
        """
        Return all the steps in this instance's recipe object.
        """
        steps_str = f"Here are the steps to make {self.recipe['title']}: \n"
        for step in self.recipe['steps']:
            steps_str += f"{step['step_number']}. {step['text']}\n"
        return steps_str

    def return_ingredients(self, step=None):
        match step:
            case None:
                ingredients_list = [f"{i+1}. {ingredient['name']}" for i, ingredient in enumerate(self.recipe['ingredients'])]
                return f"Here are the ingredients used in {self.recipe['title']}:\n" + "\n".join(ingredients_list)
            case _: # return ingredients for specific step
                if self.recipe['steps'][step]['ingredients']:
                    ingredients_list = [f"{i+1}. {ingredient}" for i, ingredient in enumerate(self.recipe['steps'][step]['ingredients'])]
                    return f"Here are the ingredients used in step {step + 1} of {self.recipe['title']}:\n" + "\n".join(ingredients_list)
                return f"There are no ingredients for this step."

    def return_tools(self, step=None):
        """
        Return all tools required in this instance's recipe object.
        """
        match step:
            case None:
                tools_list = [f"{i+1}. {tool}" for i, tool in enumerate(self.recipe['tools'])]
                return f"Here are the tools used in {self.recipe['title']}:\n" + "\n".join(tools_list)
            case _: # return tools for specific step
                if self.recipe['steps'][step]['tools']:
                    tools_list = [f"{i+1}. {tool}" for i, tool in enumerate(self.recipe['steps'][step]['tools'])]
                    return f"Here are the tools used in step {step + 1} of {self.recipe['title']}:\n" + "\n".join(tools_list)
                return f"There are no tools required for this step."
        
    def return_methods(self, step=None):
        """
        Return all methods utilized in this instance's recipe object.
        """
        match step:
            case None:
                methods_list = [f"{i+1}. {method}" for i, method in enumerate(self.recipe['methods'])]
                return f"Here are the methods used in {self.recipe['title']}:\n" + "\n".join(methods_list)
            case _: # return methods for specific step 
                if self.recipe['steps'][step]['methods']:
                    methods_list = [f"{i+1}. {method}" for i, method in enumerate(self.recipe['steps'][step]['methods'])]
                    return f"Here are the methods used in step {step + 1} of {self.recipe['title']}:\n" + "\n".join(methods_list)
                return f"There are no methods for this specific step."
    
    def return_directions(self, step):
        """
        Return the recipe directions for a specific step.
        """
        step_directions_info = self.recipe['steps'][step]['text']
        return f"Here are the directions for this step: {step_directions_info}"

    def return_time(self, step):
        """
        Return time/duration information regarding how long to carry out a specific step.
        If step directions include qualitative and numeric time criteria, this function will return both.
        Example:
            Step 4: Bake in the preheated oven until evenly toasted, 7 minutes.
                Q: How long should I bake for?
                A: Bake until evenly toasted, for about 7 minutes.
        """
        step_time_info = self.recipe['steps'][step]['time']
        duration_info = step_time_info['duration']
        condition_info = step_time_info['condition']
        if duration_info is None and condition_info is None:
            return "There are no time specifications for the methods of this step."
        
        # return time for corresponding methods, if they exist
        step_methods = self.recipe['steps'][step]['methods']
        
        if duration_info and condition_info: # if time duration & qualitative description specified
            return f"{'Carry out this step' if not step_methods else ' and '.join(step_methods)} {condition_info}, {'for about ' + duration_info}"
        elif duration_info: # only time duration specified
            return f"{'Carry out this step' if not step_methods else ' and '.join(step_methods)} {'for ' + duration_info}"
        else: # only qualitative description specified
            return f"{'Carry out this step' if not step_methods else ' and '.join(step_methods)} {condition_info}"
        
    def extract_demonstrative_reference(self, text):
        """
        Helper function to extract demonstrative references and their subjects
        """
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
        """
        For vague queries concerning ingredients about a particular recipe step, 
        this function extracts the relevant ingredients that the user could be referring to.
        """
        request = request.lower()
        ingredients = [ingredient['name'].lower() for ingredient in self.recipe['ingredients']]
        found_ingredients = []
        for ingredient in ingredients:
            if ingredient in request:
                found_ingredients.append(ingredient)
        return found_ingredients
    
    def extract_subject_method(self, request):
        """
        For vague queries concerning methods about a particular recipe step, 
        this function extracts the relevant methods that the user could be referring to.
        """
        request = request.lower()
        methods = [method.lower() for method in self.recipe['methods']]
        found_methods = []
        for method in methods:
            if method in request:
                found_methods.append(method)
        return found_methods
    
    def extract_subject_tool(self, request):
        """
        For vague queries concerning tools about a particular recipe step, 
        this function extracts the relevant tools that the user could be referring to.
        """
        request = request.lower()
        tools = [tool.lower() for tool in self.recipe['tools']]
        found_tools = []
        for tool in tools:
            if tool in request:
                found_tools.append(tool)
        return found_tools