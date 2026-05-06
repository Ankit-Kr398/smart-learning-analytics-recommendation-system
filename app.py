from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Subject, Topic, StudyLog, WeeklyReport
from config import config
from datetime import datetime, date


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not username or not email or not password:
                flash('All fields are required.', 'danger')
                return render_template('register.html')

            if len(username) < 3:
                flash('Username must be at least 3 characters.', 'danger')
                return render_template('register.html')

            if len(password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('register.html')

            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('register.html')

            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already taken. Please choose another.', 'danger')
                return render_template('register.html')

            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already registered. Please log in.', 'danger')
                return render_template('register.html')

            hashed_password = generate_password_hash(password)

            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash(f'Welcome, {username}! Your account has been created.', 'success')
            return redirect(url_for('dashboard'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember = request.form.get('remember') == 'on'

            if not email or not password:
                flash('Email and password are required.', 'danger')
                return render_template('login.html')

            user = User.query.filter_by(email=email).first()

            if not user or not check_password_hash(user.password_hash, password):
                flash('Invalid email or password.', 'danger')
                return render_template('login.html')

            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        username = current_user.username
        logout_user()
        flash(f'Goodbye, {username}! You have been logged out.', 'info')
        return redirect(url_for('index'))


    #@app.route('/dashboard')
    #@login_required
    #def dashboard():
    #    return render_template('dashboard.html', user=current_user)
    

    @app.route('/api/topics/<int:subject_id>')
    @login_required
    def get_topics(subject_id):
        topics = Topic.query.filter_by(subject_id=subject_id).all()
        topics_list = [{'id': t.id, 'name': t.name} for t in topics]
        from flask import jsonify
        return jsonify(topics_list)


    @app.route('/log-study', methods=['GET', 'POST'])
    @login_required
    def log_study():
        subjects = Subject.query.all()

        if request.method == 'POST':
            topic_id = request.form.get('topic_id', '').strip()
            questions_attempted = request.form.get('questions_attempted', '').strip()
            correct_answers = request.form.get('correct_answers', '').strip()
            difficulty = request.form.get('difficulty', 'Medium').strip()
            study_time_minutes = request.form.get('study_time_minutes', '').strip()
            session_date = request.form.get('session_date', '').strip()
            notes = request.form.get('notes', '').strip()

            if not all([topic_id, questions_attempted, correct_answers,
                        study_time_minutes, session_date]):
                flash('All required fields must be filled.', 'danger')
                return render_template('log_study.html', subjects=subjects)

            try:
                topic_id = int(topic_id)
                questions_attempted = int(questions_attempted)
                correct_answers = int(correct_answers)
                study_time_minutes = int(study_time_minutes)
                session_date = datetime.strptime(session_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid data format. Please check your inputs.', 'danger')
                return render_template('log_study.html', subjects=subjects)

            if correct_answers > questions_attempted:
                flash('Correct answers cannot exceed questions attempted.', 'danger')
                return render_template('log_study.html', subjects=subjects)

            if questions_attempted < 0 or study_time_minutes < 0:
                flash('Values cannot be negative.', 'danger')
                return render_template('log_study.html', subjects=subjects)

            if difficulty not in ['Easy', 'Medium', 'Hard']:
                difficulty = 'Medium'

            topic = Topic.query.get(topic_id)
            if not topic:
                flash('Selected topic does not exist.', 'danger')
                return render_template('log_study.html', subjects=subjects)

            new_log = StudyLog(
                user_id=current_user.id,
                topic_id=topic_id,
                questions_attempted=questions_attempted,
                correct_answers=correct_answers,
                difficulty=difficulty,
                study_time_minutes=study_time_minutes,
                session_date=session_date,
                notes=notes if notes else None
            )

            db.session.add(new_log)
            db.session.commit()

            flash(f'Study session logged successfully! '
                  f'Accuracy: {new_log.accuracy()}%', 'success')
            return redirect(url_for('dashboard'))

        return render_template('log_study.html', subjects=subjects)


    @app.route('/dashboard')
    @login_required
    def dashboard():
        from analytics import compute_user_analytics
        from recommendation import generate_recommendations

        analytics_data = compute_user_analytics(current_user.id)
        recommendations = generate_recommendations(analytics_data)

        recent_logs = (StudyLog.query
                       .filter_by(user_id=current_user.id)
                       .order_by(StudyLog.session_date.desc())
                       .limit(5)
                       .all())

        return render_template(
            'dashboard.html',
            user=current_user,
            analytics=analytics_data,
            recommendations=recommendations,
            recent_logs=recent_logs
        )


    @app.route('/analytics')
    @login_required
    def analytics():
        from analytics import compute_user_analytics
        from flask import jsonify
        data = compute_user_analytics(current_user.id)
        return jsonify(data)


    @app.route('/recommendations')
    @login_required
    def recommendations():
        from analytics import compute_user_analytics
        from recommendation import generate_recommendations
        from flask import jsonify
        analytics_data = compute_user_analytics(current_user.id)
        recs = generate_recommendations(analytics_data)
        return jsonify(recs)


    @app.route('/weekly-report')
    @login_required
    def weekly_report():
        from analytics import compute_weekly_report
        report_data = compute_weekly_report(current_user.id)
        return render_template('weekly_report.html',
                               user=current_user,
                               report=report_data)


    @app.route('/monthly-report')
    @login_required
    def monthly_report():
        from analytics import compute_monthly_report
        report_data = compute_monthly_report(current_user.id)
        return render_template('monthly_report.html',
                               user=current_user,
                               report=report_data)


    @app.route('/history')
    @login_required
    def history():
        page = request.args.get('page', 1, type=int)
        logs = (StudyLog.query
                .filter_by(user_id=current_user.id)
                .order_by(StudyLog.session_date.desc())
                .paginate(page=page, per_page=10, error_out=False))
        return render_template('history.html',
                               user=current_user,
                               logs=logs)


    @app.route('/delete-log/<int:log_id>', methods=['POST'])
    @login_required
    def delete_log(log_id):
        log = StudyLog.query.get_or_404(log_id)
        if log.user_id != current_user.id:
            flash('You are not authorized to delete this entry.', 'danger')
            return redirect(url_for('history'))
        db.session.delete(log)
        db.session.commit()
        flash('Study log deleted.', 'info')
        return redirect(url_for('history'))

    return app


def seed_subjects():
    subjects_data = [
        {'name': 'DSA', 'description': 'Data Structures and Algorithms', 'weight': 0.30},
        {'name': 'DBMS', 'description': 'Database Management Systems', 'weight': 0.20},
        {'name': 'OS', 'description': 'Operating Systems', 'weight': 0.15},
        {'name': 'CN', 'description': 'Computer Networks', 'weight': 0.15},
        {'name': 'Aptitude', 'description': 'Quantitative and Logical Aptitude', 'weight': 0.20},
    ]

    topics_data = {
        'DSA': ['Arrays', 'Linked Lists', 'Stacks & Queues', 'Trees', 'Graphs', 'Sorting', 'Searching', 'Dynamic Programming', 'Recursion', 'Hashing'],
        'DBMS': ['ER Model', 'Normalization', 'SQL Basics', 'Joins', 'Transactions', 'Indexing', 'Keys & Constraints'],
        'OS': ['Processes & Threads', 'CPU Scheduling', 'Memory Management', 'Deadlocks', 'File Systems', 'Synchronization'],
        'CN': ['OSI Model', 'TCP/IP', 'HTTP & HTTPS', 'DNS', 'Routing', 'Subnetting', 'Socket Programming'],
        'Aptitude': ['Number Systems', 'Percentages', 'Time & Work', 'Probability', 'Logical Reasoning', 'Data Interpretation'],
    }

    for s in subjects_data:
        exists = Subject.query.filter_by(name=s['name']).first()
        if not exists:
            subject = Subject(name=s['name'], description=s['description'], weight=s['weight'])
            db.session.add(subject)
            db.session.flush()

            for topic_name in topics_data[s['name']]:
                topic = Topic(name=topic_name, subject_id=subject.id)
                db.session.add(topic)

    db.session.commit()


if __name__ == '__main__':
    app = create_app('default')
    with app.app_context():
        db.create_all()
        seed_subjects()
        print("Database initialized and subjects seeded.")
    app.run(debug=True)


# For Render/Gunicorn deployment
application = create_app('default')
with application.app_context():
    db.create_all()
    seed_subjects()










