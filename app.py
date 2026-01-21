from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from config import Config
from data_manager import check_user, create_user, get_student_progress, update_progress, load_json, save_json
from ai_engine import AIEngine
import os

app = Flask(__name__)
app.config.from_object(Config)
app.jinja_env.add_extension('jinja2.ext.do')

ai = AIEngine()

# --- Helpers ---
def get_syllabus():
    return load_json('syllabus.json')

# --- Routes ---

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/auth/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = check_user(username, password)
    if user:
        user['info_username'] = username 
        session['user'] = user
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Invalid Credentials.")

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        roll_number = request.form.get('roll_number')
        name = request.form.get('name')
        email = request.form.get('email')
        
        if create_user(username, password, roll_number, name, email):
            return redirect(url_for('index'))
        else:
            return render_template('register.html', error="Username already exists.")
            
    return render_template('register.html')

@app.route('/auth/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    
    user = session['user']
    progress = get_student_progress(user_id(user))
    syllabus = get_syllabus()
    
    # Calculate stats
    total_topics = 0
    for subj in syllabus.get('subjects', []):
        for unit in subj.get('units', []):
            total_topics += len(unit.get('topics', []))
        
    completed_count = len(progress.get('topics_completed', []))
    percent = int((completed_count / total_topics * 100)) if total_topics > 0 else 0
    
    return render_template('dashboard.html', 
                           user=user, 
                           progress=progress, 
                           percent=percent,
                           subjects=syllabus.get('subjects', []))

@app.route('/learn/<topic_id>')
def learn(topic_id):
    if 'user' not in session: return redirect(url_for('index'))
    
    # Find topic name from syllabus (inefficient search but fine for demo)
    topic_name = "Unknown Topic"
    syllabus = get_syllabus()
    for subj in syllabus.get('subjects', []):
        for unit in subj.get('units', []):
            for t in unit.get('topics', []):
                if t['id'] == topic_id:
                    topic_name = t['name']
                    break
            if topic_name != "Unknown Topic": break
        if topic_name != "Unknown Topic": break
    
    # Get AIGEN content
    content = ai.generate_explanation(topic_name)
    
    return render_template('learning.html', topic_id=topic_id, topic_name=topic_name, content=content)

@app.route('/mark_complete/<topic_id>', methods=['POST'])
def mark_complete(topic_id):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    update_progress(user_id(session['user']), topic_id, 'complete', True)
    return jsonify({"status": "success", "message": "Topic marked as complete"})

@app.route('/settings/update_difficulty', methods=['POST'])
def update_difficulty():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    session['difficulty'] = data.get('difficulty', 'Moderate')
    return jsonify({"status": "success"})

@app.route('/quiz/<topic_id>')
def quiz(topic_id):
    if 'user' not in session: return redirect(url_for('index'))
    
    # Determine difficulty from session or credential
    difficulty = session.get('difficulty', 'Moderate') 
    
    questions = ai.generate_quiz(topic_id, difficulty)
    return render_template('quiz.html', topic_id=topic_id, questions=questions)

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    topic_id = data.get('topic_id')
    score = data.get('score') # In a real app, calculate on backend
    total = data.get('total')
    
    update_progress(user_id(session['user']), topic_id, 'score', {
        "topic_id": topic_id,
        "score": score, 
        "total": total, 
        "timestamp": "Now"
    })
    
    return jsonify({"status": "success", "redirect": url_for('analysis')})

@app.route('/analysis')
def analysis():
    if 'user' not in session: return redirect(url_for('index'))
    
    progress = get_student_progress(user_id(session['user']))
    scores_map = progress.get('quiz_scores', {})
    scores = []
    for tid, data in scores_map.items():
        d = data.copy()
        d['topic_id'] = tid
        scores.append(d)
    
    analysis_result = ai.analyze_performance(scores)
    
    return render_template('analysis.html', analysis=analysis_result, scores=progress.get('quiz_scores', {}))

@app.route('/semester_prep')
def semester_prep():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('semester_prep.html')

@app.route('/important_questions')
def important_questions():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('important_questions.html', subjects=get_syllabus().get('subjects', []))

@app.route('/topic_list')
def topic_list():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('topic_list.html', subjects=get_syllabus().get('subjects', []))

@app.route('/settings')
def settings():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('settings.html')

@app.route('/add_subject', methods=['POST'])
def add_subject():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    
    # Helper to append to syllabus.json
    syllabus = load_json('syllabus.json')
    new_sub = {
        "id": data['id'],
        "name": data['name'],
        "units": [
            {
                "id": data['id'] + "_u1",
                "name": "Unit 1",
                "topics": [{"id": data['id']+"_u1_t1", "name": data['topic'], "difficulty": "Moderate"}]
            }
        ]
    }
    
    if "subjects" not in syllabus: syllabus["subjects"] = []
    syllabus["subjects"].append(new_sub)
    save_json('syllabus.json', syllabus)
    
    return jsonify({"status": "success"})

@app.route('/mock_exam')
def mock_exam():
    if 'user' not in session: return redirect(url_for('index'))
    # Generate a random mixed quiz from all subjects
    # For demo, just picking first topic of first 3 subjects
    syllabus = get_syllabus()
    questions = []
    for subj in syllabus.get('subjects', [])[:3]:
        for unit in subj.get('units', [])[:1]:
            if unit.get('topics'):
                q = ai.generate_quiz(unit['topics'][0]['name'], "Hard")
                if q: questions.append(q[0]) # Take top 1 question from each
            
    return render_template('quiz.html', topic_id="mock_final", questions=questions)

def user_id(user_obj):
    # Helper to get the key from the dict. 
    # Since session stores the sub-object, we might need the username key. 
    # For now in students.json, let's assume 'roll_number' is unique enough or I change logic.
    # Actually, data_manager functions expect the *username* key from students.json.
    # Start: Hack fix.
    # Ideally store 'username' in session too.
    # For this demo, I will just loop through students.json to find key or store it in session during login.
    # Refactoring login needed slightly.
    return user_obj.get('info_username', 'student') # Setup in login

# Refactor Login to store username key
@app.route('/auth/login_fix', methods=['POST']) 
def login_new():
    # Will overwrite the previous login function logic
    pass

if __name__ == '__main__':
    app.run(debug=True)
