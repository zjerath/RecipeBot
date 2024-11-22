GitHub Repo: https://github.com/zjerath/RecipeBot

Project 2 CS 337: RecipeBot

File Structure:
- main.py: script used to run our program locally
- app.py: script for running RecipeBot on the discord server
- parse.py: logic for recipe retrieval and parsing into appropriate data structure defined in representation.py
- representation.py: defines the data structure where we store the parsed information about the recipe
- question_handler.py: handle generic question-answering logic for a given recipe
- conversation.py: track and update state variables relevant to a conversation about a recipe, and direct user requests to the appropriate question-answering module
- requirements.txt: contains dependencies required to set up an environment to run RecipeBot 

Getting started:
1. Clone the repository
2. Create a virtual environment (python 3.10/3.11)
3. Install the dependencies with pip install -r requirements.txt
4. Join the discord server at https://discord.gg/HmNm343g7S to start interacting with our RecipeBot! Instructions for using the chatbot are below.

Discord server invite link to interact with the bot: https://discord.gg/HmNm343g7S

How to use the Discord bot: 
1. Create a .env file in the root directory and add the following:
    - BOT_TOKEN=MTMwNzc4Mjc4OTgyMjY4MTE1OQ  .Gw47Xk.6xRQ0hMusWuBuLPPryQPeF82zcDn35k4ebZOH0 (remove the spaces, can't upload explicit bot token to github)
2. Start the bot locally by running python app.py
3. Mention the bot to start a conversation (e.g. "@RecipeBot Help me make this: https://www.allrecipes.com/recipe/156037/classic-lasagna/")
4. Talk to the bot like you would to another person (e.g. "What are the ingredients needed?")
5. Type "stop" to end the conversation

Example Questions for Question Answering Goals:
1. Recipe retrieval and display.
    - "Tell me the ingredients for this recipe."
    - "What tools do I need?"
    - "List all the steps for this recipe."
2. Navigation utterances.
    - "Go to the next step", "Next step", "Proceed"
    - "Go back", "Previous step"
    - "Navigate to the 5th step", "Go to step 8" (outside of "first"/"last", must specify a number i.e. not "fifth")
    - "Repeat", "Say that again"
3. Asking about the parameters of the current step.
    - "What tools do I need for this step?"
    - "What are the ingredients for this step?"
    - "How long do I <cooking method>?"
    - "Tell me the methods for this step."
    - "What can I replace <recipe step ingredient> with?"
4. Simple "what is" questions.
    - "What is a <tool being mentioned>?"
5. Specific "how to" questions.
    - "How do I <specific technique>?"
6. Vague questions.
    - "What can I replace that with?"
