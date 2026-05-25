import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

os.environ["FLASK_DEBUG"] = "0"

from main import create_app
application = create_app()
