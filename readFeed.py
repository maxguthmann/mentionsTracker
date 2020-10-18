from pprint import pprint
import feedparser
import time
import os.path
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

url = 'https://www.google.com/alerts/feeds/03545304205581962896/7762502584850169436'

spreadsheetId = '1goy51SVdHK0ZV6Xaj7YbPbt9bROWA_vQlDnc5nq-bzA'
range_ = 'Sheet1'
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


value_range_body = {
    "range": 'Sheet1',
    "majorDimension": 'ROWS',
    "values": [
        [1,2,3]
    ]
}

#request = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
#response = request.execute()

#pprint(response)

d = feedparser.parse(url)
#print(d)
for entry in d['entries']:
    print('')
    print(entry['title'])
    print(entry['link'])
    print(entry['published'])

    value_range_body = {
        "range": 'Sheet1',
        "majorDimension": 'ROWS',
        "values": [
            [entry['title'],entry['link'],entry['published']]
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