import os
import uuid
from celery import Celery
import chromadb
from flask import Response
from chatwrap.client import LlmClient
from pdfminer.high_level import extract_text

CELERY_BROKER_URL = f"sqlalchemy+sqlite:///db.sqlite3"
CVS_DIR = 'cvs'

pdf_converter = Celery('tasks', broker=CELERY_BROKER_URL)
chroma_client = chromadb.PersistentClient(path='chroma.db')
collection = chroma_client.get_or_create_collection(name="my_collection")

@pdf_converter.task
def convert_pdf(file_name):
    if not os.path.exists(os.path.join(CVS_DIR, file_name)):
        return Response('File not found', status=404)
    
    text = extract_text(os.path.join(CVS_DIR, file_name))
    system_content = 'You are a helpful HR assistant. Your answers are concise.'
    user_content = f'Extract the name of the candidate and give me a list of their technical skills from the following text: {text}'

    llmClient = LlmClient('http://127.0.0.1:1234', 'llama-3.2-3b-instruct')
    skills = llmClient.generate(system_content, user_content, 'llama-3.2-3b-instruct', 0.7, -1, False, None)

    collection.upsert(
        documents=[
            skills
        ],
        metadatas=[
            {'file_name': file_name}
        ],
        ids=[str(uuid.uuid4())]
    )

    print('PDF converted successfully!')