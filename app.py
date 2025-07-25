# app.py

import os
import re
from flask import Flask, request, jsonify, render_template
import pdfplumber
import docx

# Initialize the Flask application
app = Flask(__name__, template_folder='templates', static_folder='static')

# Define keywords for different sections
# You can expand this list extensively
SKILLS_KEYWORDS = [
    'python', 'java', 'c++', 'javascript', 'html', 'css', 'react', 'angular', 'vue', 'node.js',
    'flask', 'django', 'sql', 'nosql', 'mongodb', 'postgresql', 'aws', 'azure', 'docker', 'kubernetes',
    'git', 'jira', 'agile', 'scrum', 'machine learning', 'data analysis', 'artificial intelligence'
]

# --- Helper Functions for Analysis ---

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    doc = docx.Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def analyze_resume(text):
    """Analyzes the resume text and returns a score and suggestions."""
    score = 100
    suggestions = []
    
    # 1. Check for Contact Information (Email and Phone)
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_regex = r'(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    
    if not re.search(email_regex, text):
        score -= 15
        suggestions.append("CRITICAL: No email address found. Add a professional email address.")
    
    if not re.search(phone_regex, text):
        score -= 15
        suggestions.append("CRITICAL: No phone number found. Add your contact number.")

    # 2. Check for Essential Sections
    required_sections = ['experience', 'education', 'skills']
    text_lower = text.lower()
    for section in required_sections:
        if section not in text_lower:
            score -= 10
            suggestions.append(f"Missing Section: Add a clear '{section.capitalize()}' section for better ATS parsing.")

    # 3. Check for Keywords (Skills)
    found_skills = [skill for skill in SKILLS_KEYWORDS if re.search(r'\b' + re.escape(skill) + r'\b', text_lower)]
    if len(found_skills) < 5:
        score -= 10
        suggestions.append("Low Skill Count: Your resume has few relevant skills. Add more job-specific skills.")
    else:
        suggestions.append(f"Good Skills Match: Found {len(found_skills)} relevant skills.")

    # 4. Check for Action Verbs (a simple check)
    action_verbs = ['developed', 'led', 'managed', 'created', 'implemented', 'designed', 'achieved']
    if not any(verb in text_lower for verb in action_verbs):
        score -= 5
        suggestions.append("Use Action Verbs: Start bullet points with action verbs like 'Managed', 'Developed', or 'Led' to describe your accomplishments.")

    # 5. Check for formatting issues (e.g., length)
    word_count = len(text.split())
    if word_count > 800:
        score -= 5
        suggestions.append("Conciseness: Your resume is too long ({word_count} words). Aim for 400-600 words for most roles.")
    elif word_count < 300:
        score -= 5
        suggestions.append("Expand Content: Your resume is very short ({word_count} words). Consider adding more detail to your experience.")

    # Ensure score is not negative
    score = max(0, score)
    
    return {'score': score, 'suggestions': suggestions}


# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handles the file upload and analysis."""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # Save the file temporarily
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        text = ""
        try:
            # Extract text based on file type
            if file.filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            elif file.filename.lower().endswith('.docx'):
                text = extract_text_from_docx(file_path)
            else:
                return jsonify({'error': 'Unsupported file type. Please upload a PDF or DOCX.'}), 400
            
            # Analyze the extracted text
            analysis_result = analyze_resume(text)

            # Clean up the uploaded file
            os.remove(file_path)

            return jsonify(analysis_result)

        except Exception as e:
            # Clean up in case of error
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({'error': f'An error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)