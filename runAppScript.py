# POST https://script.googleapis.com/v1/scripts/{scriptId}:run
import json
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build


import requests

with open('client_secret.json', 'r') as file:
    credentials = json.load(file)

# Extract OAuth 2.0 credentials
CLIENT_ID = credentials['web']['client_id']
CLIENT_SECRET = credentials['web']['client_secret']
AUTH_URI = credentials['web']['auth_uri']
TOKEN_URI = credentials['web']['token_uri']
REDIRECT_URI = 'http://localhost:8000/callback'



def refresh_access_token(refresh_token: str) -> Optional[str]:
    response = requests.post(TOKEN_URI, auth=(CLIENT_ID, CLIENT_SECRET), data={
        'refresh_token': refresh_token,
        # 'client_id': CLIENT_ID,
        # 'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token'
    })

    tokens = response.json()
    new_access_token = tokens.get('access_token')

    if new_access_token:
        return new_access_token
    else:
        return None


# ACCESS_TOKEN = refresh_access_token("1//0gJx9fJppz4e_CgYIARAAGBASNwF-L9IriBkYcsrX0YaLHSYl_jyKzq5WuX1PsjM_IGXYRizGTZdQHfi0Rtm6BGx6LoLrOCUZLMo")
# print(ACCESS_TOKEN)

SCRIPT_ID = '1m5uO5lfq0-LNC8mnprist3Uo6g492jCS2Klkitfsf5F2DKM8KbPfCIGN'
deployment_id = 'AKfycbznMSl3-Rv3lDbJCDKcLYb-_-vRqpcrl_k-SXmDvL57dZJi5RIQWARtz2U9Y6rnSuZa'
ACCESS_TOKEN = "ya29.a0AcM612wf4XekBqzZoDDOLC4O2ILgNjlYyEDuruqjrDtS874z4i8gi8bCDAHBi0VlmIQOd5WW85N0enPgX8PYtIBFAJFs0VsfjlEFXEdBm9RYWVoBl9IgaaXhDThe9KWLVqK-HPgN0raC6Xhi224LpCEl0l6M4nRDLmXGaCgYKAZ8SARASFQHGX2MiCY5f7ISUPVwX5jXT2yi_xQ0171"


def run_script(function_name):
    url = f'https://script.googleapis.com/v1/scripts/{SCRIPT_ID}:run'
    headers = {
        'Authorization': 'Bearer ya29.a0AcM612wf4XekBqzZoDDOLC4O2ILgNjlYyEDuruqjrDtS874z4i8gi8bCDAHBi0VlmIQOd5WW85N0enPgX8PYtIBFAJFs0VsfjlEFXEdBm9RYWVoBl9IgaaXhDThe9KWLVqK-HPgN0raC6Xhi224LpCEl0l6M4nRDLmXGaCgYKAZ8SARASFQHGX2MiCY5f7ISUPVwX5jXT2yi_xQ0171',
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "function": "run"
    })
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text


# response = run_script('run')
# print(response)
# if 'error' in response:
#     print(f"Error: {response['error']['message']}")
# else:
#     print(f"Script executed successfully: {response['response']['result']}")
#
#
with open('certiphicate.json', 'r') as file:
    creds = json.load(file)
credentials = service_account.Credentials.from_service_account_info(creds, scopes=['https://www.googleapis.com/auth/script.external_request https://www.googleapis.com/auth/script.projects https://www.googleapis.com/auth/script.deployments https://www.googleapis.com/auth/script.scriptapp https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/documents'])
service = build("script", "v1", credentials=credentials)
request = {"function": "run"}
response = service.scripts().run(scriptId=deployment_id, body=request).execute()
print(response)


def run_apps_script():
    url = "https://script.googleapis.com/v1/scripts/AKfycbznMSl3-Rv3lDbJCDKcLYb-_-vRqpcrl_k-SXmDvL57dZJi5RIQWARtz2U9Y6rnSuZa:run"

    payload = json.dumps({
      "function": "run"
    })
    headers = {
      'Authorization': 'Bearer ya29.a0AcM612wf4XekBqzZoDDOLC4O2ILgNjlYyEDuruqjrDtS874z4i8gi8bCDAHBi0VlmIQOd5WW85N0enPgX8PYtIBFAJFs0VsfjlEFXEdBm9RYWVoBl9IgaaXhDThe9KWLVqK-HPgN0raC6Xhi224LpCEl0l6M4nRDLmXGaCgYKAZ8SARASFQHGX2MiCY5f7ISUPVwX5jXT2yi_xQ0171',
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return(response.json())
# print(run_apps_script())