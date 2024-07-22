import requests
import base64

# Function to upload any file to Google Apps Script web app
def upload_file_to_apps_script(file_path, content_type, script_url):
    with open(file_path, 'rb') as f:
        file_content = f.read()

    # Encode file content as base64
    encoded_content = base64.b64encode(file_content).decode('utf-8')

    # Prepare POST request data
    data = {
        'contentType': content_type,
        'contents': encoded_content
    }

    # Send POST request to Google Apps Script web app
    response = requests.post(script_url, json=data)

    # Print response data
    if response.status_code == 200:
        print('File uploaded successfully.')
        print('File ID:', response.text)
    else:
        print('Error uploading file:', response.text)

# Replace with your Google Apps Script web app URL
script_url = 'https://script.google.com/macros/s/AKfycbyrN9rt1KzA4hYe60QnkaTqG094qmqabU6HDm3fN0YepFj1gM04dUk6C1qkKyCBHgDp/exec'

# Replace with the path to your file
file_path = 'static/sample/pdf/output_JGI-2024-1721431771971117000.pdf'  # Example: 'path/to/your/file.pdf'

# Replace with the content type of your file
content_type = 'application/pdf'  # Example: 'image/jpeg', 'image/png', 'application/pdf', etc.

# Call the function to upload the file to Google Apps Script web app
upload_file_to_apps_script(file_path, content_type, script_url)