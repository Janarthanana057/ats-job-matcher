from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from matcher import match_resume
from datetime import datetime
import PyPDF2
import io

app = Flask(__name__)

# =========================
# DATABASE SETUP
# =========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =========================
# DATABASE MODEL
# =========================
class ScanHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False)
    matched_count = db.Column(db.Integer)
    missing_count = db.Column(db.Integer)
    matched_keywords = db.Column(db.Text)
    missing_keywords = db.Column(db.Text)
    format_score = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    target_role = db.Column(db.String(100))

    def to_dict(self):
        return {
            'id': self.id,
            'score': self.score,
            'matched_count': self.matched_count,
            'missing_count': self.missing_count,
            'matched_keywords': self.matched_keywords.split(',') if self.matched_keywords else [],
            'missing_keywords': self.missing_keywords.split(',') if self.missing_keywords else [],
            'format_score': self.format_score,
            'target_role': self.target_role,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

# =========================
# CREATE DB
# =========================
with app.app_context():
    db.create_all()

# =========================
# HELPER FUNCTION
# =========================
def extract_pdf_text(pdf_file):
    """
    Extract text safely from uploaded PDF
    """
    text = ""

    try:
        pdf_file.seek(0)
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file.read()))

        for page in pdf_reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + " "

    except Exception as e:
        raise Exception(f"PDF Extraction Failed: {str(e)}")

    return text.strip()

# =========================
# HOME PAGE
# =========================
@app.route('/')
def index():
    return render_template('index.html')

# =========================
# ANALYZE ATS
# =========================
@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        resume_text = ""
        jd_text = request.form.get('jd', '').strip()
        target_role = request.form.get("target_role", "").strip()

        # =========================
        # PDF UPLOAD
        # =========================
        if 'resume_pdf' in request.files:
            pdf_file = request.files['resume_pdf']

            if pdf_file and pdf_file.filename:
                resume_text = extract_pdf_text(pdf_file)

        # =========================
        # MANUAL RESUME OVERRIDE
        # =========================
        manual_resume = request.form.get('resume', '').strip()

        if manual_resume:
            resume_text = manual_resume

        # =========================
        # VALIDATION
        # =========================
        if not resume_text or not jd_text:
            return jsonify({
                'error': 'Please provide both resume and job description'
            }), 400

        # Clean text
        resume_text = resume_text.strip()
        jd_text = jd_text.strip()

        # Debug
        print("Resume Preview:", resume_text[:500])
        print("JD Preview:", jd_text[:500])

        # =========================
        # NLP MATCHING
        # =========================
        result = match_resume(resume_text, jd_text)

        # =========================
        # SAFE FALLBACKS
        # =========================
        score = result.get('score', 0)
        matched = result.get('matched', [])
        missing = result.get('missing', [])
        tech_score = result.get('tech_score', 0)
        tfidf_score = result.get('tfidf_score', 0)
        format_score = result.get('format_score', 0)
        trust_score = result.get('trust_score', 0)
        suggestions = result.get('suggestions', [])

        # Backup suggestions if matcher doesn't return them
        if not suggestions:
            suggestions = []

            for keyword in missing[:5]:
                suggestions.append(f"Add '{keyword}' to skills or projects")

        # =========================
        # SAVE HISTORY
        # =========================
        scan = ScanHistory(
            score=score,
            matched_count=len(matched),
            missing_count=len(missing),
            matched_keywords=",".join(matched),
            missing_keywords=",".join(missing),
            format_score=format_score,
            target_role=target_role
        )

        db.session.add(scan)
        db.session.commit()

        # =========================
        # RESPONSE
        # =========================
        return jsonify({
            'score': score,
            'matched': matched,
            'missing': missing,
            'tech_score': tech_score,
            'tfidf_score': tfidf_score,
            'format_score': format_score,
            'trust_score': trust_score,
            'suggestions': suggestions,
            'scan_id': scan.id
        }), 200

    except Exception as e:
        print("Analyze Error:", str(e))

        return jsonify({
            'error': str(e)
        }), 500

# =========================
# GET HISTORY
# =========================
@app.route('/api/history', methods=['GET'])
def get_history():
    scans = ScanHistory.query.order_by(
        ScanHistory.timestamp.desc()
    ).limit(10).all()

    return jsonify({
        'success': True,
        'count': len(scans),
        'data': [scan.to_dict() for scan in scans]
    }), 200

# =========================
# GET SPECIFIC SCORE
# =========================
@app.route('/api/score/<int:scan_id>', methods=['GET'])
def get_score(scan_id):
    scan = ScanHistory.query.get(scan_id)

    if not scan:
        return jsonify({
            'success': False,
            'error': f'Scan ID {scan_id} not found'
        }), 404

    return jsonify({
        'success': True,
        'data': scan.to_dict()
    }), 200

# =========================
# DELETE HISTORY
# =========================
@app.route('/api/history', methods=['DELETE'])
def delete_history():
    ScanHistory.query.delete()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'All scan history cleared'
    }), 200

# =========================
# STATS
# =========================
@app.route('/api/stats', methods=['GET'])
def get_stats():
    total_scans = ScanHistory.query.count()

    if total_scans == 0:
        return jsonify({
            'success': True,
            'data': {
                'total_scans': 0,
                'average_score': 0,
                'highest_score': 0,
                'lowest_score': 0
            }
        }), 200

    scores = [s.score for s in ScanHistory.query.all()]

    return jsonify({
        'success': True,
        'data': {
            'total_scans': total_scans,
            'average_score': round(sum(scores) / len(scores), 2),
            'highest_score': max(scores),
            'lowest_score': min(scores)
        }
    }), 200
# =========================
# CLEAR SCAN HISTORY
# =========================
@app.route("/api/clear-history", methods=["DELETE"])
def clear_history():
    try:
        ScanHistory.query.delete()
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Scan history cleared successfully"
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500




# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=False)
    