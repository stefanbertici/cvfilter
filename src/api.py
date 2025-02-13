from flask import Flask
from chatwrap import LlmClient

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'

@app.route('/cv', methods=['POST'])
def upload_cv():
    cv = "Stefan Bertici, I know Python, Java 3 years experience"
    llmClient = LlmClient('http://127.0.0.1:1234')

    # extract skills from the cv with LLM - create appropriate prompt
    # look over chromadb and install it
    # get used to flask 

    return 'Upload cv works!'

@app.route('/candidates/top', methods=['GET'])
def get_top_candidates():
    return 'Top candidates works!'

if __name__ == '__main__':
    app.run(debug=True)