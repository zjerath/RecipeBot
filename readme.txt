GitHub Repo: https://github.com/zjerath/RecipeBot

Steps to Run:
1. Clone the repo and create a virtual environment with python=3.10. Activate the environment and run 'pip install -r requirements.txt'.
2. Join the discord server at https://discord.gg/HmNm343g7S.
3. Create a .env file in the root directory and add the following: BOT_TOKEN=MTMwNzc4Mjc4OTgyMjY4MTE1OQ .Gw47Xk.6xRQ0hMusWuBuLPPryQPeF82zcDn35k4ebZOH0 (remove the newline space, can't upload explicit bot token to github)
4. Mention the bot to start a conversation (e.g. "@RecipeBot Help me make this: https://www.allrecipes.com/recipe/156037/classic-lasagna/")
5. Type "stop" to end the conversation.

File Structure:
Our main.py file contains the script used to run our program locally. The code for running on the discord server is in app.py. Parsing is handled in representation.py and parse.py. Conversation code and logic can be found in conversation.py and question_handler.py.
