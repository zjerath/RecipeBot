import re

class QuestionHandler:
    def __init__(self, recipe):
        self.recipe = recipe
    
    def build_google_search_query(self, question):
        return f"https://www.google.com/search?q={question.replace(' ', '+')}"

    # detect general self.recipe questions, or how to
    # i.e. "show me the ingredients list", "how to preheat oven"
    def is_general_question(self, response):
        return True

    # detect navigation requests 
    # i.e. "go to next step"
    def is_navigation_request(self, response):
        return True

    # detect whether question is asking about parameters for a particular step
    # i.e. "what are the ingredients for this step"
    def is_step_specific_question(self, response):
        return True
    
    # Function to extract step number from user navigation request
    def extract_step_number(self, request):
        '''
        TO DO:
            implement extraction of ordinal numbers & conversion to corresponding numeric values
        Example usage:
            print(extract_step_number("Go to step 42"))  # Output: 42
            print(extract_step_number("navigate to the 5th step"))  # Output: 5
        '''

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
    
        # # Regular expressions to capture the nth step
        # navigation_patterns = [
        #     r"\b(?:go to|navigate to|move to|proceed to|take me to)\b.*\b(\d+)(?:st|nd|rd|th)?\b.*\b(?:step|instruction)\b.*",
        #     r"\b(?:go to|navigate to|move to|proceed to|take me to)\b \b(?:step|instruction)\b \b(\d+)\b.*", #[a-zA-Z]+
        # ]
        
        # for pattern in navigation_patterns:
        #     match = re.search(pattern, request, re.IGNORECASE)
        #     if match:
        #         step = match.group(1)  # Capture the step part
        #         print(f"Request: {request} | Step: {int(step)}")
        #         return int(step)
                # # Check if it's a digit and return as an integer
                # if step.isdigit():
                #     return int(step)
                # # Otherwise, attempt to convert ordinal to a number
                # return self.ordinal_to_number(step.lower())
        # return None  # Return None if no step is found
    
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
        if re.search(r"\b(?:go to|navigate to|move to|proceed to|take me to)\b.*\b((\d+)(?:st|nd|rd|th)?|first|last)\b.*\b(?:step|instruction)?\b.*", user_query, re.IGNORECASE) or re.search(r"\b(?:go to|navigate to|move to|proceed to|take me to)\b \b(?:step|instruction)\b \b(\d+)\b.*", user_query, re.IGNORECASE):
            return "Nth"
        elif re.search(r".*\b(next|proceed|move|advance)\b.*", user_query, re.IGNORECASE):
            return "Next"
        elif re.search(r".*\b(previous|go back|return|back to|last|prior)\b.*", user_query, re.IGNORECASE):
            return "Previous"
        elif re.search(r".*\b(repeat|redo|again|once more|do over)\b.*", user_query, re.IGNORECASE):
            return "Current"
        else:
            return "Unknown"

    
    def determine_request_type(self, request):
        '''
        Determine whether a user request is one of the following:
            General
            Navigation
            Step-specific
        '''
        request_type_keywords = {
            "General": ["how to", "how do", "what is"],
            "Navigation": ["go", "proceed", "take me", "move", "navigate", "next", "previous", 'repeat', 'again'],
            "Step": ["step", "long", "time"] # time requests typically ask about step-specific methods  
        }

        for request_type in request_type_keywords:
            if any(i.lower() in request.lower() for i in request_type_keywords[request_type]):
                return request_type
        # if no request type match found, classify as general request
        return "General"
        

    def return_steps(self):
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
        step_directions_info = self.recipe['steps'][step]['text']
        return f"Here are the directions for this step: {step_directions_info}"

    # To do: format this better
    def return_time(self, step):
        step_time_info = self.recipe['steps'][step]['time']
        if step_time_info['duration'] == "N/A" or step_time_info['unit'] == "N/A":
            return "There are no time specifications for the methods of this step."
        
        # return time for corresponding methods, if they exist
        step_methods = self.recipe['steps'][step]['methods']
        if step_methods:
            method_str = " and ".join(step_methods)
            return f"{method_str} for {step_time_info['duration']} {step_time_info['unit']}{'s' if step_time_info['duration'] != 1 else ''}"
        
        return f"Carry out this step for {step_time_info['duration']} {step_time_info['unit']}{'s' if step_time_info['duration'] != 1 else ''}"