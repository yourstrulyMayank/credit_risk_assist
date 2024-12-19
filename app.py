from flask import Flask, render_template, request, redirect, url_for
import os
import threading
import time

app = Flask(__name__)
UPLOAD_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Mock populate_database function
def populate_database():
    time.sleep(5)  # Simulating time for vectorization

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Call populate_database in a background thread
            threading.Thread(target=run_populate_database).start()
            return render_template('loading.html')  # Show loading screen
    return redirect(url_for('index'))

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        question = request.form.get('question')
        # Process the question using the database (mocked here)
        response = f"You asked: {question}. (Mocked response)"
        return render_template('ask.html', response=response)
    return render_template('ask.html', response=None)

@app.route('/query', methods=['GET'])
def query():
    return redirect(url_for('ask'))  # Directly go to question-answering page

def run_populate_database():
    populate_database()
    # After processing, redirect to the question-answering page
    print("Finished processing")  # Use logs or signal completion as needed

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
