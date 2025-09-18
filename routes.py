from flask import Blueprint, render_template # organizes routes, render template for using flask html templates 'jinja'
from pathlib import Path
import json
import base64 # images 
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import numpy as np # arrays for data
import logging # for debugging

bp = Blueprint('main', __name__) # blueprint set up

# log message to know if i run this elsewhere/ where the error is
logger = logging.getLogger(__name__)

MATCH_HISTORY_PATH = None

def init_routes(app):
    """Initialize routes with app context and location of match_history file"""
    global MATCH_HISTORY_PATH
    MATCH_HISTORY_PATH = Path(app.root_path).parent / "data" / "match_history.json"
    logger.info(f"Match history path set to: {MATCH_HISTORY_PATH}")

def generate_graph(matches, stat_type): # stat type is hs/kd
    """handles generating graphs"""
    try:
        plt.style.use('seaborn-v0_8') # style
        fig, ax = plt.subplots(figsize=(10, 5)) # format for creating figure
        
        if not matches:
            raise ValueError("Empty matches data")
            
        dates = [m.get('timestamp', 'N/A') for m in matches] # the timestamp of the matches from match history
        values = []
        # check for stat type and append it to list of kd/hs
        for m in matches:
            if stat_type == 'kd':
                values.append(m.get('kd', 0))
            else:
                values.append(m.get('hs', 0) * 100)

        # Plotting (rest of your graph code remains the same)
        if stat_type == 'kd':
            ax.plot(dates, values, color='#3498db', marker='o', linewidth=2.5)
            ax.set_ylabel('K/D Ratio')
        else:
            bars = ax.bar(dates, values, color='#e74c3c', alpha=0.7)
            ax.set_ylabel('HS%')
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%', ha='center', va='bottom')

        ax.set_title(f'Last {len(matches)} Matches')
        plt.xticks(rotation=45)
        ax.grid(True, linestyle='--', alpha=0.6)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=120)
        plt.close(fig)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
        
    except Exception as e:
        logger.error(f"Graph generation failed: {str(e)}")
        plt.close('all')
        return None

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.r6stats import get_stats


@bp.route('/')
def index():
    try:
        live_stats = get_stats()  
        
        stats = {
            "rank": live_stats.get('rank', 'Unranked'),
            "kd": live_stats.get('kd', 0.0),
            "kd_ratio": live_stats.get('kd_ratio', 0.0),  # Add this line
            "total_matches": 0,
            "last_match": None
        }

        if MATCH_HISTORY_PATH.exists():
            try:
                with open(MATCH_HISTORY_PATH) as f:
                    matches = json.load(f)
                    if matches:
                        stats['total_matches'] = len(matches)
                        last_match = matches[-1]
                        stats['last_match'] = {
                            "map": last_match.get('map_name', 'Unknown'),
                            "score": last_match.get('score', '0-0'),
                            "kd": last_match.get('kd', 0.0),
                            "hs": last_match.get('hs', 0.0) * 100
                        }
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Match history load error: {str(e)}")

        return render_template('index.html', stats=stats)

    except Exception as e:
        logger.error(f"Main page error: {str(e)}", exc_info=True)
        try:
            return render_template('error.html',
                               message="Stats temporarily unavailable"), 500
        except:
            return f"Error: Stats temporarily unavailable. {str(e)}", 500

from flask import jsonify  
import os

@bp.route('/match_history')
def match_history():
    if not os.path.exists(MATCH_HISTORY_PATH):
        return render_template('match_history.html', error="Match history file not found")

    try:
        with open(MATCH_HISTORY_PATH) as f:
            matches = json.load(f)
            
            # Add deduplication - remove consecutive duplicates
            unique_matches = []
            last_match = None
            for match in matches:
                if match != last_match:
                    unique_matches.append(match)
                    last_match = match
            
            # Generate graphs for K/D and HS
            kd_graph = generate_graph(unique_matches, 'kd')
            hs_graph = generate_graph(unique_matches, 'hs')

            # Render the match history template with the match data
            return render_template('match_history.html', 
                                   matches=unique_matches[-3:] if unique_matches else [], 
                                   kd_graph=kd_graph, hs_graph=hs_graph)
            
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Match history load error: {str(e)}")

        return render_template('match_history.html', error="Failed to load match history")
