from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import re
import os

app = Flask(__name__)
app.secret_key = 'student_portal_secret_key_2025'


# ==============================
# ✅ Database Setup and Utilities
# ==============================
DB_NAME = 'database.db'

def get_connection():
    """Create a database connection (consistent everywhere)"""
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    """Initialize the database and create tables if they don't exist"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    course TEXT NOT NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()


# ==============================
# ✅ Validation Helpers
# ==============================
def validate_phone(phone):
    """Validate phone number format (10 digits)"""
    return re.match(r'^\d{10}$', phone)

def validate_email(email):
    """Basic email validation"""
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)


# ==============================
# ✅ Routes
# ==============================
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Student registration page"""
    if request.method == 'POST':
        # Get form data
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        course = request.form.get('course', '').strip()
        
        # Server-side validation
        if not all([first_name, last_name, email, phone, course]):
            flash('All fields are required!', 'danger')
            return render_template('register.html')
        
        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')
        
        if not validate_phone(phone):
            flash('Please enter a valid 10-digit phone number.', 'danger')
            return render_template('register.html')
        
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute('''INSERT INTO students (first_name, last_name, email, phone, course)
                         VALUES (?, ?, ?, ?, ?)''',
                      (first_name, last_name, email, phone, course))
            conn.commit()
            conn.close()
            flash('Registration successful!', 'success')
            
            return redirect(url_for('confirmation', 
                                    first_name=first_name, 
                                    last_name=last_name,
                                    email=email,
                                    course=course))
        except sqlite3.IntegrityError:
            flash('Email already registered! Please use a different email.', 'danger')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('register.html')


@app.route('/confirmation')
def confirmation():
    """Registration confirmation page"""
    first_name = request.args.get('first_name', '')
    last_name = request.args.get('last_name', '')
    email = request.args.get('email', '')
    course = request.args.get('course', '')
    
    return render_template('confirmation.html', 
                           first_name=first_name,
                           last_name=last_name,
                           email=email,
                           course=course)


@app.route('/students')
def students():
    """Display all registered students"""
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM students ORDER BY registration_date DESC")
        students = c.fetchall()
        conn.close()
        
        return render_template('students.html', students=students)
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'danger')
        return render_template('students.html', students=[])


# ==============================
# ✅ Error Handlers
# ==============================
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    flash('An internal error occurred. Please try again later.', 'danger')
    return render_template('500.html'), 500


# ==============================
# ✅ Main Entry Point
# ==============================
if __name__ == '__main__':
    # Initialize the database before running the app
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
