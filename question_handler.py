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
    
    def determine_request_type(self, request):
        '''
        Determine whether a user request is one of the following:
            General
            Navigation
            Step-specific
        '''
        request_type_keywords = {
            "General": ["how to", "how do"],
            "Navigation": ["go", "proceed", "take me", "move", "navigate"],
            "Step": ["for this step"]
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
                ingredients_list = [f"{i+1}. {ingredient}" for i, ingredient in enumerate(self.recipe['steps'][step]['ingredients'])]
                return f"Here are the ingredients used in step {step + 1} of {self.recipe['title']}:\n" + "\n".join(ingredients_list)

    def return_tools(self, step=None):
        match step:
            case None:
                tools_list = [f"{i+1}. {tool}" for i, tool in enumerate(self.recipe['tools'])]
                return f"Here are the tools used in {self.recipe['title']}:\n" + "\n".join(tools_list)
            case _: # return tools for specific step
                tools_list = [f"{i+1}. {tool}" for i, tool in enumerate(self.recipe['steps'][step]['tools'])]
                return f"Here are the tools used in step {step + 1} of {self.recipe['title']}:\n" + "\n".join(tools_list)
        
    def return_methods(self, step=None):
        match step:
            case None:
                methods_list = [f"{i+1}. {method}" for i, method in enumerate(self.recipe['methods'])]
                return f"Here are the methods used in {self.recipe['title']}:\n" + "\n".join(methods_list)
            case _: # return methods for specific step 
                methods_list = [f"{i+1}. {method}" for i, method in enumerate(self.recipe['steps'][step]['methods'])]
                return f"Here are the methods used in step {step + 1} of {self.recipe['title']}:\n" + "\n".join(methods_list)

    # To do: format this better
    def return_time(self, step):
        step_time_info = self.recipe['steps'][step]['time']
        return f"Carry out this step for {step_time_info['duration']} {step_time_info['unit']}{'s' if step_time_info['duration'] != 1 else ''}"