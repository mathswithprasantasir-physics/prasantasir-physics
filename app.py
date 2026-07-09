from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from database import db, Question
from datetime import datetime
import os

# Delete old database if exists (for fresh start)
if os.path.exists('neet_physics.db'):
    os.remove('neet_physics.db')
    print("✅ Old database deleted!")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///neet_physics.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print("✅ Database created with all columns!")

# Admin password
ADMIN_PASSWORD = 'admin123'

# All topics list
TOPICS = [
    'Units & Measurement', 'Motion in a Straight Line', 'Motion in a Plane',
    'Laws of Motion', 'Work, Energy and Power', 'Center of Mass and Collision',
    'Rotational Motion', 'Gravitation', 'Properties of Matter',
    'Heat and Thermodynamics', 'Oscillations', 'Waves',
    'Electricity', 'Current Electricity', 'Capacitor',
    'Moving Charges and Magnetism', 'Magnetism and Matter',
    'Electromagnetic Induction', 'Alternating Current', 'Electromagnetic Waves',
    'Optics', 'Wave Optics', 'Geometrical Optics',
    'Atoms and Nuclei', 'Dual Nature of Radiation and Matter', 'Semiconductor Electronics'
]

# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('✅ Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('❌ Incorrect password!', 'error')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('✅ Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    total_questions = Question.query.count()
    
    topic_stats = []
    for topic in TOPICS:
        count = Question.query.filter_by(topic=topic).count()
        if count > 0:
            topic_stats.append({
                'name': topic,
                'count': count,
                'weightage': round((count / total_questions * 100) if total_questions > 0 else 0, 2)
            })
    
    recent_questions = Question.query.order_by(Question.created_at.desc()).limit(10).all()
    
    easy = Question.query.filter_by(difficulty='Easy').count()
    medium = Question.query.filter_by(difficulty='Medium').count()
    hard = Question.query.filter_by(difficulty='Hard').count()
    
    return render_template('admin/dashboard.html',
                         total_questions=total_questions,
                         topic_stats=topic_stats,
                         recent_questions=recent_questions,
                         easy=easy, medium=medium, hard=hard)

@app.route('/admin/questions')
def admin_questions():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    topic_filter = request.args.get('topic', '')
    year_filter = request.args.get('year', '')
    difficulty_filter = request.args.get('difficulty', '')
    
    query = Question.query
    if topic_filter:
        query = query.filter_by(topic=topic_filter)
    if year_filter:
        query = query.filter_by(year=year_filter)
    if difficulty_filter:
        query = query.filter_by(difficulty=difficulty_filter)
    
    questions = query.order_by(Question.created_at.desc()).all()
    
    return render_template('admin/questions_list.html',
                         questions=questions,
                         topics=TOPICS,
                         current_topic=topic_filter,
                         current_year=year_filter,
                         current_difficulty=difficulty_filter)

@app.route('/admin/add-question', methods=['GET', 'POST'])
def admin_add_question():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        try:
            question = Question(
                topic=request.form['topic'],
                subtopic=request.form.get('subtopic', ''),
                year=request.form.get('year', '2026'),
                question_text=request.form['question_text'],
                question_image=request.form.get('question_image', ''),
                option_a=request.form.get('option_a', ''),
                option_b=request.form.get('option_b', ''),
                option_c=request.form.get('option_c', ''),
                option_d=request.form.get('option_d', ''),
                option_a_image=request.form.get('option_a_image', ''),
                option_b_image=request.form.get('option_b_image', ''),
                option_c_image=request.form.get('option_c_image', ''),
                option_d_image=request.form.get('option_d_image', ''),
                correct_answer=request.form.get('correct_answer', ''),
                solution=request.form.get('solution', ''),
                solution_image=request.form.get('solution_image', ''),
                explanation=request.form.get('explanation', ''),
                marks=int(request.form.get('marks', 4)),
                negative_marks=int(request.form.get('negative_marks', 1)),
                exam_type=request.form.get('exam_type', 'NEET'),
                difficulty=request.form.get('difficulty', 'Medium')
            )
            db.session.add(question)
            db.session.commit()
            flash('✅ Question added successfully!', 'success')
            return redirect(url_for('admin_questions'))
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template('admin/add_question.html', topics=TOPICS)

@app.route('/admin/edit-question/<int:id>', methods=['GET', 'POST'])
def admin_edit_question(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    question = Question.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            question.topic = request.form['topic']
            question.subtopic = request.form.get('subtopic', '')
            question.year = request.form.get('year', '2026')
            question.question_text = request.form['question_text']
            question.question_image = request.form.get('question_image', '')
            question.option_a = request.form.get('option_a', '')
            question.option_b = request.form.get('option_b', '')
            question.option_c = request.form.get('option_c', '')
            question.option_d = request.form.get('option_d', '')
            question.option_a_image = request.form.get('option_a_image', '')
            question.option_b_image = request.form.get('option_b_image', '')
            question.option_c_image = request.form.get('option_c_image', '')
            question.option_d_image = request.form.get('option_d_image', '')
            question.correct_answer = request.form.get('correct_answer', '')
            question.solution = request.form.get('solution', '')
            question.solution_image = request.form.get('solution_image', '')
            question.explanation = request.form.get('explanation', '')
            question.marks = int(request.form.get('marks', 4))
            question.negative_marks = int(request.form.get('negative_marks', 1))
            question.exam_type = request.form.get('exam_type', 'NEET')
            question.difficulty = request.form.get('difficulty', 'Medium')
            question.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('✅ Question updated successfully!', 'success')
            return redirect(url_for('admin_questions'))
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template('admin/edit_question.html', question=question, topics=TOPICS)

@app.route('/admin/delete-question/<int:id>')
def admin_delete_question(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    question = Question.query.get_or_404(id)
    try:
        db.session.delete(question)
        db.session.commit()
        flash('✅ Question deleted successfully!', 'success')
    except Exception as e:
        flash(f'❌ Error: {str(e)}', 'error')
    return redirect(url_for('admin_questions'))

# ==================== STUDENT ROUTES ====================

@app.route('/')
def student_home():
    total_questions = Question.query.count()
    
    topic_stats = []
    for topic in TOPICS:
        count = Question.query.filter_by(topic=topic).count()
        if count > 0:
            topic_stats.append({
                'name': topic,
                'count': count
            })
    
    random_questions = Question.query.order_by(db.func.random()).limit(5).all()
    
    return render_template('student/index.html',
                         total_questions=total_questions,
                         topic_stats=topic_stats,
                         random_questions=random_questions)

@app.route('/practice')
def student_practice():
    topic_filter = request.args.get('topic', '')
    difficulty_filter = request.args.get('difficulty', '')
    
    query = Question.query
    if topic_filter:
        query = query.filter_by(topic=topic_filter)
    if difficulty_filter:
        query = query.filter_by(difficulty=difficulty_filter)
    
    questions = query.order_by(db.func.random()).all()
    
    return render_template('student/practice.html',
                         questions=questions,
                         topics=TOPICS,
                         current_topic=topic_filter,
                         current_difficulty=difficulty_filter)

@app.route('/question/<int:id>')
def student_question_detail(id):
    question = Question.query.get_or_404(id)
    return render_template('student/question_detail.html', question=question)

@app.route('/api/questions')
def api_questions():
    questions = Question.query.all()
    return jsonify([q.to_dict() for q in questions])

if __name__ == '__main__':
    app.run(debug=True)