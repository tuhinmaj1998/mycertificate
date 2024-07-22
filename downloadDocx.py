import requests
from docxtpl import DocxTemplate
import json
import os

def delete_files_in_folder(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)

    # Iterate over all files and delete them
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                print(f"{file_path} is not a file.")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")


def download_file_from_google_drive(file_id, destination):
    export_url = f"https://docs.google.com/feeds/download/documents/export/Export?id={file_id}&exportFormat=docx"
    session = requests.Session()
    response = session.get(export_url, stream=True)
    if response.status_code == 200:
        save_response_content(response, destination)
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

def save_response_content(response, destination):
    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)



#
#
# def download_file_from_google_drive(file_id, destination):
#     URL = "https://docs.google.com/uc?export=download&confirm=1"
#     session = requests.Session()
#     response = session.get(URL, params={"id": file_id}, stream=True)
#     token = get_confirm_token(response)
#     if token:
#         params = {"id": file_id, "confirm": token}
#         response = session.get(URL, params=params, stream=True)
#     save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value
    return None

#
# def save_response_content(response, destination):
#     CHUNK_SIZE = 32768
#     with open(destination, "wb") as f:
#         for chunk in response.iter_content(CHUNK_SIZE):
#             if chunk:  # filter out keep-alive new chunks
#                 f.write(chunk)

def registeredTemplateList(url):
    response = requests.get(url)
    docxFileIds = response.json()['data']

    # jsonFile = open('registered_template.json', 'r')
    # values = json.load(jsonFile)
    # jsonFile.close()

    return docxFileIds


def extract_variables_from_template(template_path):
    try:
        # Load the DocxTemplate object
        tpl = DocxTemplate(template_path)

        # Extract all variables from the template
        variables = set()
        for field in tpl.get_undeclared_template_variables():
            variables.add(field)
        return variables
    except Exception as e:
        return str(e)


# response = requests.get('https://script.google.com/macros/s/AKfycbz2jE3eg4mdxe4cTArHWLf9ylGSgc_CyDtou7kHJ-tzvMjiNuciOSUP9H1KjXkmuK8z/exec')
# docxFileIds = response.json()['data']
# for i in docxFileIds:
#     file_loc = f'static/docx-template/{i["name"]}'
#     print(file_loc)
#     download_file_from_google_drive(i['id'], file_loc)
#     identified_temp_Cols = extract_variables_from_template(file_loc)
#     print(identified_temp_Cols)

