import os
import chromadb
from flask import Flask, request
from src.workers.pdf_converter import convert_pdf

app = Flask(__name__)

CVS_DIR = 'cvs'
CHROMA_DIR = 'chroma.db'

chroma_client = chromadb.PersistentClient(CHROMA_DIR)
collection = chroma_client.get_or_create_collection(
    name="my_collection",
    metadata={
        "hnsw:space": "cosine",
        "hnsw:search_ef": 100
    })

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'

@app.route('/candidates/top', methods=['GET'])
def get_top_candidates():
    job_description = request.get_json().get('job_description')
    top = request.get_json().get('top')

    # Force a fresh client to ensure up-to-date data
    fresh_chroma_client = chromadb.PersistentClient(CHROMA_DIR)
    fresh_collection = fresh_chroma_client.get_collection("my_collection")
    
    results = fresh_collection.query(
        query_texts=[job_description],
        n_results=top
    )

    return results

@app.route('/cv/upload', methods=['POST'])
def upload_cv():
    file = request.files['file']
    file.save(os.path.join(CVS_DIR, file.filename))

    convert_pdf.delay(file.filename)

    return 'File uploaded successfully!'

if __name__ == '__main__':
    app.run(debug=False)