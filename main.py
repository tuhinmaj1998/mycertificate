import os

import pandas as pd
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Query
# from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from TemplateDataFitting import templateDataFit, CreatePDFsInGdrive
from downloadDocx import registeredTemplateList, download_file_from_google_drive, extract_variables_from_template, \
    delete_files_in_folder
from extractGsheet import fetch_post_data

load_dotenv()

extractGsheet_url = os.getenv('extractGsheet_url')
get_gsheetslist_url = os.getenv('get_gsheetslist_url')
registered_template_url = os.getenv('registered_template_url')
generateSampleCertGdrive_url = os.getenv('generateSampleCertGdrive_url')
appscript_key = os.getenv('appscript_key')  # '123'
embedded_template_url = os.getenv('embedded_template_url')  # '123'
zip_download_url = os.getenv('zip_download_url')  # '123'

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

    # print('is_sample: ', is_sample)
    # print('template_file_id: ', template_file_id)
    # print('spreadsheet_url: ', spreadsheet_url)
    # print('sheetname: ', sheetname)
    # print('gsheet_columnwise_data: ', gsheet_columnwise_data)
    # print('column_mapping: ', column_mapping)

    pdf_files = CreatePDFsInGdrive(generateSampleCertGdrive_url, is_sample, template_file_id, spreadsheet_url,
                                   sheetname, gsheet_columnwise_data, column_mapping)
    print(pdf_files)
    return pdf_files


@app.post("/submitData")
async def submitData(request: Request):
    submitted_data = await request.json()
    print(submitted_data)
    return submitted_data

@app.post("/embeddedTemplate")
async def embeddedTemplate(request: Request):
    submitted_data = await request.json()
    template_id = submitted_data['template_id']
    embedded_template_full_url = f'{embedded_template_url}?template_file_id={template_id}'
    embedded_template_preview = requests.get(embedded_template_full_url).json()
    print(embedded_template_preview['pdf_url'])
    return embedded_template_preview['pdf_url']


@app.post("/downloadPdfZip")
async def downloadPdfZip(request:Request):
    folder_data = await request.json()
    print(folder_data)
    folder_url = folder_data
    print('folder_url', folder_url)
    zip_url = f'{zip_download_url}?folder_url={folder_url}'
    response = requests.get(zip_url).json()
    print(response)
    return response
