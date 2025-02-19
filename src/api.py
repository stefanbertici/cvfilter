import os
import chromadb
from flask import Flask, Response, request
from chatwrap.client import LlmClient
from pdfminer.high_level import extract_text
import requests

app = Flask(__name__)

CVS_DIR = 'cvs'
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="my_collection")

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'

@app.route('/candidates/top', methods=['GET'])
def get_top_candidates():
    job_description = request.get_json().get('job_description')
    top = request.get_json().get('top')

    results = collection.query(
        query_texts=[job_description],
        n_results=top
    )

    return results

@app.route('/cv/upload', methods=['POST'])
def upload_cv():
    file = request.files['file']
    file.save(os.path.join(CVS_DIR, file.filename))

    return 'File uploaded successfully!'

@app.route('/cv/process', methods=['POST'])
def process_cv():
    file_name = request.get_json().get('file_name')

    if not os.path.exists(os.path.join(CVS_DIR, file_name)):
        return Response('File not found', status=404)
    
    text = extract_text(os.path.join(CVS_DIR, file_name))
    system_content = 'You are a helpful HR assistant. Your answers are concise.'
    user_content = f'Extract the name of the candidate and give me a list of their technical skills from the following text: {text}'

    llmClient = LlmClient('http://127.0.0.1:1234', 'llama-3.2-3b-instruct')
    skills = llmClient.generate(system_content, user_content, 'llama-3.2-3b-instruct', 0.7, -1, False, None)
    count = collection.count()

    collection.upsert(
        documents=[
            skills
        ],
        ids=["id" + str(count + 1)]
    )

    return skills

def __load_initial_files_to_chroma():
    print('~~~ Start loading files to chroma')
    files = __get_initial_file_names()
    
    for file in files:
        print(f'~~~ Processing file: {file}')
        __process_file(file, files.index(file) + 1)
    
    print('~~~ Finished loading files to chroma')

def __get_initial_file_names():
    print('~~~ Getting initial file names')
    
    if not os.path.exists(CVS_DIR):
        print('~~~ Creating CVS directory')
        os.makedirs(CVS_DIR)
    
    return os.listdir(CVS_DIR)

def __process_file(file, index):
    file_name = file
    
    text = extract_text(os.path.join(CVS_DIR, file_name))
    system_content = 'You are a helpful HR assistant. Your answers are concise.'
    user_content = f'Extract the name of the candidate and give me a list of their technical skills from the following text: {text}'

    llmClient = LlmClient('http://127.0.0.1:1234', 'llama-3.2-3b-instruct')
    skills = llmClient.generate(system_content, user_content, 'llama-3.2-3b-instruct', 0.7, -1, False, None)

    collection.upsert(
        documents=[
            skills
        ],
        ids=["id" + str(index)]
    )

    return skills

if __name__ == '__main__':
    __load_initial_files_to_chroma()
    app.run(debug=True)