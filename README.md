# RecipeBot
Project 2 CS 337

# Discord server invite link to interact with the bot: 
https://discord.gg/HmNm343g7S

# Getting started
1. Clone the repository
2. Create a virtual environment (python 3.10/3.11)
3. Install the dependencies with pip install -r requirements.txt
4. Run the chatbot in cli with python main.py

# How to use the Discord bot: 
1. Create a .env file in the root directory and add the following:
    - BOT_TOKEN=MTMwNzc4Mjc4OTgyMjY4MTE1OQ  .Gw47Xk.6xRQ0hMusWuBuLPPryQPeF82zcDn35k4ebZOH0 (remove the spaces, can't upload explicit bot token to github)
2. Start the bot locally by running python app.py
3. Mention the bot to start a conversation (e.g. "@RecipeBot Help me make this: https://www.allrecipes.com/recipe/156037/classic-lasagna/")
4. Talk to the bot like you would to another person (e.g. "What are the ingredients needed?")
5. Type "stop" to end the conversation

# Question Answering Goals: Example Questions
1. Recipe retrieval and display.
    - "Tell me the ingredients for this recipe."
    - "What tools do I need?"
    - "List all the steps of this recipe."
2. Navigation utterances.
    - "Go to the next step", "Next step"
    - "Go back", "Previous step"
    - "Navigate to the 5th step", "Go to step 8" (outside of "first"/"last", must specify a number i.e. not "fifth")
    - "Repeat", "Say that again"
3. Asking about the parameters of the current step.
    - "What tools do I need for this step?"
    - "What are the ingredients for this step?"
    - "How long do I <cooking method>?"
    - "Tell me the methods for this step."
4. Simple "what is" questions.
    - "What is a <tool being mentioned>?"
5. Specific "how to" questions.
    - "How do I <specific technique>?"
6. Vague "how to" questions ("How do I do that?" – use conversation history to infer what “that” refers to)

