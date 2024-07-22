
import requests


def fetch_post_data(url, submit_response):
    # url = 'https://script.google.com/macros/s/your-script-id/exec'  # Replace with your published script URL
    try:
        print(submit_response)
        response = requests.post(url, data=submit_response)  # {"key":"123", 'password':'123'})
        data = response.json()
        return {'code': response.status_code, 'msg': data}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return {'code': response.status_code, 'data': []}
#
# def identify_columns(post_response_data):
#     import pandas as pd
#     try:
#         records = pd.DataFrame(post_response)#(post_response['msg']['data'])
#         print(records.columns)
#         return records.columns#.to_list()
#     except Exception as e:
#         print(str(e))
#         return []
#
# import pandas as pd
# url = 'https://script.google.com/macros/s/AKfycby3X7uvFqiU3NN2FnjhtxryNGFPU__wqXxBTGOtr-cQwk-z3y8ZLSkJ5Abku8-A6Ycg/exec'
# submit_response = {
#     'spreadsheet_url': 'https://docs.google.com/spreadsheets/d/1_EqBltrMWdhB6pWDTkoPzFwcZL1C1RT9HJEbvHHUHCY/edit?resourcekey=&gid=1267774142#gid=1267774142',
#     'sheetname': 'Sample_Form1',
#     'key': '123',
#     'password': '123'
# }
# post_response = fetch_post_data(url, submit_response)
# records = pd.DataFrame(post_response['msg']['data'])
# print(records)
# print(records.columns)
# records = pd.DataFrame(post_response['msg']['data'])
# print(records.to_string(index=False))
