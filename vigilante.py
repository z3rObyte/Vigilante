#!/usr/bin/env python3
import sys
import requests
import signal
import re
import json
import string
import random
import gzip
import urllib.request
from urllib.parse import unquote
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def random_password(length):
    random_str = ''.join(random.choice(string.ascii_lowercase) for i in range(length-2)) + random.choice(string.ascii_uppercase) + random.choice(string.digits)
    random_str += random.choice(string.ascii_uppercase)

    return random_str

def ctrl_c(sig, frame):
    print("\n[+] Saliendo...")
    sys.exit(1)
signal.signal(signal.SIGINT, ctrl_c)

def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    ]
    header = {
        "User-Agent": random.choice(user_agents)
    }
    return header

def pornhub(email):
    # get token
    url = "https://www.pornhub.com/signup"
    s = requests.Session()
    s.cookies.set("accessAgeDisclaimerPH", "1", domain=".pornhub.com")
    s.cookies.set("platform", "pc", domain=".pornhub.com")
    s.headers.update(random_user_agent())
    r = s.get(url)
    token = re.findall("token=(.*?)\"", r.text)[-1]

    # check email
    url = "https://www.pornhub.com/user/create_account_check"
    s.headers.update({"X-Requested-With":"XMLHttpRequest"})
    r = s.post(url, params={"token":token}, data={"check_what":"email", "email":email})
    
    return "has been taken" in r.text
    
def xvideos(email):
    url = "https://www.xvideos.com"
    s = requests.Session()
    s.headers.update({"X-Requested-With":"XMLHttpRequest"})
    s.headers.update(random_user_agent())
    r = s.get(url)
    r = s.get(url+'/account/checkemail', params={'email':email})
    return "is already in use" in r.text

def duolingo(email):
    url = "https://www.duolingo.com/2017-06-30/users"
    data={
    "timezone":"CET",
    "fromLanguage":"en",
    "age":"20",
    "email":email,
    "identifier":"",
    "name":"",
    "password":"",
    "username":None
    }
    r = requests.post(url, headers=random_user_agent(), params={"fields":"id"}, json=data)
    return "EMAIL_TAKEN" in r.text

def instagram(email):
    url = "https://www.instagram.com"
    
    s = requests.Session()
    s.headers.update(random_user_agent())
    r = s.get(url)
    CSRF_token = s.cookies.get_dict()['csrftoken']
    data = {
        "email":email,
        "first_name":"",
        "username":"",
        "opt_into_one_tap":False
        }
    s.headers.update({"X-CSRFToken":CSRF_token})
    r = s.post(url+'/api/v1/web/accounts/web_create_ajax/attempt/', data=data)
    return "email_is_taken" in r.text

def twitter(email):
    url = "https://api.twitter.com/i/users/email_available.json"
    params = {
        "email":email
    }
    random_user_agent().update({"Accept-Language":"en-US,en;q=0.5"})
    r = requests.get(url, params=params, headers=random_user_agent())
    return "has already been taken" in r.text

def hackthebox(email):
    url = "https://labs.hackthebox.com/api/v4/register/check"
    data = {
        "type":"email",
        "input":email
        }
    r = requests.post(url, headers=random_user_agent(), json=data)
    json_string = json.loads(r.text)
    
    return json_string['message']['found']

def callofduty(email):
    data = {
        'email': email
    }
    r = requests.post("https://profile.callofduty.com/cod/signup/checkEmail", headers=random_user_agent(), data=data)
    parsed_json = json.loads(r.text)
    
    return "already in use." in ''.join(parsed_json['exceptionMessageList'])

def spotify(email):
    url = "https://spclient.wg.spotify.com/signup/public/v1/account"
    params = f"?validate=1&email={email}"
    req = urllib.request.Request(url+params, headers=random_user_agent())
    response = urllib.request.urlopen(req)
    
    if response.info().get('Content-Encoding') == 'gzip':
        gzip_file = gzip.GzipFile(fileobj=response)
        decoded_data = gzip_file.read()
    else:
        decoded_data = response.read()
    
    parsed_json = json.loads(decoded_data)
    try:
        error = parsed_json['errors']['email']
    except KeyError:
        return False
    return 'is already registered' in parsed_json['errors']['email']

def stackoverflow(email):
    
    headers = random_user_agent()
    headers['Referer']='https://stackoverflow.com/users/signup?ssrc=head&returnurl=https://stackoverflow.com/'

    data = {
        'email': email,
        'password': random_password(8),
        'oauth_version': '',
        'oauth_server': '',
    }

    r = requests.post('https://stackoverflow.com/users/signup?ssrc=head&returnurl=https://stackoverflow.com/', headers=headers, data=data, verify=False, allow_redirects=True)
    soup = BeautifulSoup(r.text, 'html.parser')
    title = soup.find('title')
    return 'account recovery' in title.string.lower()
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"[+] Usage: {sys.argv[0]} test@test.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    if pornhub(email):
        print(f"[+] Registered in pornhub.com")
    if xvideos(email):
        print(f"[+] Registered in xvideos.com")
    if duolingo(email):
        print(f"[+] Registered in duolingo.com")
    if instagram(email):
        print(f"[+] Registered in instagram.com")
    if twitter(email):
        print(f"[+] Registered in twitter.com")
    if hackthebox(email):
        print(f"[+] Registered in labs.hackthebox.com")
    if callofduty(email):
        print(f"[+] Registered in callofduty.com")
    if spotify(email):
        print("[+] Registered in spotify.com")
    if stackoverflow(email):
        print("Registered in stackoverflow.com")
