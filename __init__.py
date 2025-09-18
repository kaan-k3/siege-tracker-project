from flask import Flask
from pathlib import Path
import matplotlib
matplotlib.use('Agg') # for storing as a file

def create_app():
    app = Flask(__name__) # create app instance
    
    # Initialize routes
    from app.routes import bp, init_routes
    init_routes(app)  # register paths/routes/bp
    app.register_blueprint(bp)
    
    return app # return the app object to be used later

def _configure_matplotlib(): # just styling/formatting for the graphs
    import matplotlib.pyplot as plt
    try:
        plt.style.use('seaborn-v0_8')  # seaborn style
    except:
        plt.style.use('ggplot')  # secondary style if first one is offline/doesn't work
    plt.rcParams['figure.facecolor'] = 'white' # background color
    plt.rcParams['axes.grid'] = True #display grid