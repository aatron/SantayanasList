"""Get Netflix History"""
import argparse
import mechanicalsoup
import json
import time
from slimit.lexer import Lexer

# Initialize credentials from command prompt arguments
parser = argparse.ArgumentParser(description='Log into Netflix.')
parser.add_argument('username')
parser.add_argument('password')
args = parser.parse_args()

# Create browser
browser = mechanicalsoup.Browser()

# Login
login_page = browser.get("https://www.netflix.com/login")
login_form = login_page.soup.select("form.login-form")[0]
login_form.select("input[name='email']")[0]['value'] = args.username
login_form.select("input[name='password']")[0]['value'] = args.password
logged_in_page = browser.submit(login_form, login_page.url)

history_page = browser.get("https://www.netflix.com/viewingactivity")

# Use lexer to extract the BUILD_IDENTIFER from the last Javascript script tag
script_tag = history_page.soup.find_all("script", {"src" : ""}, recursive=True)[-1]
lexer = Lexer()
lexer.input(script_tag.text)

while True:
    token = lexer.token()
    if token.value == "\"BUILD_IDENTIFIER\"":
        lexer.token() # :
        api_path = lexer.token().value.replace("\"", "")
        break

netflixHistory = []
page = 0;
historyRecovered = False

# Get history
while not historyRecovered:
    page += 1
    print("getting page: " + str(page) )

    url = "https://www.netflix.com/api/shakti/{}/viewingactivity?pg={}&pgSize=100&_={}".format(api_path, page, int(time.time()))
    page_down = browser.get(url)

    historyJson = json.loads(page_down.text)
    if historyJson['viewedItems'] == []:
        historyRecovered = True
    else:
        netflixHistory.extend(historyJson['viewedItems'])

# Save to file as json
fileName = time.strftime("%Y%m%d%I%M%S") + '_netflixhistory.json'
with open(fileName, 'w') as jsonFile:
    json.dump(netflixHistory, jsonFile)

