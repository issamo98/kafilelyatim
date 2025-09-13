import os
import sys
import subprocess
import webbrowser
import time
import multiprocessing

def main():
    # Start Django server
    subprocess.Popen([sys.executable, "manage.py", "runserver", "127.0.0.1:8003"])

    # Wait a bit to let the server start
    time.sleep(3)

    # Open browser automatically (only once)
    webbrowser.open("http://127.0.0.1:8003")

    # Keep process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    multiprocessing.freeze_support()  # <-- important for Windows
    main()
