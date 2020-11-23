from pprint import pprint
from bs4 import BeautifulSoup
from bs4.element import Comment
import concurrent.futures
import feedparser
import time
import os.path
import pickle
import requests

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

spreadsheetId      = '1goy51SVdHK0ZV6Xaj7YbPbt9bROWA_vQlDnc5nq-bzA'
value_input_option = 'RAW'
insert_data_option = 'INSERT_ROWS'

executor = concurrent.futures.ThreadPoolExecutor()

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


#url = 'https://www.google.com/alerts/feeds/03545304205581962896/7762502584850169436'
#range_ = 'small modular reactor'


class GSheetsParser:
    def __init__(self, path):
        creds = None
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        if os.path.exists(path):
            with open(path, 'rb') as token:
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

        self.service = build('sheets', 'v4', credentials=creds)

    def getLatestTime(self, range_, url):
        rowcount = self.service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range_).execute()
        index = len(rowcount['values']) - 1
        latestTime = rowcount['values'][index][2]
        while True:
            index -= 1
            latestTimeTemp = rowcount['values'][index][2]
            if(latestTimeTemp < latestTime):
                break
            latestTime = latestTimeTemp
        return latestTime

    def parseFeed(self, feed):
        range_ = feed[0]
        print(range_)
        url    = feed[1]
        print(feed)
        latestTime = self.getLatestTime(range_, url)
        
        print(latestTime)

        d = feedparser.parse(url)
        print(d['entries'])
        print(self.get_keywords("asd f asd molten salt spot blind spot exciting overrated", feed[2:]))
        for entry in d['entries']:
            print('')
            entry_data={}

            linkStart = entry['link'].find('url=')
            linkEnd = entry['link'].rfind('&ct')
            entry_data['link'] = entry['link'][linkStart + 4:linkEnd]
            print(entry_data['link'])

            hyphen = entry['published'].find('-')
            entry_data['year'] = entry['published'][:hyphen]
            rest = entry['published'][hyphen + 1:]
            hyphen = rest.find('-')
            entry_data['month'] = rest[:hyphen]
            entry_data['day'] = rest[hyphen + 1:rest.find('T')]
            time = rest[rest.find('T') + 1 : -1]
            if(entry['published'] <= latestTime):
                print('continue')
                continue
            #print(time)
            #print(entry)

            try:
                html1 = requests.get(entry_data['link'], timeout=5)
                html = html1.content
                soup = BeautifulSoup(html, features='lxml')
                texts = soup.findAll(text=True)
                visible_texts = filter(tag_visible, texts)
                text = u" ".join(t.strip() for t in visible_texts)
            except:
                print('bad request')
                text = 'bad request'
            print('text')

            entry_data['title']     = entry['title']
            entry_data['published'] = entry['published']
            entry['keywords'] = self.get_keywords(text, feed[2:])
            self.save(range_, entry_data)

    def get_keywords(self, text, keyword_data):
        print(text)
        keyword_counts = []
        keywords = keyword_data[0].split(',')
        keywords = [keyword.strip() for keyword in keywords]
        print(keywords)
        #first column s set of individual keywords
        for keyword in keywords:
            keyword_counts.append(text.count(keyword))

        #other columns are groupings that share count
        for keyword_grouping in keyword_data[1:]:
            count = 0
            print(keyword_grouping)
            keyword_grouping = keyword_grouping.split(',')
            keyword_grouping = [keyword.strip() for keyword in keyword_grouping]
            for keyword in keyword_grouping:
                if(keyword == ''): continue
                count = count + text.count(keyword)
            keyword_counts.append(count)

        return keyword_counts

    def save(self, range_, entry_data):
        values = [entry_data['title'], entry_data['link'], entry_data['published'], entry_data['year'], entry_data['month'], entry_data['day']]
        values.append(entry_data['keywords'])
        value_range_body = {
            "range": range_,
            "majorDimension": 'ROWS',
            "values": values
        }
        request = self.service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=range_, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
        response = request.execute()
        print(response)

    def getFeeds(self, range_):
        rows = self.service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range_).execute()
        #futures = {executor.submit(self.parseFeed, feed): feed for feed in rows['values']}
        #concurrent.futures.wait(futures)
        self.parseFeed(rows['values'][0])


def main():
    parser = GSheetsParser('C:\\rssIn\\mentionsTracker\\token.pickle')
    parser.getFeeds('Keywords')
    
    

if __name__ == "__main__":
    main()