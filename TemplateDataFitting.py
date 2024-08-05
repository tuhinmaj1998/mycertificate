import json
import subprocess
import time
from datetime import datetime as dt

import pandas as pd
import requests
from docxtpl import DocxTemplate

root = '/Users/tuhinmajumder/pythonProject/mycertificate'
static_dir = f'{root}/static'


# static_dir = 'static'
# template_file = f'{static_dir}/docx-template/templatedoc.docx'
# list_csv = f'{static_dir}/sample_feedback.csv'

def convert_docx_to_pdf_with_pages(docx_file, pdf_file):
    try:
        applescript = f'''
            tell application "Pages"
                activate
                set inputDoc to POSIX file "{docx_file}"
                set outputPDF to POSIX file "{pdf_file}"

                -- Open the DOCX document
                open inputDoc

                -- Export as PDF
                export front document to file outputPDF as PDF

                -- Close the document without saving changes
                close front document saving no

                -- Quit Pages
                quit
            end tell
        '''
        subprocess.run(['osascript', '-e', applescript], check=True)
        print(f"Conversion successful: {docx_file} -> {pdf_file}")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed: {e}")


# doc = DocxTemplate(template_file)
# df = pd.read_csv(list_csv)


def convertSampleJsontoDF(sample_response):
    sample_response = sample_response['sample_data']
    df = pd.DataFrame(sample_response)
    df = df.T.reset_index()
    df = df.iloc[:, 1:]
    df.columns = df.iloc[0, :]
    df = df.iloc[1:, :]
    # print(df)
    return df


def templateDataFit(jsonData, is_sample):
    df = convertSampleJsontoDF(jsonData)
    template_id = jsonData['template_id']
    template_file = f'{static_dir}/docx-template/{template_id}.docx'
    for index, row in df.iterrows():
        timestamp_nanoseconds = time.time_ns()
        context = {}
        for column, value in row.items():
            context[column] = value
        context['RNUM'] = 'JGI-' + str(dt.today().year) + "-" + str(
            timestamp_nanoseconds)  # str(hash(str(row['ROLL'])))#'JGI123456'
        print(context)

        # 'RNUM': 'JGI/'+str(dt.year)+"/"+str(timestamp_nanoseconds) #str(hash(str(row['ROLL'])))#'JGI123456'

        doc = DocxTemplate(template_file)
        doc.render(context)

        if is_sample == 1:
            docx_file = f'{static_dir}/sample/docx/output_{str(context["RNUM"])}.docx'
            pdf_file = f'{static_dir}/sample/pdf/output_{str(context["RNUM"])}.pdf'
        else:
            docx_file = f'{static_dir}/output/docx/output/output_{str(row["RNUM"])}.docx'
            pdf_file = f'{static_dir}/output/pdf/output/output_{str(row["RNUM"])}.pdf'

        doc.save(docx_file)
        time.sleep(3)
        convert_docx_to_pdf_with_pages(docx_file, pdf_file)
        pdf_file = pdf_file.split(root)[1]
        return pdf_file


def get_templated_data(gsheet_columnwise_data, column_mapping, is_sample):
    # template_id = response_json['template_id']
    # gsheet_columnwise_data = response_json['gsheet_columnwise_data']
    # column_mapping = response_json['column_mapping']

    template_data = []

    for row in gsheet_columnwise_data:
        timestamp_nanoseconds = time.time_ns()
        rnum = f"JGI-{dt.today().year}-{timestamp_nanoseconds}"

        template_row = {}
        for mapping in column_mapping:
            mapping_df = pd.DataFrame([mapping])
            # print(mapping_df[mapping_df['gsheetColumns']=='Preferred Salutation']['templateColumns'].to_string(index=False))

            # print("mapping['templateColumns']", mapping['templateColumns'])
            # print("mapping['gsheetColumns']", mapping['gsheetColumns'])
            template_column = mapping['templateColumns']
            gsheet_column = mapping['gsheetColumns']
            hardcode_value = mapping['hardcode_value_ifapplicable']

            if gsheet_column == 'others':
                template_row[template_column] = hardcode_value
            else:

                # print('templateCol:', template_column, '\ngsheet_col:', gsheet_column)
                if is_sample == 1:
                    template_row[mapping_df[mapping_df['gsheetColumns'] == gsheet_column]['templateColumns'].to_string(
                        index=False)] = row[template_column]
                else:
                    template_row[template_column] = row[gsheet_column]

        template_row['RNUM'] = rnum
        template_data.append(template_row)

    return template_data


def CreatePDFsInGdrive(url, is_sample, template_file_id, spreadsheet_url, sheetname, gsheet_columnwise_data,
                       column_mapping, headers):
    ''' example:
    var jData = [
      {
        "NAME": "John Doe",
        "SALUTE": "Mr",
        "DATE": "July 18, 2024",
        "COURSENAME": "Course X",
        "RNUM":"123"
      },
      {
        "NAME": "Ashis Kumar Majumder",
        "SALUTE": "Sir",
        "DATE": "July 18, 2024",
        "COURSENAME": "Coursera",
        "RNUM":"124"
      }
    ]
    '''
    submit_response = {}
    submit_response['is_sample'] = is_sample
    submit_response['template_file_id'] = template_file_id
    submit_response['spreadsheet_url'] = spreadsheet_url
    submit_response['sheetname'] = sheetname

    data = get_templated_data(gsheet_columnwise_data, column_mapping, is_sample)
    submit_response['data'] = data

    submit_response = json.dumps(submit_response)
    print(submit_response)
    response = requests.post(url, data=submit_response, headers=headers)  # {"key":"123", 'password':'123'})

    if response.status_code != 200:
        return {"code": response.status_code, "data":response.text}
    response_pdfs = response.json()
    return {"code": response.status_code, "data":response_pdfs}


# print(CreatePDFsInGdrive(
#     url='https://script.google.com/macros/s/AKfycbw0csSAN8OoZnkB-J1KUFY_50t4oXwh9df0B1o2JLsBWpH40mN1ytzuXCh9ijGXQ27-SQ/exec',
#     is_sample=0,
#     template_file_id='1I-J3UUfBpVv8M5q9HDdkEl2zlVbJ0NCUgET_nvRuCw8',
#     spreadsheet_url='https://docs.google.com/spreadsheets/d/1_EqBltrMWdhB6pWDTkoPzFwcZL1C1RT9HJEbvHHUHCY/edit?gid=1267774142#gid=1267774142',
#     sheetname='f1',
#     gsheet_columnwise_data = [
#             # {'Timestamp': '2024-07-10T16:53:24.195Z', 'Email Address': 'skumar123@gmail.com', 'NAME': 'Suraj Kumar', 'SALUTE': 'Mr', 'Tell us about the Experience': 'Good', 'Rate the Session': '3'},
#             # {'Timestamp': '2024-07-10T16:54:45.124Z', 'Email Address': 'kmathur007@gmail.com', 'NAME': 'Kailash Mathur', 'SALUTE': 'Dr', 'Tell us about the Experience': 'Could be more engaging.', 'Rate the Session': '2'},
#             # {'Timestamp': '2024-07-10T20:27:07.251Z', 'Email Address': 'tuhinmaj1998@gmail.com', 'NAME': 'Tuhin M', 'SALUTE': 'Mr', 'Tell us about the Experience': 'Very Good', 'Rate the Session': '5'},
#             # {'Timestamp': '2024-07-10T20:28:53.557Z', 'Email Address': 'prathamdrift16@gmail.com', 'NAME': 'Pratham Majumder', 'SALUTE': 'Dr', 'Tell us about the Experience': 'Excellent', 'Rate the Session': '5'},
#             {'Timestamp': '2024-07-14T09:57:52.008Z', 'Email Address': 'test123@gmail.com', 'NAME': 'test1 Harrington', 'SALUTE': 'Mr', 'Tell us about the Experience': 'good', 'Rate the Session': '3'},
#             {'Timestamp': '2024-07-13T17:30:00.000Z', 'Email Address': 'sampleperson1@sample.com', 'NAME': 'sample patel', 'SALUTE': 'Ms', 'Tell us about the Experience': 'Admiriable', 'Rate the Session': '4'}
#     ],
#     column_mapping = [
#              {'templateColumns': 'NAME', 'gsheetColumns': 'NAME', 'hardcode_value_ifapplicable': ''},
#              {'templateColumns': 'SALUTE', 'gsheetColumns': 'SALUTE', 'hardcode_value_ifapplicable': ''},
#              {'templateColumns': 'COURSENAME', 'gsheetColumns': 'others', 'hardcode_value_ifapplicable': 'Course1'},
#              {'templateColumns': 'DATE', 'gsheetColumns': 'others', 'hardcode_value_ifapplicable': '22July,2024'}
#     ])
# )

# print(templateDataFit({'template_id': '1evorSKDJmzKnVmQyQm3gquhZf-y2Tdfl',
#                   'sample_data': [{'templateColumns': 'SALUTE', 'sampleValue': 'Mr'},
#                                   {'templateColumns': 'ADDRESS', 'sampleValue': '123, Kanakpura'},
#                                   {'templateColumns': 'COURSENAME', 'sampleValue': 'Coursera'},
#                                   {'templateColumns': 'DATE', 'sampleValue': '22-27th July, 2024'},
#                                   {'templateColumns': 'NAME', 'sampleValue': 'Tuhin Majumder'}]}, 1))


# def CreatePDFsInGdrive_1(url, is_sample, template_file_id, spreadsheet_url, sheetname, gsheet_columnwise_data,
#                        column_mapping):
#     gsheet_columnwise_data_corrected = pd.DataFrame()
#     df = pd.DataFrame(gsheet_columnwise_data)
#     column_mapping_df = pd.DataFrame(column_mapping)
#
#     # for index, row in df.iterrows():
#     #     print(row)
#         # gsheet_columnwise_data_corrected[str(column_mapping_df[index])] = row
#
#
#
#     return df.to_string(index=False)


# #
# print(CreatePDFsInGdrive(
#     url='https://script.google.com/macros/s/AKfycbw0csSAN8OoZnkB-J1KUFY_50t4oXwh9df0B1o2JLsBWpH40mN1ytzuXCh9ijGXQ27-SQ/exec',
#     is_sample=1,
#     template_file_id='1NLcYVsC6JQP6uG4f-MrpzVPdnKNwpPaCq_C5WqruC78',
#     spreadsheet_url='https://docs.google.com/spreadsheets/d/1xIw-odZu7wUKK6bEtWiCGXGO7MrPSYHQE-udnbJIgs4/edit',
#     sheetname='nw_fq',
#     gsheet_columnwise_data=[
#         {"COURSENAME": "Certificate Generation 101", "SALUTE": "Mr", "NAME": "T Majumder", "DATE": "3@gmail.com"}],
#     column_mapping=[{"templateColumns": "COURSENAME", "gsheetColumns": "others",
#                      "hardcode_value_ifapplicable": "Certificate Generation 101"},
#                     {"templateColumns": "SALUTE", "gsheetColumns": "Preferred Salutation",
#                      "hardcode_value_ifapplicable": ""},
#                     {"templateColumns": "NAME", "gsheetColumns": "NAME", "hardcode_value_ifapplicable": ""},
#                     {"templateColumns": "DATE", "gsheetColumns": "Email Address", "hardcode_value_ifapplicable": ""}])
# )
