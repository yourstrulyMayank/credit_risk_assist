import os
import threading
from flask import Flask, render_template, request, redirect, url_for, jsonify
import populate_database
import clear_database
from query_data import query_rag

app = Flask(__name__)
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

processing_status_upload = {"complete": False}
processing_status_fetch = {"complete": False}

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
        return render_template('loading.html')  # Show loading page while population happens


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


@app.route('/clear_database', methods=['POST'])
def clear_database_route():
    try:
        clear_database.clear_database()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def run_populate_database():
    global processing_status_upload
    processing_status_upload["complete"] = False
    try:
        populate_database.populate_database()
    finally:
        processing_status_upload["complete"] = True
        # After database population, redirect to fetching results
        threading.Thread(target=redirect_to_fetching_results).start()


@app.route('/check_status_upload', methods=['GET'])
def check_status_upload():
    return jsonify({"complete": processing_status_upload["complete"]})


@app.route('/check_status_fetch', methods=['GET'])
def check_status_fetch():
    return jsonify({"complete": processing_status_fetch["complete"]})


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


@app.route('/fetching_results', methods=['GET'])
def fetching_results():
    """
    Render fetching_results.html and start querying the database for predefined questions.
    """
    return render_template('fetching_results.html')


prepopulated_questions = {
    "Net Sales": "What is the Net Sales?",
    "Gross Profit": "What is the Gross Profit?",
    "Debt/Equity Ratio": "What is the Debt/Equity Ratio?",
    "Company Name": "What is the name of the company mentioned in the document?"
}

fetched_results = {}  # Store results globally for simplicity


def query_vector_db(question):
    answer = query_rag(question)  
    return answer


def redirect_to_fetching_results():
    # Wait until the database population is complete
    while not processing_status_upload["complete"]:
        pass

    # Once population is complete, move to querying the database
    processing_status_fetch["complete"] = False
    threading.Thread(target=run_query_database).start()


def run_query_database():
    """
    Query the database for prepopulated questions and update the fetched_results.
    """
    global fetched_results
    global processing_status_fetch

    # Simulate querying the database
    results = {}
    for key, question in prepopulated_questions.items():
        results[key] = query_vector_db(question)

    fetched_results.update(results)

    # Mark fetching as complete and redirect to analyze page
    processing_status_fetch["complete"] = True
    with app.app_context():
        return render_template('analyze.html', data=fetched_results)


@app.route('/analyze', methods=['GET'])
def analyze():
    """
    Render analyze.html with fetched results.
    """
    return render_template('analyze.html', data=fetched_results)


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
