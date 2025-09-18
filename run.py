import subprocess
import sys
from pathlib import Path
from time import sleep

# Path to your scripts (same folder as this launcher)
SCRIPTS = [
    "runflask.py", 
    "rundiscord.py",
    "runarduino.py"
]

def run_scripts():
    # Run Arduino script first and wait for manual input in a new terminal window
    try:
        print("Running Arduino script. Please select the device manually...")
        subprocess.run(["start", "cmd", "/K", "python", str(Path(__file__).parent / "runarduino.py")], shell=True)
        print("✅ Arduino script completed successfully")
    except Exception as e:
        print(f"❌ Failed to start runarduino.py: {str(e)}")

    # After Arduino script completes, run the other scripts in parallel
    for script in SCRIPTS:
        if script != "runarduino.py":
            try:
                subprocess.Popen([sys.executable, str(Path(__file__).parent / script)])
                sleep(3)
                print(f"✅ {script} started")
            except Exception as e:
                print(f"❌ Failed to start {script}: {str(e)}")

if __name__ == '__main__':
    run_scripts()
    print("All components launched")
