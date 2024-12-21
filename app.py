import os
import subprocess
import threading
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify
from query_data import query_rag
import populate_database
import clear_database

app = Flask(__name__)
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
processing_status = {"complete": False}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Run populate_database.py in the background
        threading.Thread(target=run_populate_database).start()
        return render_template('loading.html')  # Show a loading page
    return redirect(url_for('index'))


@app.route('/ask', methods=['GET', 'POST'])
def ask():
    document_titles = load_file_titles()
    if request.method == 'POST':
        question = request.form.get('question')
        if question:
            # Process question using query_rag
            response = query_rag(question)  # Replace with actual RAG logic
            return render_template('ask.html', response=response, document_titles=document_titles)
    return render_template('ask.html', document_titles=document_titles)


@app.route('/batch_ask', methods=['POST'])
def batch_ask():
    data = request.json
    questions = data.get('questions', [])
    answers = []

    # Process each question and append the response
    for question in questions:
        answer = query_rag(question)  # Replace with actual RAG logic
        answers.append(answer)

    return jsonify({"answers": answers})

@app.route('/query', methods=['GET'])
def query():
    return redirect(url_for('ask'))  # Directly go to question-answering page

@app.route('/clear', methods=['GET','POST'])
def clear():
    return clear_database.clear_database()

def run_populate_database():
    global processing_status
    processing_status["complete"] = False
    try:
        populate_database.populate_database()
    finally:
        processing_status["complete"] = True

@app.route('/check_status', methods=['GET'])
def check_status():
    return jsonify({"complete": processing_status["complete"]})

def load_file_titles():
    titles = []
    try:
        with open("utils/files.txt", "r") as file:
            for line in file:
                print(line)
                key, _ = line.strip().split(":")
                titles.append(key)
    except FileNotFoundError:
        pass
    return titles

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
