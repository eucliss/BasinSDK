
from unittest import result
from dotenv import load_dotenv
import os
import requests
import json
import re
from bs4 import BeautifulSoup

page = f'https://www.abilityarena.com/api/games/6776010256'
req = requests.get(page)
# print(req)
print(req.json())
# my_json = req.content.decode('utf8').replace("'", '"')
# print(my_json)
# print(dir(req))
