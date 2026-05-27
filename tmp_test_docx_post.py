import io
from docx import Document
import requests

doc = Document()
doc.add_paragraph('Hello from test')
buf = io.BytesIO()
doc.save(buf)
buf.seek(0)
files={'file':('test.docx', buf, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
try:
    r = requests.post('http://localhost:5000/convertDocxToPdf', files=files, timeout=10)
    print('STATUS', r.status_code)
    print('CT', r.headers.get('Content-Type'))
    print('Disposition', r.headers.get('Content-Disposition'))
    print('LEN', len(r.content))
    try:
        print(r.content[:200])
    except Exception:
        pass
    if r.status_code==200 and r.headers.get('Content-Type','').startswith('application/pdf'):
        with open('out_test_converted.pdf','wb') as f:
            f.write(r.content)
        print('Saved out_test_converted.pdf')
    else:
        print(r.text)
except Exception as e:
    print('ERROR', e)
