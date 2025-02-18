import os
from flask import Flask, Response, request
from chatwrap.client import LlmClient
from pdfminer.high_level import extract_text

app = Flask(__name__)
CVS_DIR = 'cvs'

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'

@app.route('/extract', methods=['POST'])
def extract_skills():
    cv = request.get_json().get('content')
    job = 'Java developer'
    prompt = f"Extract the relevant skills for a '{job}' position from the following text '{cv}'"
    llmClient = LlmClient('http://127.0.0.1:1234', 'llama-3.2-3b-instruct')
        
    skills = llmClient.generate(prompt=prompt, model='llama-3.2-3b-instruct', temperature=0.7, max_tokens=250, stream=False)

    return skills

@app.route('/cv/upload', methods=['POST'])
def upload_cv():
    file = request.files['file']
    file.save(os.path.join(CVS_DIR, file.filename))

    return 'File uploaded successfully!'

@app.route('/cv/process', methods=['POST'])
def process_cv():
    file_name = request.get_json().get('file_name')
    job_title = request.get_json().get('job_title')

    if not os.path.exists(os.path.join(CVS_DIR, file_name)):
        return Response('File not found', status=404)
    
    text = extract_text(os.path.join(CVS_DIR, file_name))
    # text = 'My name is Stefan Bertici and in the past I worked with python and Java. With Java I have used spring boot and hibernate. I have also worked with databases like MySQL and PostgreSQL. I have experience with RESTful APIs and I have worked with Git.'
    system_content = 'You are a helpful HR assistant. Your answers are concise.'
    user_content = f'Extract the name of the candidate and give me a list of their relevant skills for a {job_title} position from the following text: {text}'

    llmClient = LlmClient('http://127.0.0.1:1234', 'llama-3.2-3b-instruct')
    skills = llmClient.generate(system_content, user_content, 'llama-3.2-3b-instruct', 0.7, -1, False, None)

    return skills

if __name__ == '__main__':
    app.run(debug=True)