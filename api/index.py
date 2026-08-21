import os
import sys

# Add the parent directory to sys.path so we can import webapp
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webapp.server import app
