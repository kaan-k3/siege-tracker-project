import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # R6Tracker
    TRACKER_NETWORK_URL = "https://r6.tracker.network/profile/"
    
    # Discord
    DISCORD_BOT_TOKEN = 'MTM1NDYwMzg0OTMxODQwMDI0Mw.GG05Vs.eGXtyZ3hha4jktjzd06fKY7asV9nCudTAQ_Aa4'
    DISCORD_USER_ID = 807812546181464075  
    
    # Arduino
    ARDUINO_PORT = 'COM3'  
    ARDUINO_BAUDRATE = 9600