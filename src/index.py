import chromadb
from argparse import ArgumentParser
from pathlib import Path
from src.workers.pdf_converter import convert_pdf

CVS_DIR = 'cvs'
CHROMA_DIR = 'chroma.db'

chroma_client = chromadb.PersistentClient(CHROMA_DIR)
collection = chroma_client.get_or_create_collection(
        name="my_collection",
        metadata={
            "hnsw:space": "cosine",
            "hnsw:search_ef": 100
        })

def main(params):
    folder = Path(CVS_DIR) if params.path in [None, ''] else Path(params.path)
    file_names = [file.name for file in folder.iterdir() if file.is_file()]
    ids = collection.get()['ids']

    if ids:
        print(f'Clearing chroma db of {ids}')
        collection.delete(ids)
    else:
        print('Chroma db already empty. Proceeding without clearing')

    for file_name in file_names:
        if file_name.endswith('.pdf'):
            print(f'Queuing CV indexing for {file_name}')
            convert_pdf.delay(file_name)

    print('Finished queuing CVs')    

if __name__ == '__main__':
    args = ArgumentParser('Index')
    args.add_argument('--path', help='Path to CVs')
    params = args.parse_args()
    main(params);