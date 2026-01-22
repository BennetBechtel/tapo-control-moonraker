#!/usr/bin/python3

import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()

port = int(os.getenv("PORT", 56427))  # Default to 56427 if PORT is not set

if __name__ == "__main__":
    uvicorn.run("server:app", host="localhost", port=port, reload=True)
