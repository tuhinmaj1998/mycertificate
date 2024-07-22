import os
import pandas as pd
import requests
from fastapi import FastAPI, Request, Query
# from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from TemplateDataFitting import templateDataFit, CreatePDFsInGdrive
from downloadDocx import registeredTemplateList, download_file_from_google_drive, extract_variables_from_template, \
    delete_files_in_folder
from extractGsheet import fetch_post_data

import os
from dotenv import load_dotenv, dotenv_values
load_dotenv()


extractGsheet_url = os.getenv('extractGsheet_url') # 'https://script.google.com/macros/s/AKfycby3X7uvFqiU3NN2FnjhtxryNGFPU__wqXxBTGOtr-cQwk-z3y8ZLSkJ5Abku8-A6Ycg/exec'
get_gsheetslist_url = os.getenv('get_gsheetslist_url') # 'https://script.google.com/macros/s/AKfycbzOwM4ugHnmdG01V7zEWzene8ON4QVUZ9SPASTAHFxxoEDgoHiEF4_V17ksrm-NUHsL_g/exec'
registered_template_url = os.getenv('registered_template_url') # 'https://script.google.com/macros/s/AKfycbz2jE3eg4mdxe4cTArHWLf9ylGSgc_CyDtou7kHJ-tzvMjiNuciOSUP9H1KjXkmuK8z/exec'
generateSampleCertGdrive_url = os.getenv('generateSampleCertGdrive_url') # 'https://script.google.com/macros/s/AKfycbw0csSAN8OoZnkB-J1KUFY_50t4oXwh9df0B1o2JLsBWpH40mN1ytzuXCh9ijGXQ27-SQ/exec'
appscript_key = os.getenv('appscript_key') # '123'

print(os.environ.get('ExtractGsheet_url'))
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='templates')


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/getRegisteredTemplate_")
async def getRegisteredTemplate_(request: Request):
    rTemplates = registeredTemplateList(registered_template_url)
    return rTemplates


@app.get("/getRegisteredTemplate/")
async def getRegisteredTemplate(refresh: int = Query(..., description="Refresh value (1 or 0)")):
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
async def Get_gsheetslist_url():
    response = requests.get(get_gsheetslist_url)
    get_gsheetslists_data = response.json()
    return get_gsheetslists_data['sheetData']

@app.post("/fetchgsheet")
async def fetchgsheet(request: Request):
    form_data = await request.json()
    spreadsheet_url = form_data.get("spreadsheet_url")
    sheetname = form_data.get("sheetname")
    password = form_data.get("password")

    submit_response = {
        'spreadsheet_url': spreadsheet_url,
        'sheetname': sheetname,
        'key': appscript_key,
        'password': password
    }

    post_response = fetch_post_data(extractGsheet_url, submit_response)
    records = pd.DataFrame(post_response['msg']['data'])
    # print(records.to_string(index=False))
    return post_response['msg']['data']


@app.post("/fetchgsheetColumns")
async def fetchgsheetColumns(request: Request):
    post_response_data = await fetchgsheet(request)
    records_df = pd.DataFrame(post_response_data)
    identified_columns = records_df.columns.to_list()
    return identified_columns


@app.get("/organiser")
async def organiser(request: Request):
    return templates.TemplateResponse("organiser.html", {"request": request})


@app.post("/generateSampleCert")
async def generateSampleCert(request: Request):
    form_data = await request.json()
    pdf_file = templateDataFit(form_data, is_sample=1)
    print(pdf_file)
    return pdf_file


@app.post("/generateCertGdrive")
async def generateCertGdrive(request: Request):
    form_data = await request.json()
    is_sample = form_data.get("is_sample")
    template_file_id = form_data.get("template_id")
    spreadsheet_url = form_data.get("spreadsheet_url")
    sheetname = form_data.get("sheetname")
    gsheet_columnwise_data = form_data.get("gsheet_columnwise_data")
    column_mapping = form_data.get("column_mapping")

    print('is_sample: ', is_sample)
    print('template_file_id: ', template_file_id)
    print('spreadsheet_url: ', spreadsheet_url)
    print('sheetname: ', sheetname)
    print('gsheet_columnwise_data: ', gsheet_columnwise_data)
    print('column_mapping: ', column_mapping)


    pdf_files = CreatePDFsInGdrive(generateSampleCertGdrive_url, is_sample, template_file_id, spreadsheet_url,
                                   sheetname, gsheet_columnwise_data, column_mapping)
    print(pdf_files)
    return pdf_files


@app.post("/submitData")
async def submitData(request: Request):
    submitted_data = await request.json()
    print(submitted_data)
    return submitted_data
