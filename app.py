import discord
from discord.ext import commands
import json
import os
import re
from conversation import Conversation
from parse import fetch_recipe, extract_json_ld, parse_recipe, recipe_to_json

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store user IDs who have mentioned the bot
conversations = {}

def extract_url(message_content):
    """Extract and validate AllRecipes URL from message content"""
    # Extract URL using regex pattern
    url_pattern = r'https?://(www\.)?allrecipes\.com/recipe/\d+/[^/\s]+/?'
    match = re.search(url_pattern, message_content)
    
    if match:
        url = match.group(0)
        # Validate the extracted URL
        if re.match(r'^https?://(www\.)?allrecipes\.com/recipe/\d+/[^/]+/?$', url):
            return url
    return None

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Continue an existing conversation
    if str(message.author.id) in conversations:
        conversation = conversations[str(message.author.id)]

        # If the user says "stop", end the conversation
        if message.content.lower() == "stop":
            del conversations[str(message.author.id)]
            await message.channel.send("Conversation ended.")
            return
        
        response = conversation.handle_request(message.content)
        await message.channel.send(response)

    # Check if bot is mentioned
    elif bot.user.mentioned_in(message):
        # Start a new conversation
        url = extract_url(message.content)
        if not url:
            await message.channel.send("Please provide a valid AllRecipes URL.")
            return
        
        # attempt to fetch and parse url
        try:
            soup = fetch_recipe(url)
            json_data = extract_json_ld(soup)
            if not json_data:
                await message.channel.send("Could not find a valid recipe in the provided URL.")
                return
            # parse recipe
            recipe = parse_recipe(json_data)
            # if json easier to work with, add line below and refer to jsn in convo
            jsn = recipe_to_json(recipe)
            conversation = Conversation(jsn) # Conversation() assumes recipe object in JSON format ATM
            await message.channel.send(f"Alright. So let's start working with \"{recipe.title}\". \nWould you like to start with the ingredients list or the recipe steps?")
            
        except Exception as e:
            print(f"An error occurred: {e}")

        conversations[str(message.author.id)] = conversation   

bot.run(os.getenv('BOT_TOKEN'))
