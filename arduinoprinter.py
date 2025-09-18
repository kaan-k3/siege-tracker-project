import sys
from pathlib import Path
import discord
from discord.ext import tasks
import asyncio
import serial
from engi1020.arduino.api import *
from core.r6stats import get_stats

# Project setup
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Discord setup
intents = discord.Intents.default() # basically just permission for send messages
intents.messages = True
client = discord.Client(intents=intents)
USER_ID = 807812546181464075
BOT_TOKEN = 'MTM1NDYwMzg0OTMxODQwMDI0Mw.GG05Vs.eGXtyZ3hha4jktjzd06fKY7asV9nCudTAQ_Aa4'
prev_rank = None



# async is required for discord bots to run since they require non-blocking code, and await allows them to pause and wait for commands


async def send_ragemessage():
    """Function that tells discord to send the rage message, pretty simple"""
    try:
        user = await client.fetch_user(USER_ID)
        await user.send("We both know you suck at the game, but take a breather for me and calm down.")
    except Exception as e:
        print(f"Error sending message: {e}")

async def handle_rage_mode(stats_text):
    """Rage Quit Mode Activation"""
    oled_clear()
    oled_print("RAGE MODE - 60s COOLDOWN")
    await send_ragemessage() # sends the message from earlier
    await asyncio.sleep(60) # pauses this for 60s before executing the clear command
    oled_clear()
    

def update_rank_color(rank):
    """Update LCD color based on rank, a dictionary listed below"""
    color_mapping = {
        'COPPER': (128, 0, 0),
        'BRONZE': (255, 111, 5),
        'SILVER': (224, 224, 224),
        'GOLD': (230, 100, 1),
        'PLATINUM': (0, 255, 200),
        'EMERALD': (0, 255, 0),
        'DIAMOND': (255, 130, 150),
        'CHAMPION': (255, 0, 150)
    }
    if rank:
        for prefix, color in color_mapping.items(): # loops through dictionary keys and values
            if rank.startswith(prefix): # if the current rank starts with one of the keys
                rgb_lcd_colour(*color) # update lcd screen using tuple
                break

async def handle_rank_change():
    """Handle buzzer for rank changes, always runs the first time since prev_rank is set to None"""
    buzzer_frequency(5, 500)
    await asyncio.sleep(2)
    buzzer_stop(5)

async def arduino_loop():
    """Main Arduino control loop"""
    global prev_rank

    while True:
        try:
            stats_text = get_stats(output_format='string') # asks for a string output instead of dictionary
            current_rank = stats_text.split("Rank: ")[1].split("\n")[0] if stats_text else None # it strips the text and isolates the specific Rank

            if stats_text:
                rgb_lcd_print(stats_text) # print the rank to the screen
                
                # check rage mode on every loop cycle 
                if analog_read(2) >= 675:
                    await handle_rage_mode(stats_text)

                update_rank_color(current_rank) # change color

                if current_rank and current_rank != prev_rank:
                    await handle_rank_change()
                    prev_rank = current_rank # handle the rank change
            else:
                oled_clear()
                oled_print("No stats available")
            
            await asyncio.sleep(5)  # wait 5 seconds before checking stats again

        except Exception as e:
            print(f"Arduino error: {e}")
            await asyncio.sleep(5)


@client.event # marks this function for when the bot starts
async def on_ready():
    """Discord bot startup"""
    print(f'Logged in as {client.user}')
    # runs Arduino loop in background
    asyncio.create_task(arduino_loop())

def start_bot():
    """Start the Discord bot"""
    discord.heartbeat_timeout = 60.0 # connection timeout time
    client.run(BOT_TOKEN) # runs the bot

if __name__ == '__main__': #it blocks bot from running automatically elsewhere - but i can run it here for tests
    start_bot()