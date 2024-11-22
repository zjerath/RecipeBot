import re
import json
import spacy
import requests
import Levenshtein
from bs4 import BeautifulSoup
from representation import Ingredient, Step, Recipe

nlp = spacy.load('en_core_web_lg')

def fetch_recipe(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        raise ValueError("Could not fetch the webpage. Please check the URL.")
    
def extract_json_ld(soup):
    script_tag = soup.find('script', {'type': 'application/ld+json'})
    if script_tag:
        json_data = json.loads(script_tag.string)
        # check if JSON-LD is a list
        if isinstance(json_data, list):
            for entry in json_data:
                # get recipe if in list
                if "Recipe" in entry.get("@type", []):
                    return entry
        # otherwise get recipe
        elif "Recipe" in json_data.get("@type", []):
            return json_data
    return None

def parse_ingredients(json_data):
    ingredients = []
    raw_ingredients = []
    for item in json_data.get("recipeIngredient", []):
        raw_ingredients.append(item.strip())
        quantity = None
        descriptor = None
        preparation = None
        if ", or to taste" in item.lower():
            # handle "to taste" or ", or to taste"
            item = item.replace(", or to taste", "").strip()
            quantity = "to taste"
        if "to taste" in item.lower():
            item = item.replace("to taste", "").strip()
            quantity = "to taste"
        # handle measurements in parentheses
        parenthesis_pattern = r"(\d+/\d+|\d+\.\d+|\d+)?\s*\((.*?)\)\s*(.*)"
        match_parenthesis = re.match(parenthesis_pattern, item)
        if match_parenthesis:
            # extract name, quantity, measurement
            name = match_parenthesis.group(3).strip()
            quantity = match_parenthesis.group(1).strip() if match_parenthesis.group(1) else "1"
            measurement = match_parenthesis.group(2).strip()
        # regex to extract name, quantity (fractional or decimal), and measurement
        else:
            pattern = r"(\d+/\d+|\d+\.\d+|\d+)?\s*(\b(?:cup|cups|teaspoon|teaspoons|tbsp|tablespoon|tablespoons|oz|ounce|ounces|pound|pounds|g|grams|kg|kilograms|ml|milliliters|l|liters|handful|pinch|pinches|dash|dashes|slice|slices|clove|cloves|package|packages|piece|pieces|milligrams|tsp|quart|quarts|pint|pints|fluid ounce|fluid ounces|gal|gallon|gallons|dl)\b)?\s*(.*)"
            match = re.match(pattern, item)
            name = match.group(3).strip() if match and match.group(3) else item.strip()
            prev = quantity
            quantity = match.group(1).strip() if match and match.group(1) else prev
            measurement = match.group(2).strip() if match and match.group(2) else None
        # regex for descriptors and preparation
        descriptor_pattern = r"\b(fresh|extra-virgin|dehydrated|heirloom|aged|low-fat|reduced-fat|lean|package|packages|packaged|packed|box|boxed|jar|jarred|jars|ripe|can|cans|canned|frozen|organic|large|small|medium|smoked|thick-cut|thinly|boneless|skinless|bone-in)\b"
        descriptor_match = re.search(descriptor_pattern, name.lower())
        if descriptor_match:
            descriptor = descriptor_match.group(0).strip()
            name = name.replace(descriptor, "").strip()
        preparation_pattern = r"\b(finely chopped|chopped|shredded|divided|finely shredded|minced|sliced|diced|grated|ground|julienned|peeled|squeezed|dried|roughly chopped|roughly diced|pureed|smashed|zested|beaten|marinated|mashed|sliced thinly|halved|quartered|cut into chunks|brushed|trimmed|cored|cubed|butterflied|crushed)\b"
        preparation_match = re.search(preparation_pattern, name.lower())
        if preparation_match:
            preparation = preparation_match.group(0).strip()
            name = name.replace(preparation, "").strip()
        # format ingredient
        ingredient = Ingredient(name, quantity, measurement, descriptor, preparation)
        ingredients.append(ingredient)
    return raw_ingredients, ingredients

# parse time info for a given step
def parse_time(sentence):   
    # Patterns to match durations and conditional phrases
    time_patterns = [
        r"\d+\s*(?:more)?\s*(?:second[s]?|minute[s]?|hour[s]?|sec|min|hr[s]?)",  # Numeric durations with units
        r"about\s+\d+\s*(?:second[s]?|minute[s]?|hour[s]?)",         # Approximate durations
        r"for\s+\d+\s*(?:second[s]?|minute[s]?|hour[s]?)"            # 'for X time'
    ] 

    # Patterns to match conditions
    condition_patterns = [
        r"until\s+[\w\s]+",        # Conditions like 'until golden brown'
        r"once\s+[\w\s]+",         # Conditions like 'once dissolved'
        r"when\s+[\w\s]+"          # Conditions like 'when bubbly'
    ] 

    # Compile the patterns
    time_regex = re.compile("|".join(time_patterns), re.IGNORECASE)
    condition_regex = re.compile("|".join(condition_patterns), re.IGNORECASE)

    # Find all matches
    times = time_regex.findall(sentence)
    conditions = condition_regex.findall(sentence)

    # Extract structured results
        # duration : time value (for 10 minutes)
        # condition : condition value (until brown)
    time_info = {} 
    for time in times:
        cleaned_time = re.sub(r"^(for|about)\s+", "", time, flags=re.IGNORECASE)
        time_info['duration'] = cleaned_time.strip()
    if not times: 
        time_info['duration'] = None
    for condition in conditions:
        # Remove the keywords ('until', 'once', 'when') from the matched condition
        # cleaned_condition = re.sub(r"^(until|once|when)\s+", "", condition, flags=re.IGNORECASE)
        time_info['condition'] = condition.strip()
    if not conditions:
        time_info['condition'] = None

    return time_info

def parse_steps(json_data, ingredient_names):
    steps = []
    instructions = json_data.get("recipeInstructions", [])
    step_counter = 1
    for step in instructions:
        text = step.get("text", "").strip()
        # split sentences using regex and spacy
        doc = nlp(text)
        sentences = []
        for sent in doc.sents:
            sub_sentences = re.split(r'[;]', sent.text)
            sub_sentences = [sub_sentence.strip() for sub_sentence in sub_sentences if sub_sentence.strip()]
            sentences.extend(sub_sentences)
        for sub_text in sentences:
            if not sub_text:
                continue
            # regex for tools and methods
            tools_pattern = r"\b(oven|pot|skillet|baking pan|bowl|plate|aluminum foil|foil|tray|sheet|whisk|spatula|strainer|ladle|colander|saucepan|grater|microplane|peeler|tongs|mortar|pestle|slotted spoon|mandoline|rolling pin|measuring cup|measuring spoon|baster|mixing bowl|blender|pressure cooker|air fryer)\b"
            tools = list(set(re.findall(tools_pattern, sub_text.lower())))
            methods_pattern = r"\b(preheat|boil|cook|stir|mix|layer|bake|drain|broil|poach|roast|grill|steam|sear|saute|braise|whisk|knead|caramelize|marinate|simmer|parboil|blanch|whip|fold|beat|blend|pulse|scald|deglaze|fillet|infuse|deep-fry|deep fry|score|smoke)\b"
            methods = list(set(re.findall(methods_pattern, sub_text.lower())))
            # handle ingredients
            ingredients = list(set(filter(lambda ingredient: ingredient.lower() in sub_text.lower(), ingredient_names)))
            for ingredient in ingredient_names:
                for word in sub_text.lower().split():
                    # use Levenshtein to compare word similarity with the ingredient
                    similarity = Levenshtein.ratio(word, ingredient.lower())
                    if similarity >= 0.6 and ingredient not in ingredients:
                        ingredients.append(ingredient)
                        break
            # handle time
            time = parse_time(sub_text)                
            
            # create step object and add to list of steps
            step_obj = Step(step_number=step_counter, text=sub_text, ingredients=ingredients, tools=tools, methods=methods, time=time)
            steps.append(step_obj)
            step_counter += 1
    return steps

def parse_recipe(json_data):
    title = json_data.get("name", "Unknown Title")
    raw_ingredients, ingredients = parse_ingredients(json_data)
    ingredient_names = [ing.name for ing in ingredients]
    steps = parse_steps(json_data, ingredient_names)
    return Recipe(title=title, raw_ingredients= raw_ingredients, ingredients=ingredients, steps=steps)

def recipe_to_json(recipe):
    recipe_dict = {
        "title": recipe.title,
        "raw_ingredients": [
            ing for ing in recipe.raw_ingredients
        ],
        "ingredients": [
            {
                "name": ing.name,
                "quantity": ing.quantity,
                "measurement": ing.measurement,
                "descriptor": ing.descriptor,
                "preparation": ing.preparation
            }
            for ing in recipe.ingredients
        ],
        "tools": list(set({tool for step in recipe.steps for tool in step.tools})),
        "methods": list(set({method for step in recipe.steps for method in step.methods})),
        "steps": [
            {
                "step_number": step.step_number,
                "text": step.text,
                "ingredients": step.ingredients,
                "tools": step.tools,
                "methods": step.methods,
                "time": {
                    "duration": step.time['duration'],
                    "condition": step.time['condition']
                }
            }
            for step in recipe.steps
        ]
    }
    return recipe_dict


'''
# test
link = "https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/"
soup = fetch_recipe(link)
recipe_data = extract_json_ld(soup)
if recipe_data:
    recipe = parse_recipe(recipe_data)
    # title
    print(f"Title: {recipe.title}")
    # raw ingredients
    print("\nRaw Ingredients:")
    for ingredient in recipe.raw_ingredients:
        print(f"- {ingredient}")
    # ingredients
    print("\nIngredients:")
    for ingredient in recipe.ingredients:
        print(f"- {ingredient.name} (Quantity: {ingredient.quantity}, Measurement: {ingredient.measurement}, Descriptor: {ingredient.descriptor}, Preparation: {ingredient.preparation})")
    # steps
    print("\nSteps:")
    for step in recipe.steps:
        print(f"Step {step.step_number}: {step.text} (Ingredients: {step.ingredients}, Tools: {step.tools}, Methods: {step.methods}, Time: {step.time})")
    recipe_json = recipe_to_json(recipe)
    # write to example.json (already did)
    # with open('example.json', 'w', encoding='utf-8') as f:
        # json.dump(recipe_json, f, ensure_ascii=False, indent=2)
else:
    print("No recipe data found in the JSON-LD.")
'''
