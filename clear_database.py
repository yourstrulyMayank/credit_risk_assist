import argparse
import os
import shutil
# from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
# from langchain.vectorstores.chroma import Chroma
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFDirectoryLoader


CHROMA_PATH = "chroma"
AVAILABLE_FILES_PATH = "utils\\files.txt"

def main():
    print("✨ Clearing Database Main")
    return clear_database()

def clear_database():
    print("✨ Clearing Database")
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)
    with open(AVAILABLE_FILES_PATH, "w") as file:
        file.write("")
    return True

if __name__ == "__main__":
    main()
