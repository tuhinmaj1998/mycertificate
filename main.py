import json
import os
from typing import Optional
from urllib.parse import urlencode

import pandas as pd
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
# from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from TemplateDataFitting import templateDataFit, CreatePDFsInGdrive
from downloadDocx import registeredTemplateList, download_file_from_google_drive, extract_variables_from_template, \
    delete_files_in_folder
from extractGsheet import fetch_post_data

load_dotenv()

user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"

extractGsheet_url = os.getenv('extractGsheet_url')
get_gsheetslist_url = os.getenv('get_gsheetslist_url')
registered_template_url = os.getenv('registered_template_url')
generateSampleCertGdrive_url = os.getenv('generateSampleCertGdrive_url')
appscript_key = os.getenv('appscript_key')  # '123'
embedded_template_url = os.getenv('embedded_template_url')  # '123'
zip_download_url = os.getenv('zip_download_url')  # '123'
SECRET_KEY = os.getenv('SECRET_KEY')

with open('client_secret.json', 'r') as file:
    credentials = json.load(file)

# Extract OAuth 2.0 credentials
CLIENT_ID = credentials['web']['client_id']
CLIENT_SECRET = credentials['web']['client_secret']
AUTH_URI = credentials['web']['auth_uri']
TOKEN_URI = credentials['web']['token_uri']
# REDIRECT_URI = 'http://localhost:8000/callback'
REDIRECT_URI = credentials['web']['redirect_uris'][1]#'http://localhost:8000/callback'

# Your secret key for sessions
# SECRET_KEY = '1234'  # os.getenv('SECRET_KEY', 'default_secret_key')  # Replace with a secure key

# Add session middleware for storing tokens

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='templates')


@app.get('/login')
async def login():
    authorization_url = (
        f'{AUTH_URI}?response_type=code'
        f'&client_id={CLIENT_ID}'
        f'&redirect_uri={REDIRECT_URI}'
        f'&scope=email '
        # f'https://www.googleapis.com/auth/script.external_request '
        f'https://www.googleapis.com/auth/userinfo.email '
        f'https://www.googleapis.com/auth/script.projects '
        # f'https://www.googleapis.com/auth/script.deployments '
        f'https://www.googleapis.com/auth/script.scriptapp '
        f' https://www.googleapis.com/auth/drive '
        f' https://www.googleapis.com/auth/documents '
        f' https://www.googleapis.com/auth/spreadsheets '
        f'&access_type=offline'  # Request offline access to get a refresh token
        f'&prompt=consent'  # Ensure that Google prompts the user for consent
    )
    # print(authorization_url)
    return RedirectResponse(url=authorization_url)


@app.get('/callback')
async def callback(code: str, request: Request):
    response = requests.post(TOKEN_URI, data={
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    })

    tokens = response.json()
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')

    # print("access_token: ", access_token)
    # print(refresh_token)
    if access_token:
        request.session['access_token'] = access_token
        request.session['refresh_token'] = refresh_token

        new_access_token = access_token
        headers = {'Authorization': f'Bearer {new_access_token}'}
        user_info_response = requests.get(user_info_url, headers=headers)

        print(user_info_response.content)
        if user_info_response.status_code == 401:  # Unauthorized, likely expired token
            new_access_token = refresh_access_token(refresh_token)
            if new_access_token:
                request.session['access_token'] = new_access_token
                headers['Authorization'] = f'Bearer {new_access_token}'
                user_info_response = requests.get(user_info_url, headers=headers)
            else:
                return RedirectResponse(url='/login')

        if user_info_response.status_code != 200:
            return HTMLResponse(f"Error fetching user info: {user_info_response.text}",
                                status_code=user_info_response.status_code)

        user_info = user_info_response.json()
        request.session['user_info'] = user_info
        email = user_info.get('email', 'No Email Found')
        print(user_info)

        return RedirectResponse(url='/')
    else:
        return HTMLResponse(f"Error: Unable to retrieve access token. Response: {tokens}", status_code=400)


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


@app.get('/profile', response_class=HTMLResponse)
async def profile(request: Request):
    access_token = request.session.get('access_token')

    # Check if access token is expired (basic error handling approach)

    headers = {'Authorization': f'Bearer {access_token}'}
    user_info_response = requests.get(user_info_url, headers=headers)

    if user_info_response.status_code != 200:  # Unauthorized, likely expired token
        return RedirectResponse(url='/login')


    user_info = user_info_response.json()
    request.session['user_info'] = user_info
    email = user_info.get('email', 'No Email Found')
    print(user_info)


    # Render template
    template = templates.get_template('profile.html')
    return template.render(email=email, user_info=user_info)


@app.get('/login_page', response_class=HTMLResponse)
async def login_page():
    template = templates.get_template('login.html')
    return template.render()


@app.get('/logout')
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url='/login')


@app.get("/mydata")
async def home(request: Request):
    myEmail = requests. \
        get(
        'https://script.google.com/macros/s/AKfycbwfosUsiug0iFbR4gIGxP6mdGgfrYSzHSpqrEx4VJj1Lankemnu5b_b1OLQ3bOFDBRy/exec').content
    print(myEmail)
    return HTMLResponse(content=myEmail, status_code=200)


@app.get("/")
async def home(request: Request):
    user_info = request.session.get('user_info', None)
    return templates.TemplateResponse("home.html", {"request": request, "user_info":user_info, "nav":"Home"})


@app.get("/getRegisteredTemplate/")
async def getRegisteredTemplate(request: Request, refresh: int = Query(..., description="Refresh value (1 or 0)")):
    access_token = request.session.get('access_token')
    refresh_token = request.session.get('refresh_token')
    new_access_token = access_token
    if not new_access_token:
        return RedirectResponse(url='/login')

    refresh_val = refresh
    headers = {
        "Authorization": f"Bearer {new_access_token}"
    }
    rTemplates_response = requests.get(registered_template_url, headers=headers)

    if rTemplates_response.status_code == 401:  # Unauthorized, likely expired token
        new_access_token = refresh_access_token(refresh_token)
        if new_access_token:
            request.session['access_token'] = new_access_token
            headers['Authorization'] = f'Bearer {new_access_token}'
            rTemplates_response = requests.get(registered_template_url, headers=headers)
        else:
            return RedirectResponse(url='/login')
    print('rTemplates_response: ', rTemplates_response.text)
    if rTemplates_response.status_code != 200:
        return RedirectResponse(url=f'/error?error_text={rTemplates_response.text}&status_code={rTemplates_response.status_code}')

    rTemplates_content = rTemplates_response.content
    rTemplates = json.loads(rTemplates_content)['data']
    print(rTemplates)
    templateInfoList = []

    if refresh_val == 1 or refresh_val == 0:
        for i in rTemplates:
            templateInfoList.append(i)
        return templateInfoList


@app.get("/getRegisteredTemplate_/")
async def getRegisteredTemplate_(refresh: int = Query(..., description="Refresh value (1 or 0)")):
    refresh_val = refresh
    rTemplates = registeredTemplateList(registered_template_url)
    templateInfoList = []

    template_folder_loc = 'static/docx-template'
    if refresh_val == 1:
        delete_files_in_folder(template_folder_loc)
    for i in rTemplates:
        file_loc = f'{template_folder_loc}/{i["id"]}.docx'
        print(file_loc)
        if refresh_val == 1:
            download_file_from_google_drive(i['id'], file_loc)
        identified_temp_Cols = extract_variables_from_template(file_loc)
        print(identified_temp_Cols)
        i['loc'] = file_loc
        i['variable'] = identified_temp_Cols
        templateInfoList.append(i)

    return templateInfoList


# @app.get("/registeredTemplate/columns")
# async def registeredTemplate(request:Request):
#     rTemplates = registeredTemplateList(registered_template_url)
#     return rTemplates

@app.get("/get_gsheetslist")
async def Get_gsheetslist_url(request:Request):
    access_token = request.session.get('access_token')
    if not access_token:
        return RedirectResponse(url='/login')
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(get_gsheetslist_url, headers=headers)

    if response.status_code != 200:
        return RedirectResponse(url=f'/error?error_text={response.text}&status_code={response.status_code}')#, error_text=response.text, status_code=response.status_code)
        # return HTMLResponse(f"Error fetching user info: {response.text}<br>Please Try Again!",
        #                     status_code=response.status_code)
    get_gsheetslists_data = response.json()
    return get_gsheetslists_data['sheetData']


@app.post("/fetchgsheet")
async def fetchgsheet(request: Request):
    form_data = await request.json()

    access_token = request.session.get('access_token')
    if not access_token:
        return RedirectResponse(url='/login')
    headers = {'Authorization': f'Bearer {access_token}'}

    spreadsheet_url = form_data.get("spreadsheet_url")
    sheetname = form_data.get("sheetname")
    password = form_data.get("password")

    submit_response = {
        'spreadsheet_url': spreadsheet_url,
        'sheetname': sheetname,
        'key': appscript_key,
        'password': password
    }

    post_response = fetch_post_data(extractGsheet_url, submit_response, headers)

    if post_response['code'] != 200:
        return RedirectResponse(url=f'/error?error_text={str(post_response["msg"])}&status_code={post_response["code"]}')
        # return HTMLResponse(f"Error fetching user info: {post_response['msg']}<br>Please Try Again!",
        #                     status_code=post_response['code'])

    records = pd.DataFrame(post_response['msg']['data'])
    # print(records.to_string(index=False))
    return post_response['msg']['data']


# @app.post("/fetchgsheetColumns")
# async def fetchgsheetColumns(request: Request):
#     post_response_data = await fetchgsheet(request)
#     records_df = pd.DataFrame(post_response_data)
#     identified_columns = records_df.columns.to_list()
#     return identified_columns


@app.get("/organiser")
async def organiser(request: Request):
    access_token = request.session.get('access_token', None)
    if access_token == None:
        return RedirectResponse(url='/login')
    user_info = request.session.get('user_info', None)
    if user_info is None:
        return RedirectResponse(url='/login')
    return templates.TemplateResponse("organiser.html", {"request": request, "user_info": user_info, "nav":"Organiser"})


# @app.post("/generateSampleCert")
# async def generateSampleCert(request: Request):
#     form_data = await request.json()
#     pdf_file = templateDataFit(form_data, is_sample=1)
#     print(pdf_file)
#     return pdf_file


@app.post("/generateCertGdrive")
async def generateCertGdrive(request: Request):
    form_data = await request.json()
    is_sample = form_data.get("is_sample")
    template_file_id = form_data.get("template_id")
    spreadsheet_url = form_data.get("spreadsheet_url")
    sheetname = form_data.get("sheetname")
    gsheet_columnwise_data = form_data.get("gsheet_columnwise_data")
    column_mapping = form_data.get("column_mapping")

    access_token = request.session.get('access_token')
    if not access_token:
        return RedirectResponse(url='/login')
    headers = {'Authorization': f'Bearer {access_token}'}

    post_response = CreatePDFsInGdrive(generateSampleCertGdrive_url, is_sample, template_file_id, spreadsheet_url,
                                   sheetname, gsheet_columnwise_data, column_mapping, headers)

    print('post_response: ', post_response['data'])
    # if post_response.get('code',None) is not None and post_response.get('error',None) is not None:
    #     print('This is what I want!')
    #     params = {'error_text': str(post_response.get("error", None)), 'status_code': 401}
    #     query_string = urlencode(params)
    #     return RedirectResponse(url=f'/error?{query_string}', status_code=303)
        # return HTMLResponse(f"Error fetching user info: {post_response['data']}<br>Please Try Again!",
        #                     status_code=post_response['code'])

    # print(post_response)
    return post_response['data']


@app.post("/submitData")
async def submitData(request: Request):
    submitted_data = await request.json()
    print(submitted_data)
    return submitted_data


# @app.post("/embeddedTemplate")
# async def embeddedTemplate(request: Request):
#     submitted_data = await request.json()
#     template_id = submitted_data['template_id']
#     embedded_template_full_url = f'{embedded_template_url}?template_file_id={template_id}'
#     embedded_template_preview = requests.get(embedded_template_full_url).json()
#     print(embedded_template_preview['pdf_url'])
#     return embedded_template_preview['pdf_url']


@app.post("/downloadPdfZip")
async def downloadPdfZip(request: Request):
    folder_data = await request.json()
    print(folder_data)
    folder_url = folder_data
    print('folder_url', folder_url)
    access_token = request.session.get('access_token')
    if access_token is None:
        return RedirectResponse(url='/login')
    headers = {'Authorization': f'Bearer {access_token}'}
    print(headers)
    zip_url = f'{zip_download_url}?folder_url={folder_url}'
    response = requests.get(url=zip_url, headers=headers)

    if response.status_code != 200:
        return RedirectResponse(
            url=f'/error?error_text={str(response.text)}&status_code={response.status_code}')
        # return HTMLResponse(f"Error fetching user info: {response.text}<br>Please Try Again!",
        #                     status_code=response.status_code)
    print(response.json())
    return response.json()


# @app.post('/error', response_class=HTMLResponse)
@app.get('/error', response_class=HTMLResponse)
def error(request: Request, error_text: str = Query(...), status_code: int = Query(...)):
    user_info = request.session.get('user_info', None)
    try:
        print(error_text)
        print(status_code)
    except Exception as e:
        print(str(e))
    template = templates.get_template('error.html')
    return template.render(error_text=error_text, status_code=status_code, user_info=user_info)

# @app.get('/e')
# def e(request:Request):
#     return RedirectResponse(url=f'/error?error_text=rTemplates_response&status_code=201')