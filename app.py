from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from data_loader import load_questions, save_questions, get_topics
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'

# Admin password
ADMIN_PASSWORD = 'admin123'

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
    
    questions = load_questions()
    total_questions = len(questions)
    
    # Topic-wise statistics
    topic_stats = {}
    for q in questions:
        topic = q.get('topic', 'Unknown')
        topic_stats[topic] = topic_stats.get(topic, 0) + 1
    
    topic_list = [{'name': k, 'count': v, 'weightage': round((v/total_questions*100) if total_questions > 0 else 0, 2)} 
                  for k, v in topic_stats.items()]
    
    # Difficulty distribution
    easy = len([q for q in questions if q.get('difficulty') == 'Easy'])
    medium = len([q for q in questions if q.get('difficulty') == 'Medium'])
    hard = len([q for q in questions if q.get('difficulty') == 'Hard'])
    
    return render_template('admin/dashboard.html',
                         total_questions=total_questions,
                         topic_stats=topic_list,
                         recent_questions=questions[:10],
                         easy=easy, medium=medium, hard=hard)

@app.route('/admin/questions')
def admin_questions():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    questions = load_questions()
    topics = get_topics()
    
    # Filter
    topic_filter = request.args.get('topic', '')
    difficulty_filter = request.args.get('difficulty', '')
    
    filtered = questions
    if topic_filter:
        filtered = [q for q in filtered if q.get('topic') == topic_filter]
    if difficulty_filter:
        filtered = [q for q in filtered if q.get('difficulty') == difficulty_filter]
    
    return render_template('admin/questions_list.html',
                         questions=filtered,
                         topics=topics)

@app.route('/admin/add-question', methods=['GET', 'POST'])
def admin_add_question():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    topics = get_topics()
    
    if request.method == 'POST':
        try:
            questions = load_questions()
            
            # Generate new ID
            new_id = max([q.get('id', 0) for q in questions]) + 1 if questions else 1
            
            new_question = {
                'id': new_id,
                'topic': request.form['topic'],
                'subtopic': request.form.get('subtopic', ''),
                'year': request.form.get('year', '2026'),
                'question_text': request.form['question_text'],
                'question_image': request.form.get('question_image', ''),
                'option_a': request.form.get('option_a', ''),
                'option_b': request.form.get('option_b', ''),
                'option_c': request.form.get('option_c', ''),
                'option_d': request.form.get('option_d', ''),
                'option_a_image': request.form.get('option_a_image', ''),
                'option_b_image': request.form.get('option_b_image', ''),
                'option_c_image': request.form.get('option_c_image', ''),
                'option_d_image': request.form.get('option_d_image', ''),
                'correct_answer': request.form.get('correct_answer', ''),
                'solution': request.form.get('solution', ''),
                'solution_image': request.form.get('solution_image', ''),
                'explanation': request.form.get('explanation', ''),
                'marks': int(request.form.get('marks', 4)),
                'negative_marks': int(request.form.get('negative_marks', 1)),
                'exam_type': request.form.get('exam_type', 'NEET'),
                'difficulty': request.form.get('difficulty', 'Medium')
            }
            
            questions.append(new_question)
            save_questions(questions)
            
            flash('✅ Question added successfully!', 'success')
            return redirect(url_for('admin_questions'))
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template('admin/add_question.html', topics=topics)

@app.route('/admin/edit-question/<int:id>', methods=['GET', 'POST'])
def admin_edit_question(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    questions = load_questions()
    question = next((q for q in questions if q.get('id') == id), None)
    
    if not question:
        flash('❌ Question not found!', 'error')
        return redirect(url_for('admin_questions'))
    
    topics = get_topics()
    
    if request.method == 'POST':
        try:
            # Update question
            question['topic'] = request.form['topic']
            question['subtopic'] = request.form.get('subtopic', '')
            question['year'] = request.form.get('year', '2026')
            question['question_text'] = request.form['question_text']
            question['question_image'] = request.form.get('question_image', '')
            question['option_a'] = request.form.get('option_a', '')
            question['option_b'] = request.form.get('option_b', '')
            question['option_c'] = request.form.get('option_c', '')
            question['option_d'] = request.form.get('option_d', '')
            question['option_a_image'] = request.form.get('option_a_image', '')
            question['option_b_image'] = request.form.get('option_b_image', '')
            question['option_c_image'] = request.form.get('option_c_image', '')
            question['option_d_image'] = request.form.get('option_d_image', '')
            question['correct_answer'] = request.form.get('correct_answer', '')
            question['solution'] = request.form.get('solution', '')
            question['solution_image'] = request.form.get('solution_image', '')
            question['explanation'] = request.form.get('explanation', '')
            question['marks'] = int(request.form.get('marks', 4))
            question['negative_marks'] = int(request.form.get('negative_marks', 1))
            question['exam_type'] = request.form.get('exam_type', 'NEET')
            question['difficulty'] = request.form.get('difficulty', 'Medium')
            
            save_questions(questions)
            flash('✅ Question updated successfully!', 'success')
            return redirect(url_for('admin_questions'))
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'error')
    
    return render_template('admin/edit_question.html', question=question, topics=topics)

@app.route('/admin/delete-question/<int:id>')
def admin_delete_question(id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    questions = load_questions()
    questions = [q for q in questions if q.get('id') != id]
    save_questions(questions)
    
    flash('✅ Question deleted successfully!', 'success')
    return redirect(url_for('admin_questions'))

# ==================== STUDENT ROUTES ====================

@app.route('/')
def student_home():
    questions = load_questions()
    total_questions = len(questions)
    
    # Topic-wise statistics
    topic_stats = {}
    for q in questions:
        topic = q.get('topic', 'Unknown')
        topic_stats[topic] = topic_stats.get(topic, 0) + 1
    
    topic_list = [{'name': k, 'count': v} for k, v in topic_stats.items()]
    
    # Random questions
    random_questions = random.sample(questions, min(5, len(questions))) if questions else []
    
    return render_template('student/index.html',
                         total_questions=total_questions,
                         topic_stats=topic_list,
                         random_questions=random_questions)

@app.route('/practice')
def student_practice():
    questions = load_questions()
    topics = get_topics()
    
    topic_filter = request.args.get('topic', '')
    difficulty_filter = request.args.get('difficulty', '')
    
    filtered = questions
    if topic_filter:
        filtered = [q for q in filtered if q.get('topic') == topic_filter]
    if difficulty_filter:
        filtered = [q for q in filtered if q.get('difficulty') == difficulty_filter]
    
    return render_template('student/practice.html',
                         questions=filtered,
                         topics=topics,
                         current_topic=topic_filter,
                         current_difficulty=difficulty_filter)

@app.route('/question/<int:id>')
def student_question_detail(id):
    questions = load_questions()
    question = next((q for q in questions if q.get('id') == id), None)
    if not question:
        return "Question not found", 404
    return render_template('student/question_detail.html', question=question)

@app.route('/api/questions')
def api_questions():
    return jsonify(load_questions())

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
