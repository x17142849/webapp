import os
from os.path import join, dirname
from dotenv import load_dotenv
import time


dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

NEXMO_API_KEY = os.getenv('NEXMO_API_KEY')
NEXMO_API_SECRET = os.getenv('NEXMO_SECRET')
TO_NUMBER = os.getenv('DESTINATION_PHONE_NUMBER')

import nexmo


client = nexmo.Client(key=NEXMO_API_KEY, secret=NEXMO_API_SECRET)

client.send_message({
    'from': 'Doorbell',
    'to': TO_NUMBER,
    'text': 'Hello, a new doorbell at '+time.strftime("%X"),
    })

