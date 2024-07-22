from docxtpl import DocxTemplate
import subprocess
import time
import pandas as pd

"""
Directory tree

Static
|----docx-template
    |---------templatedoc.docx
|----output
|   |--------docx
|   |--------pdf
|----list.csv
"""
static_dir = '/Users/tuhinmajumder/pythonProject/mycertificate/static'
template_file = f'{static_dir}/docx-template/templatedoc.docx'
list_csv = f'{static_dir}/sample_feedback.csv'

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

doc = DocxTemplate(template_file)
df = pd.read_csv(list_csv)

for index,row in df.iterrows():
    context = {
        'SALUTE': row['SALUTE'],
        'NAME': row['NAME'],
        'COURSENAME': 'Generative AI Models & Applications of Machine Learning',
        'DATE': '22nd - 27th July, 2024',
        'RNUM': 'JGI'+str(hash(str(row['Timestamp']))) #str(hash(str(row['ROLL'])))#'JGI123456'
    }
    doc.render(context)

    docx_file = f'{static_dir}/output/docx/output_{str(row["NAME"])}.docx'
    pdf_file = f'{static_dir}/output/pdf/output_{str(row["NAME"])}.pdf'

    doc.save(docx_file)
    time.sleep(3)

    # docx_file = "/Users/tuhinmajumder/pythonProject/mycertificate/Static/output/docx/output.docx"
    # pdf_file = "/Users/tuhinmajumder/pythonProject/mycertificate/Static/output/pdf/output.pdf"

    convert_docx_to_pdf_with_pages(docx_file, pdf_file)
