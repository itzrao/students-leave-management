from flask import Flask, render_template, request, redirect, session, flash
from db_config import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from markupsafe import Markup
from flask import Flask, render_template, request, redirect, flash, url_for
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def home():
    return render_template('home.html')





@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect('/')
@app.route('/instructions')
def instructions():
    return render_template('instructions.html')






@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form['student_id']
        password = request.form['password']
        course = request.form['course']
        name = request.form['name']
        mobile = request.form['mobile']
        email = request.form['email']
        unit = request.form['unit']
        address = request.form['address']

        conn = get_connection()
        cursor = conn.cursor()

        # Check for duplicate student_id or email
        cursor.execute("SELECT * FROM users WHERE student_id = %s OR email = %s", (student_id, email))
        existing = cursor.fetchone()

        if existing:
            flash('Email or Student ID already exists!', 'danger')
            conn.close()
            return redirect(url_for('register'))

        try:
            cursor.execute("""
                INSERT INTO users (student_id, password, course_name, full_name, mobile, email, unit_area, address, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'present')
            """, (student_id, generate_password_hash(password), course, name, mobile, email, unit, address))
            conn.commit()
            flash('Registration successful!', 'success')
        except Exception as e:
            print(e)
            flash('Something went wrong during registration.', 'danger')
        finally:
            conn.close()
            return redirect(url_for('register'))

    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data['email']
        password = data['password']
        role = data['role']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s  AND role=%s", (email,  role))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user'] = user
            flash("Login successful!", "success")
            if user['role'] == 'Student':
                return redirect('/student/dashboard')
            else:
                return redirect('/faculty/dashboard')
        else:
            flash("Invalid login details", "danger")
    return render_template('login.html')




# Student Dashboard (show form + history)
@app.route('/student/dashboard', methods=['GET', 'POST'])
def student_dashboard():
    if 'user' not in session or session['user']['role'] != 'Student':
        return redirect('/login')

    user = session['user']

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Leave application submission
        leave_from = request.form['leave_from']
        leave_to = request.form['leave_to']

        # Calculate no_of_days
        d_from = datetime.strptime(leave_from, '%Y-%m-%d')
        d_to = datetime.strptime(leave_to, '%Y-%m-%d')
        no_of_days = (d_to - d_from).days + 1

        cursor.execute("""
            INSERT INTO leave_applications (student_id, student_name, leave_from, leave_to, no_of_days, status, applied_on, modified_by)
            VALUES (%s, %s, %s, %s, %s, 'Pending', NOW(), %s)
        """, (user['student_id'], user['full_name'], leave_from, leave_to, no_of_days, user['full_name']))
        conn.commit()
        flash("Leave applied successfully!", "success")

    # Fetch leave history for logged-in student
    cursor.execute("SELECT * FROM leave_applications WHERE student_id=%s ORDER BY applied_on DESC", (user['student_id'],))
    leaves = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('student_dashboard.html', leaves=leaves, user=user)

@app.route('/faculty/dashboard')
def faculty_dashboard():
    if 'user' not in session or session['user']['role'] != 'Faculty':
        return redirect('/login')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all pending leave applications
    cursor.execute("""
        SELECT * FROM leave_applications WHERE status = 'Pending' ORDER BY applied_on ASC
    """)
    pending_leaves = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('faculty_dashboard.html', pending_leaves=pending_leaves)


@app.route('/faculty/approve_leave/<int:leave_id>/<string:action>', methods=['POST'])
def approve_leave(leave_id, action):
    if 'user' not in session or session['user']['role'] != 'Faculty':
        return redirect('/login')

    if action not in ['Approved', 'Rejected']:
        flash("Invalid action!", "danger")
        return redirect('/faculty/dashboard')

    user = session['user']

    conn = get_connection()
    cursor = conn.cursor()

    # Get student_id of the leave application
    cursor.execute("SELECT student_id FROM leave_applications WHERE leave_id = %s", (leave_id,))
    res = cursor.fetchone()
    if not res:
        flash("Leave application not found.", "danger")
        return redirect('/faculty/dashboard')

    student_id = res[0]

    # Update the leave application status
    cursor.execute("""
        UPDATE leave_applications
        SET status = %s, modified_by = %s, last_modified = NOW()
        WHERE leave_id = %s
    """, (action, user['full_name'], leave_id))
    conn.commit()

    cursor.close()
    conn.close()

    flash(f"Leave application {action.lower()} successfully!", "success")
    return redirect('/faculty/dashboard')




def get_leave_history(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT leave_from, leave_to, status
        FROM leave_applications
        WHERE student_id = %s AND status != 'Pending'
        ORDER BY applied_on DESC
        LIMIT 5
    """, (student_id,))
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return history

# Make the function available inside Jinja templates
app.jinja_env.globals.update(get_leave_history=get_leave_history)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')  # You got this

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contact_messages (name, email, subject, message, submitted_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (name, email, subject, message))  # Include message here
        conn.commit()

        flash('Thank you for your message. We will get back to you shortly!', 'success')
        return redirect('/contact')

    return render_template('contact.html')




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



