from pprint import pprint
from bs4 import BeautifulSoup
from bs4.element import Comment
import feedparser
import time
import os.path
import pickle
import requests

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


url = 'https://www.google.com/alerts/feeds/03545304205581962896/7762502584850169436'

spreadsheetId = '1goy51SVdHK0ZV6Xaj7YbPbt9bROWA_vQlDnc5nq-bzA'
range_ = 'small modular reactor'
value_input_option = 'RAW'
insert_data_option = 'INSERT_ROWS'

creds = None
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)




#request = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
#response = request.execute()

#pprint(response)

d = feedparser.parse(url)
#print(d)
for entry in d['entries']:
    print('')
    linkStart = entry['link'].find('url=')
    linkEnd = entry['link'].rfind('&ct')
    link = entry['link'][linkStart + 4:linkEnd]
    print(link)

    hyphen = entry['published'].find('-')
    year = entry['published'][:hyphen]
    rest = entry['published'][hyphen + 1:]
    hyphen = rest.find('-')
    month = rest[:hyphen]
    day = rest[hyphen + 1:rest.find('T')]
    time = rest[rest.find('T') + 1 : -1]
    print(time)
    print(entry)

    html = requests.get(link).content
    soup = BeautifulSoup(html, features='lxml')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    text = u" ".join(t.strip() for t in visible_texts)
    print(text)
    value_range_body = {
        "range": 'small modular reactor',
        "majorDimension": 'ROWS',
        "values": [
            [entry['title'], link, entry['published'], text, year, month, day]
        ]
    }
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()


#while True:
#    d = feedparser.parse(url)
#    #print(d)
#    for entry in d['entries']:
#        print('')
#        print(entry['title'])
#        print(entry['link'])
#        print(entry['published'])
#    time.sleep(5)