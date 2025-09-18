import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # R6Tracker
    TRACKER_NETWORK_URL = "https://r6.tracker.network/profile/"
    
    # Discord
    DISCORD_BOT_TOKEN = # Enter Token
    DISCORD_USER_ID = # Enter User ID  
    
    # Arduino
    ARDUINO_PORT = 'COM3'  

    ARDUINO_BAUDRATE = 9600
