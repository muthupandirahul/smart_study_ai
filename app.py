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
        role = request.form.get('role', 'student')
        
        if create_user(username, password, roll_number, name, email, role):
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
    if user.get('role') == 'professor':
        return redirect(url_for('professor_dashboard'))
    
    progress = get_student_progress(user_id(user))
    syllabus = get_syllabus()
    syllabus_meta = load_json('syllabus_meta.json')
    
    # Calculate stats and per-subject readiness
    total_topics = 0
    subjects_data = []
    
    topics_completed = progress.get('topics_completed', [])
    quiz_scores = progress.get('quiz_scores', {})
    
    for subj in syllabus.get('subjects', []):
        subj_total = 0
        subj_completed = 0
        subj_score_sum = 0
        subj_quizzes = 0
        
        for unit in subj.get('units', []):
            for t in unit.get('topics', []):
                subj_total += 1
                total_topics += 1
                if t['id'] in topics_completed:
                    subj_completed += 1
                
                if t['id'] in quiz_scores:
                    qs = quiz_scores[t['id']]
                    if qs['total'] > 0:
                        subj_score_sum += (qs['score'] / qs['total']) * 100
                        subj_quizzes += 1
        
        # Readiness = Coverage(50%) + Performance(50%)
        coverage_score = (subj_completed / subj_total * 50) if subj_total > 0 else 0
        perf_score = (subj_score_sum / subj_quizzes * 0.5) if subj_quizzes > 0 else 0
        readiness_score = int(coverage_score + perf_score)
        
        status = "Needs Improvement"
        status_color = "#ef4444" # Red
        if readiness_score >= 80:
            status = "Exam Ready"
            status_color = "#22c55e" # Green
        elif readiness_score >= 60:
            status = "Moderate"
            status_color = "#f59e0b" # Yellow
            
        subjects_data.append({
            **subj,
            "readiness": readiness_score,
            "status": status,
            "status_color": status_color
        })
        
    completed_count = len(topics_completed)
    percent = int((completed_count / total_topics * 100)) if total_topics > 0 else 0
    
    return render_template('dashboard.html', 
                           user=user, 
                           progress=progress, 
                           percent=percent,
                           subjects=subjects_data,
                           syllabus_meta=syllabus_meta)

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
    
    # Find topic name from syllabus
    topic_name = "General Topic"
    syllabus = get_syllabus()
    for subj in syllabus.get('subjects', []):
        for unit in subj.get('units', []):
            for t in unit.get('topics', []):
                if t['id'] == topic_id:
                    topic_name = t['name']
                    break
            if topic_name != "General Topic": break
        if topic_name != "General Topic": break

    questions = ai.generate_quiz(topic_name, difficulty, num_questions=5)
    return render_template('quiz.html', topic_id=topic_id, questions=questions, quiz_type='topic')

@app.route('/subject_exam/<subj_id>')
def subject_exam(subj_id):
    if 'user' not in session: return redirect(url_for('index'))
    
    syllabus = get_syllabus()
    subject = next((s for s in syllabus.get('subjects', []) if s['id'] == subj_id), None)
    
    if not subject:
        return redirect(url_for('dashboard'))
    
    all_questions = []
    difficulty = session.get('difficulty', 'Moderate')
    
    # Target: 5 questions per unit, 5 units = 25 questions
    units = subject.get('units', [])[:5] 
    
    q_counter = 0 # Global seed for unique mock generation
    for unit in units:
        topics = unit.get('topics', [])
        if not topics: continue
        
        unit_qs = []
        # Distribute 5 questions across topics in this unit
        for i, topic in enumerate(topics):
            if len(unit_qs) >= 5: break
            
            # How many questions to take from this topic
            needed = 1
            if i == len(topics) - 1: # Last topic gets remainder
                needed = 5 - len(unit_qs)
            elif len(unit_qs) + (len(topics) - i) <= 5: 
                needed = 1 # Take at least 1 per topic if space allows
            
            if needed <= 0: continue
            
            qs = ai.generate_quiz(topic['name'], difficulty, num_questions=needed, global_seed=q_counter)
            unit_qs.extend(qs)
            q_counter += needed
            
        all_questions.extend(unit_qs[:5])

    # Ensure we have exactly 25 if possible
    final_questions = all_questions[:25]
    for i, q in enumerate(final_questions):
        q['id'] = i + 1 # Re-index for UI
        
    return render_template('quiz.html', 
                           topic_id=subj_id, 
                           questions=final_questions, 
                           quiz_type='semester',
                           subject_name=subject['name'])

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

# --- Professor Routes ---

@app.route('/professor/dashboard')
def professor_dashboard():
    if 'user' not in session or session['user'].get('role') != 'professor':
        return redirect(url_for('index'))
    return render_template('professor_dashboard.html', user=session['user'])

@app.route('/professor/analytics')
def class_analytics():
    if 'user' not in session or session['user'].get('role') != 'professor':
        return redirect(url_for('index'))
    
    from data_manager import get_class_analytics
    analytics = get_class_analytics()
    return render_template('class_analytics.html', analytics=analytics)

@app.route('/professor/upload_syllabus', methods=['POST'])
def upload_syllabus():
    if 'user' not in session or session['user'].get('role') != 'professor':
        return jsonify({"error": "Unauthorized"}), 401
    
    file = request.files.get('syllabus')
    if file and file.filename.endswith('.json'):
        file.save(os.path.join('data', 'syllabus.json'))
        
        # Update metadata
        from datetime import datetime
        meta = {"last_updated": datetime.now().strftime("%d %b %Y, %H:%M")}
        save_json('syllabus_meta.json', meta)
        
        return redirect(url_for('professor_dashboard'))
    return "Invalid file format", 400

@app.route('/chatbot')
def chatbot():
    if 'user' not in session: return redirect(url_for('index'))
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    user_query = request.json.get('message')
    if not user_query: return jsonify({"response": "I didn't catch that. Could you repeat your question?"})
    
    response = ai.get_chat_response(user_query)
    return jsonify({"response": response})

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
    
    # Calculate readiness for analysis page too
    subjects_data = []
    syllabus = get_syllabus()
    topics_completed = progress.get('topics_completed', [])
    quiz_scores_map = progress.get('quiz_scores', {})
    
    for subj in syllabus.get('subjects', []):
        subj_total = 0
        subj_completed = 0
        subj_score_sum = 0
        subj_quizzes = 0
        for unit in subj.get('units', []):
            for t in unit.get('topics', []):
                subj_total += 1
                if t['id'] in topics_completed: subj_completed += 1
                if t['id'] in quiz_scores_map:
                    qs = quiz_scores_map[t['id']]
                    if qs['total'] > 0:
                        subj_score_sum += (qs['score'] / qs['total']) * 100
                        subj_quizzes += 1
        
        coverage_score = (subj_completed / subj_total * 50) if subj_total > 0 else 0
        perf_score = (subj_score_sum / subj_quizzes * 0.5) if subj_quizzes > 0 else 0
        readiness_score = int(coverage_score + perf_score)
        
        status = "Needs Improvement"
        status_color = "#ef4444" 
        if readiness_score >= 80: status, status_color = "Exam Ready", "#22c55e"
        elif readiness_score >= 60: status, status_color = "Moderate", "#f59e0b"
            
        subjects_data.append({**subj, "readiness": readiness_score, "status": status, "status_color": status_color})
    
    return render_template('analysis.html', 
                           analysis=analysis_result, 
                           scores=progress.get('quiz_scores', {}),
                           subjects=subjects_data)

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
    all_topics = []
    for subj in syllabus.get('subjects', []):
        for unit in subj.get('units', []):
            for t in unit.get('topics', []):
                all_topics.append(t['name'])
    
    # Shuffle and pick topics to get 25 questions
    import random
    random.shuffle(all_topics)
    
    questions = []
    # Try to get 1 question from each unique topic until we have 25
    for topic_name in all_topics:
        if len(questions) >= 25: break
        qs = ai.generate_quiz(topic_name, "Hard", num_questions=1)
        if qs: questions.append(qs[0])
    
    # If still short, supplement
    if len(questions) < 25:
        more = ai.generate_quiz("General Knowledge", "Hard", num_questions=(25 - len(questions)))
        questions.extend(more)
            
    return render_template('quiz.html', topic_id="mock_final", questions=questions, quiz_type='semester')

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
