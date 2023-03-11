from __future__ import print_function

import requests
from lxml import html
import json
from datetime import date
from datetime import timedelta
import time

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

session_requests = requests.session()

def scrape_browser_site():
    ###FOR LOGGING INTO BROWSER APP###
    ###NOT USED###
    login_url = "https://www.moonboard.com/Account/Login"
    result = session_requests.get(login_url)

    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='__RequestVerificationToken']/@value")))[0]

    payload = {
        "Login.Username" : "Ctarry_dummy",
        "Login.Password" : "r2m5k9r3b2v8",
        "__RequestVerificationToken" : authenticity_token
    }

    result = session_requests.post(
        login_url, 
        data = payload, 
        headers = dict(referer=login_url)
    )

def scrape_moonboard_data(country, pages, setupID="1"):
    rankings_url = "https://www.moonboard.com/Ranking/GetRankings?userid=2b3ba803-6ada-4393-94a8-50250d243a21&setupId=" + setupID + "&configurationId=0"

    headers = { 
        "Host": "www.moonboard.com",
        "Origin": "https://www.moonboard.com",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8",
        "Accept-Encoding" : "gzip, deflate, br",
        "Connection": "keep-alive",
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "Referer": "https://www.moonboard.com/ranking/index/1/0?ui=2b3ba803-6ada-4393-94a8-50250d243a21",
        "Content-Length": "39",
        "X-Requested-With": "XMLHttpRequest",
    }
    rankings_payload = {
        "sort" : "",
        "page" : str(pages),
        "pageSize" : "50",
        "group" : "",
        "filter" : "country~eq~'"+ country + "'"
    }

    result = session_requests.post(
        rankings_url, 
        data = rankings_payload, 
        headers = headers 
    )

    raw_data = result.content
    return raw_data

def decode_data(raw_data): # returns a list dictionarys, in order of ranking
    data = json.loads(raw_data.decode())['Data']
    return data

def scrape_todays_data(country, pages, setupID):
    data_today = []
    for page in range(1, pages + 1):
        raw_data = scrape_moonboard_data(country, page, setupID)
        new_people = decode_data(raw_data)
        data_today.extend(new_people)
    return data_today

def moon_day():
    #Returns string of moon day
    t = time.localtime()
    actual_day = date.today()
    if 22 <= t.tm_hour:
        delta = timedelta(days = 1)
        moon_day = str(actual_day + delta)
    else:
        moon_day = str(actual_day)
    return moon_day

def scrape_and_save(country='canada', pages=4, setupID="1"):
    data_file_name = country + "_data.json"
    with open(data_file_name, "r+") as json_data:
        data = json.load(json_data)

        if moon_day() in data:
            print("Already have data for this date")
        else:
            data_today = scrape_todays_data(country, pages, setupID)
            data[moon_day()] = data_today
            json_data.seek(0)
            json.dump(data, json_data)
    return

def todays_ranking_from_db():
    with open("canada_data.json", "r") as json_data:
        data = json.load(json_data)
        names = []

        if moon_day() in data:
            for entry in data[moon_day()]:
                names.append(entry["Nickname"])
    return names

def ranking_by_id(day):
    with open("canada_data.json", "r") as json_data:
        data = json.load(json_data)
        ranking = {}
        for entry in data[day]:
            ranking[entry["Id"]] = entry["GlobalRanking"]
    return(ranking)

def api_data_object1():

    data_values = todays_ranking_from_db()
    data_values.insert(0, moon_day())

    start_date_ord = date(2023, 2, 9).toordinal()
    current_date_ord = date.fromisoformat(moon_day()).toordinal()
    date_delta = current_date_ord - start_date_ord
    column_letter = convert_index_to_column_letter(date_delta + 2)

    data_range = 'Data!' + column_letter + ':' + column_letter

    major_dimension = 'COLUMNS'

    return {
            "range": data_range,
            "majorDimension": major_dimension,
            "values": [
                data_values
            ]
        }

def api_data_object2():

    data_values = todays_ranking_from_db()
    data_values.insert(0, moon_day())

    data_range = 'Summary!B:B'

    major_dimension = 'COLUMNS'

    return {
            "range": data_range,
            "majorDimension": major_dimension,
            "values": [
                data_values
            ]
        }

def api_data_object3():

    current_date_ord = date.fromisoformat(moon_day()).toordinal()
    current_date_str = moon_day()

    one_day_ago_ord = current_date_ord - 1
    one_day_ago_str = str(date.fromordinal(one_day_ago_ord))

    three_days_ago_ord = current_date_ord - 3
    three_days_ago_str = str(date.fromordinal(three_days_ago_ord))

    seven_days_ago_ord = current_date_ord - 7
    seven_days_ago_str = str(date.fromordinal(seven_days_ago_ord))

    fourteen_days_ago_ord = current_date_ord - 14
    fourteen_days_ago_str = str(date.fromordinal(fourteen_days_ago_ord))

    thirty_days_ago_ord = current_date_ord - 30
    thirty_days_ago_str = str(date.fromordinal(thirty_days_ago_ord))

    six_months_ago_ord = current_date_ord - 182
    six_months_ago_str = str(date.fromordinal(six_months_ago_ord))

    dates = [one_day_ago_str, three_days_ago_str, seven_days_ago_str, fourteen_days_ago_str, six_months_ago_str]

    difference_one = ["1 Day Change"]
    difference_three = ["3 Day Change"]
    difference_seven = ["7 Day Change"]
    difference_fourteen_days = ["14 Day Change"]
    difference_thirty_days = ["30 Day Change"]
    difference_six_months = ["6 Month Change"]

    differences = [difference_one, difference_three, difference_seven, difference_fourteen_days, difference_thirty_days, difference_six_months]

    with open("canada_data.json", "r") as json_data:
        data = json.load(json_data)
        
        todays_rankings = data[moon_day()]
        for index, date_str in enumerate(dates):
            if date_str in data:
                rankings_by_id = ranking_by_id(date_str)
                for entry in todays_rankings:
                    entry_id = entry["Id"]
                    if entry_id in rankings_by_id:
                        difference = rankings_by_id[entry_id] - entry["GlobalRanking"]
                        differences[index].append(difference)

    data_range = 'Summary!C1:H501'

    major_dimension = 'COLUMNS'

    return {
            "range": data_range,
            "majorDimension": major_dimension,
            "values": differences
        }


def convert_index_to_column_letter(column_int):
    start_index = 1   #  it can start either at 0 or at 1
    letter = ''
    while column_int > 25 + start_index:   
        letter += chr(65 + int((column_int-start_index)/26) - 1)
        column_int = column_int - (int((column_int-start_index)/26))*26
    letter += chr(65 - start_index + (int(column_int)))
    return letter
    

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = '18CM8fMSVbMRrzSucN_tHQL_HH2Swmx-fCv4G1q2AEac'

def upload_data(data1=None, data2=None, data3=None):

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        batch_update_values_request_body = {
            'value_input_option' : 'RAW',
            'data' : [data1, data2, data3]
        }

        # Add list of today's climbers to data sheet
        sheet = service.spreadsheets()
        request = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                    body=batch_update_values_request_body)
        response = request.execute()

        # Update summary ranking to today's ranking
        request = sheet.values().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                    body=batch_update_values_request_body)
        response = request.execute()
        print(response)

    except HttpError as err:
        print(err)

scrape_and_save("Canada", 10)
scrape_and_save("united states", 20)
upload_data(api_data_object1(),api_data_object2(),api_data_object3())
