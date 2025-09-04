from label_studio_sdk.client import LabelStudio
import os
from label_studio_sdk import Client

import dotenv
dotenv.load_dotenv(dotenv_path=".env")

LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8081')
LABEL_STUDIO_API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6ODA2Mzk5NjI1MiwiaWF0IjoxNzU2Nzk2MjUyLCJqdGkiOiIxYjdiZGU1MThhNjE0ZDMxODVlMTA0NjA1NDBhMGZjMyIsInVzZXJfaWQiOiIxIn0.rzbOnXChxWYZDONPmaEvmZpFpPDzcnvkfjOxYjgMUrg'
#os.getenv('LABEL_STUDIO_API_KEY')
ls = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)


tasks = ls.tasks.list(project=1)
for task in tasks:
    print("task ", task)

ls.tasks.create(project=1, data={"question": "What about 700euros?", "answer": "It works too"})
