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
DATA_PATH = "data"
NEW_DATA_PATH = "data\\new"
AVAILABLE_FILES_PATH = "utils\\files.txt"

def main():
    return populate_database()

def populate_database(db):  

    # Create (or update) the data store.
    documents = load_documents()        
    
    chunks = split_documents(documents)    
    print("Adding to Database")
    add_to_chroma(chunks, db)
    print("Added to Database")
    add_file_to_list(db, documents[-1].metadata['source'].split('\\')[-1], len(chunks))    
    print("Added file to list")
    for filename in os.listdir(NEW_DATA_PATH):
        src = os.path.join(NEW_DATA_PATH, filename)
        dest = os.path.join(DATA_PATH, filename)
        shutil.move(src, dest)
    print(f"All files moved from {NEW_DATA_PATH} to {DATA_PATH}")


def load_documents():
    document_loader = PyPDFDirectoryLoader(NEW_DATA_PATH)
    return document_loader.load()


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " "],  # Preserve table rows
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document], db):
    # Load the existing database.
    # db = Chroma(
    #     persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    # )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        # db.persist()
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def add_file_to_list(db, file_name, new_chunk_count):
    print("Here in adding file to list")
    """
    Add the file name and chunk count difference to the available files list.

    :param db: Chroma database instance.
    :param file_name: Name of the file being processed.
    :param new_chunk_count: Number of chunks generated for the file.
    """
    # Fetch existing chunks for the file from the database.
    existing_items = db.get(include=["metadatas", "documents"])  # Use "metadatas"
    # print(existing_items)
    existing_chunks = [
    doc for doc, metadata in zip(existing_items["documents"], existing_items["metadatas"]) 
    if metadata["source"] == file_name]


    # Count existing chunks for the given file.
    existing_chunk_count = len(existing_chunks)
    chunk_difference = new_chunk_count - existing_chunk_count

    # Append the new file name and chunk count to the file list.
    with open(AVAILABLE_FILES_PATH, "a") as file:
        file.write(f"{file_name}:{chunk_difference}\n")

    print(f"✅ Updated file list for {file_name} with {chunk_difference} new chunks.")

if __name__ == "__main__":
    main()
