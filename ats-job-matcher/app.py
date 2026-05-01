from flask import Flask, render_template, request, jsonify
from matcher import match_resume

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    resume_text = data.get('resume', '')
    jd_text = data.get('jd', '')

    if not resume_text or not jd_text:
        return jsonify({'error': 'Please provide both resume and job description'}), 400

    result = match_resume(resume_text, jd_text)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)