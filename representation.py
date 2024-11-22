class Ingredient:
    """
    Ingredients 
        Ingredient name
        Quantity
        Measurement (cup, teaspoon, pinch, etc.)
        (optional) Descriptor (e.g. fresh, extra-virgin)
        (optional) Preparation (e.g. finely chopped)
    """
    def __init__(self, name, quantity=None, measurement=None, descriptor=None, preparation=None):
        self.name = name
        self.quantity = quantity
        self.measurement = measurement
        self.descriptor = descriptor
        self.preparation = preparation

class Step:
    """
    Steps – parse the directions into a series of steps that each consist of ingredients, tools, methods, and times
    """
    def __init__(self, step_number, text, ingredients=None, tools=None, methods=None, time=None):
        self.step_number = step_number
        self.text = text
        self.ingredients = ingredients or []
        self.tools = tools or []
        self.methods = methods or []
        self.time = time

class Recipe:
    def __init__(self, title, raw_ingredients, ingredients, steps):
        self.title = title
        self.raw_ingredients = raw_ingredients
        self.ingredients = ingredients
        self.steps = steps
