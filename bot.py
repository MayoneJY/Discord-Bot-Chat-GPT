import openai
import discord
from discord.ext import commands
import os
import time

openai.api_key = "YOUR OPENAI API KEY"  # Enter your OpenAI API key here.
token = "YOUR DISCORD BOT TOKEN"  # Enter your Discord bot token here.

client = discord.Bot()  # Create a new Discord bot.
remember_text = {}  # Dictionary to store conversation history.
typing_check = {}  # Dictionary to store typing status.

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

@client.command(name="new")  # Command to start a new conversation.
async def new(ctx):
    remember_text[ctx.channel.id] = []  # Clear conversation history.
    typing_check[ctx.channel.id] = False  # Reset typing status.
    await ctx.respond("Starting a new conversation.")

@client.command(name="chat")  # Command to start a conversation.
async def chat(ctx, *, text):
    try:
        # Check if conversation history and typing status dictionaries exist for the channel.
        try:
            type(remember_text[ctx.channel.id])
            type(typing_check[ctx.channel.id])
        except KeyError:
            remember_text[ctx.channel.id] = []
            typing_check[ctx.channel.id] = False
        except IndexError:
            remember_text[ctx.channel.id] = []
            typing_check[ctx.channel.id] = False
        
        # If the bot is the author of the message or is already typing, do nothing.
        if ctx.author == client.user:
            return
        if typing_check[ctx.channel.id] == True:
            await ctx.respond("Still processing the previous request. Please try again later.", delete_after=3)
            return
        
        # Set the typing status to true and get the user's message.
        typing_check[ctx.channel.id] = True
        response = None
        prompt = text
        print(text)

        # Let the user know that the bot is processing their request.
        temp = await ctx.respond("Processing your request...")
        
        # Retrieve the conversation history for the channel.
        async with ctx.typing():
            message = []
            for i in range(1, len(remember_text[ctx.channel.id]) + 1):
                if i % 2 == 1:
                    message.append({"role": "user", "content": remember_text[ctx.channel.id][i-1]})
                else:
                    message.append({"role": "assistant", "content": remember_text[ctx.channel.id][i-1]})
            message.append({"role": "user", "content": prompt})
            print(message)
            
            # Send the user's message to OpenAI and get a response.
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0301",  # Use the GPT-3 model.
                    messages=message
                    )
            except openai.error.APIError as error:
                # If there is an API error, let the user know and wait 5 seconds before processing the request again.
                if error.status == 429:
                    await temp.edit_original_response(content="Still processing the previous request. Please try again later.")
                    time.sleep(5)
                else:
                    await temp.edit_original_response(content="An error occurred. Please try again.")
            except:
                await temp.edit_original_response(content="An error occurred. Please try again.")
            
            # Get the response and update the conversation history.
            reply = response.choices[0].message.content
            await temp.edit_original_response(content="Question from " + ctx.author.name + "\nQuestion: " + text + "\nAnswer: " + reply)
            if len(remember_text[ctx.channel.id]) > 12:
                del remember_text[ctx.channel.id][0]
                del remember_text[ctx.channel.id][0]
            remember_text[ctx.channel.id].append(prompt)
            remember_text[ctx.channel.id].append(reply)
            typing_check[ctx.channel.id] = False  # Set typing status to false.
    except:
        typing_check[ctx.channel.id] = False

client.run(token)  # Start the Discord bot.