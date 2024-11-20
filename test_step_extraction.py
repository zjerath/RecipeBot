from constants import ordinal_base, ordinal_tens
import re
from conversation import Conversation
from question_handler import QuestionHandler
import json
from parse import fetch_recipe, extract_json_ld, parse_recipe, recipe_to_json
import nltk
from nltk.tokenize import sent_tokenize


def ordinal_to_number(ordinal):
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
def extract_step_number(request):
    '''
    Example usage:
        print(extract_step_number("Can you take me to the twenty-first step?"))  # Output: 21
        print(extract_step_number("Go to step 42"))  # Output: 42
        print(extract_step_number("Proceed to the fifteenth step"))  # Output: 15
    '''
    # Regular expression to capture the nth step
    match = re.search(
        r"\b(?:go to|navigate to|move to|proceed to|take me to)\b.*\b(?:step|instruction)\b.*\b(\d+|[a-zA-Z-]+)\b",
        request, re.IGNORECASE
    )
    
    if match:
        step = match.group(1)  # Capture the step part
        # Check if it's a digit and return as an integer
        if step.isdigit():
            return int(step)
        # Otherwise, attempt to convert ordinal to a number
        return ordinal_to_number(step.lower())
    return None  # Return None if no step is found

# Function to handle ordinal word to number conversion
ordinal_base = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9,
    "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13,
    "fourteenth": 14, "fifteenth": 15, "sixteenth": 16, "seventeenth": 17,
    "eighteenth": 18, "nineteenth": 19, "twentieth": 20,
    "twenty-first": 21, "twenty-second": 22, "twenty-third": 23, "twenty-fourth": 24,
    "twenty-fifth": 25, "twenty-sixth": 26, "twenty-seventh": 27, "twenty-eighth": 28,
    "twenty-ninth": 29, "thirtieth": 30, "thirty-first": 31
}

def ordinal_to_number(ordinal):
    # Check if ordinal is in the dictionary
    if ordinal in ordinal_base:
        return ordinal_base[ordinal]
    # Handle composite ordinals like "twenty-first" dynamically
    parts = ordinal.split('-')
    if len(parts) == 2 and parts[0] in ordinal_base and parts[1] in ordinal_base:
        return ordinal_base[parts[0]] + ordinal_base[parts[1]]
    return None

def extract_step_number(request):
    # Regular expression to capture the nth step
    match = re.search(
        r"\b(?:go to|navigate to|move to|proceed to|take me to)\b.*\b(?:step|instruction)\b.*\b(\d+(?:st|nd|rd|th)?|[a-zA-Z-]+)\b",
        request, re.IGNORECASE
    )
    
    if match:
        step = match.group(1)  # Capture the step part
        # Check if it's a digit or ordinal suffix form (e.g., "25th") and convert to an integer
        if step.isdigit():
            return int(step)
        elif step[:-2].isdigit():  # Handles cases like "25th", "100th" by removing suffix
            return int(step[:-2])
        # Otherwise, attempt to convert ordinal word to a number
        return ordinal_to_number(step.lower())
    return None  # Return None if no step is found

def main():
    # Test cases
    requests = [
        "go to the first step",
        "go to the last step",
        "Go to the 25th step",
        "go to 4th step",
        "Next step",
        "Proceed to the 3rd step",
        "proceed"
    ]

    url = 'https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/'
    soup = fetch_recipe(url)
    json_data = extract_json_ld(soup)
    if not json_data:
        print("Could not find a valid recipe in the provided URL.")
        return
    # parse recipe
    recipe = parse_recipe(json_data)
    # if json easier to work with, add line below and refer to jsn in convo
    jsn = recipe_to_json(recipe)

    # convo = Conversation(None)
    handler = QuestionHandler(jsn)

    for request in requests:
        print(f"request: {request} | step number: {handler.extract_step_number(request)} \n")
        # print(f"Navigation type: {convo.detect_navigation_type(request)}\n")
        # print()

    # navigation_patterns = [
    #     r"\b(?:go to|navigate to|move to|proceed to|take me to)\b.*\b(\d+)(?:st|nd|rd|th)?\b.*\b(?:step|instruction)\b.*"
    #     # r"\b(?:go to|navigate to|move to|proceed to|take me to)\b \b(?:step|instruction)\b \b(\d+)\b.*", #[a-zA-Z]+
    # ]

    # # Extract step numbers
    # for request in requests:
    #     # print(f"Request: '{request}' -> Step: {extract_step_number(request)}")
    #     for pattern in navigation_patterns:
    #         match = re.search(pattern, request, re.IGNORECASE)
    #         # print(match)
    #     if match:
    #         # print(match.groups)
    #         print(match.group(1))

def extract_time_info(recipe_text):
    # Patterns to match durations and conditional phrases
    time_patterns = [
        r"\d+\s*(?:second[s]?|minute[s]?|hour[s]?|sec|min|hr[s]?)",  # Numeric durations with units
        r"about\s+\d+\s*(?:second[s]?|minute[s]?|hour[s]?)",         # Approximate durations
        r"for\s+\d+\s*(?:second[s]?|minute[s]?|hour[s]?)"            # 'for X time'
    ] # add word boundary + arbitrary num chars?

    # Patterns to match conditions
    condition_patterns = [
        r"until\s+[\w\s]+",        # Conditions like 'until golden brown'
        r"once\s+[\w\s]+",         # Conditions like 'once dissolved'
        r"when\s+[\w\s]+"          # Conditions like 'when bubbly'
    ] # add word boundary + arbitrary num chars?

    # Compile the patterns
    time_regex = re.compile("|".join(time_patterns), re.IGNORECASE)
    condition_regex = re.compile("|".join(condition_patterns), re.IGNORECASE)

    # Find all matches
    times = time_regex.findall(recipe_text)
    conditions = condition_regex.findall(recipe_text)

    # Extract structured results
        # duration : time value (for 10 minutes)
        # condition : condition value (until brown)
    extracted_info = {} 
    for time in times:
        # extracted_info.append({"type": "time", "value": time.strip()})
        cleaned_time = re.sub(r"^(for|about)\s+", "", time, flags=re.IGNORECASE)
        extracted_info['duration'] = cleaned_time.strip()
    if not times:
        extracted_info['duration'] = None
    for condition in conditions:
        # Remove the keywords ('until', 'once', 'when') from the matched condition
        # cleaned_condition = re.sub(r"^(until|once|when)\s+", "", condition, flags=re.IGNORECASE)
        # extracted_info.append({"type": "condition", "value": condition.strip()})
        extracted_info['condition'] = condition.strip()
    if not conditions:
        extracted_info['condition'] = None

    return extracted_info

def foo():
    # Download the punkt tokenizer if not already downloaded
    nltk.download('punkt')

    # Example usage
    recipe_text = """
        Preheat the oven to 350°F. Bake for 30 minutes or until golden brown.
        Simmer for about 20 minutes until thickened.
        Stir continuously for 5 minutes. Once the sauce is smooth, remove from heat.
        Mix for 5 minutes, or once the sauce is smooth.
    """
    a = """
        my name is jimin.
        i like cheese.
        i drink coffee.
    """

    for sentence in sent_tokenize(recipe_text):
        time_info = extract_time_info(sentence)
        print(sentence)
        print(time_info)
        # for info in time_info:
        #     print(f"{info['type'].capitalize()}: {info['value']}")
        print('\n')

    request = "how to bake cheese"
    if "how much" in request.lower() or "how many" in request.lower():
        print("yes")



if __name__ == "__main__":
    # main()
    foo()