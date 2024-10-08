"""This is main file.

This file contains main function.
"""

__version__ = "1.0"
__author__ = "Wiered"

import os

from dotenv import load_dotenv

load_dotenv()

import uvicorn

from api import app

if __name__ == "__main__":
    try:
        port = int(os.environ.get("PORT"))
    except:
        port = 8080
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
