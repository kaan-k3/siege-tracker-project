import sys
from pathlib import Path
import os
import json
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
MATCH_HISTORY_FILE = Path(__file__).parent.parent / "data" / "match_history.json" # json file containing dict data
MATCH_HISTORY_FILE.parent.mkdir(exist_ok=True) # creates the directory, needed this at the start to make it, but it also checks if it exists or not to avoid error

# I was having trouble trying to import the modules below because it couldn't access the file the modules were located in. Found this quick fix online but probably not the best solution. 

# It gets the project root directory (2 levels up from current file) and adds project root to Python path so other project modules can be imported

import discord
from discord.ext import tasks
from core.match_finder import get_match_data
import time

# storing match info
match_history = []
intents = discord.Intents.default()
intents.messages = True  # Ensure the bot can receive/send messages, the setup manual had it like this so I did the same.

client = discord.Client(intents=intents)
USER_ID =  # enter user id
BOT_TOKEN = # enter bot token

def generate_match_signature(match_data):
    """
    This generates a unique signature for the match to check if it's a new match. It compares the map, score, and timestamp which will later be compared.
    """
    signature = f"{match_data['map_name']}_{match_data['score']}_{match_data['timestamp']}"
    print(f"Generated match signature: {signature}")
    return signature

def save_match_history():
    try:
        
        with open(MATCH_HISTORY_FILE, 'w') as f: # open the file to write in 
            json.dump(match_history, f, indent=2) # save the match_history dict output as a json format inside
    
    except Exception as e:
        print(f"Save failed: {str(e)}") # debug
        import traceback
        traceback.print_exc() # print the stack trace


def analyze_performance():
    """
    Analyzes the KD and HS performance over the last matches. It checks it every 2 matches.
    Sends feedback based on whether there's improvement or not.
    """
    global match_history

    if len(match_history) < 2:
        print("Not enough matches to analyze. Waiting for more matches.")
        return  # Wait until we have 2 matches to analyze
    
    previous_match = match_history[-2] # accesses last match from the list, goes second from the end
    current_match = match_history[-1] # accesses current match, since it goes at the end

    kd_diff = current_match['kd'] - previous_match['kd'] # difference in kd from current and last
    hs_diff = current_match['hs'] - previous_match['hs'] # difference in hs rate from current and last
    
    feedback = [] # store feedback
    # below are just feedback based on if the stats improved or if I did worse.
    if kd_diff > 0:
        feedback.append(f"KD ↑ +{kd_diff:.2f} from last match. Your KD is improving! Keep it up!\n")
    elif kd_diff < 0:
        feedback.append(f"KD ↓ {kd_diff:.2f} from last match. Your KD could use some work. Keep practicing!\n")
    
    if hs_diff > 0:
        feedback.append(f"HS% ↑ +{hs_diff:.2%} from last match. Your HS % is improving! Great job!\n")
    elif hs_diff < 0:
        feedback.append(f"HS% ↓ {hs_diff:.2%} from last match. Your HS % could use some work, try practicing in shooting range!\n")

    return "\n".join(feedback) if feedback else "Performance stable compared to last match" # checks for if diff =

async def check_for_new_match():
    """
    Checks for a new match and sends a message if it's a new match.
    """
    global match_history
    match_data = get_match_data()

    # uses the function from before to make a signature for the current match
    current_match_signature = generate_match_signature(match_data)

    if not match_history or generate_match_signature(match_history[-1]) != current_match_signature: # it checks if the list is empty first then if the last match is different from the current match it just found
        match_history.append({
            "map_name": match_data["map_name"], # format for the data, itll add to match history list.
            "score": match_data["score"],
            "timestamp": match_data["timestamp"],
            "kd": float(match_data["kd"]),
            "hs": float(match_data["hs"].replace('%', '')) / 100  # Convert HS % to float
        })
        
        save_match_history()
        
        # debugging purposes
        print(f"Current match history: {match_history}")

        # since its a new match, discord will send the new match info. it's just the same format, just reorganized.
        match_message = (
            f"NEW MATCH:\n"
            f"Map Name: {match_data['map_name']}\n"
            f"Timestamp: {match_data['timestamp']}\n"
            f"Score: {match_data['score']}\n"
            f"KD: {match_data['kd']}\n"
            f"HS %: {match_data['hs']}\n"
        )
        user = await client.fetch_user(USER_ID)
        await user.send(match_message)
        print("Match message sent!") # sends the match message, print was also for debugging

        # now the discord bot also checks the list, and if feedback is appropriate to go along with the match message.
        if len(match_history) >= 2:
            feedback = analyze_performance()

            if feedback:
                feedback_message = (
                    f"\nFeedback:\n{feedback}"
                )
                await user.send(feedback_message)
                print("Feedback message sent!")

@tasks.loop(minutes=10) # discord loop for doing this process every 10 minutes
async def periodic_check():
    await check_for_new_match()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    periodic_check.start()  # start the periodic check loop

def start_discord():  # this is just so i can import this entire file as a module for later, basically just condenses the process.
  
    @tasks.loop(minutes=10)
    async def periodic_check(): 
        print("Checking for new matches...")  
        await check_for_new_match() 
    
  
    @client.event 
    async def on_ready():
        print(f"Discord bot ready as {client.user}!")
        periodic_check.start()
        
        if not MATCH_HISTORY_FILE.exists():
            with open(MATCH_HISTORY_FILE, 'w') as f:
                json.dump([], f)  # Create empty list
    print("Created empty match history file")
    
    client.run(BOT_TOKEN)


client.run(BOT_TOKEN)
