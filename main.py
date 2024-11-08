import json
from conversation import Conversation

def main():
    recipe = json.load(open('example.json'))
    # print(recipe)
    conversation = Conversation(recipe)

    # Question type classification (General, Navigation, Step-specific) logic assumes specific question format
    # Check question_handler.determine_request_type() for details  
    question_sequence = [
        "What is the recipe for lasagna?",
        # "What are the ingredients?",
        # "How do I preheat the oven?",
        "Tell me the ingredients for this step.",
        "Go to the next step",
        "What are the ingredients for this step?",
        "Proceed to the next step",
        "what are the methods for this step?",
        "Go to the 5th step",
        "What tools do I need for this step?",
        "Go to the 25th step"
    ]

    for question in question_sequence:
        print(f"QUESTION: {question}")
        conversation.handle_request(question)
        print('\n')

if __name__ == "__main__":
    main()