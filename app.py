from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = "arambh_secret_key"

# -------------------------------
# MySQL configuration
# -------------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",        # your MySQL username
    password="",        # your MySQL password
    database="login_db" # existing database
)
cursor = db.cursor(dictionary=True)

# -------------------------------
# HOME (Login Page)
# -------------------------------
@app.route('/')
def home():
    return render_template('login.html')


# -------------------------------
# LOGIN ROUTE
# -------------------------------
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        flash("Login Successful!", "success")
        session['user'] = user
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password", "danger")
        return redirect(url_for('home'))


# -------------------------------
# REGISTER ROUTE
# -------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        dob = request.form.get('dob')
        email = request.form.get('email')
        password = request.form.get('password')

        if not (first_name and last_name and dob and email and password):
            flash("All fields are required!", "error")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        try:
            cursor.execute(
                "INSERT INTO users (first_name, last_name, DOB, email, password) VALUES (%s, %s, %s, %s, %s)",
                (first_name, last_name, dob, email, hashed_password)
            )
            db.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('home'))
        except mysql.connector.IntegrityError:
            flash("Email already registered!", "error")
            return redirect(url_for('register'))

    return render_template('register.html')


# -------------------------------
# DASHBOARD (After login)
# -------------------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))
    return render_template('dashboard.html', user=session['user'])


# -------------------------------
# WORKOUTS PAGE (Protected)
# -------------------------------
@app.route('/workouts/gym')
def gym_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    return render_template('gym.html')


@app.route('/workouts')
def workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    
    # Fetch workouts from database
    # cursor.execute("SELECT * FROM workouts")
    # workouts_list = cursor.fetchall()
    return render_template('workouts.html')


# -------------------------------
# ADD WORKOUT ROUTE
# -------------------------------
@app.route('/add_workout', methods=['POST'])
def add_workout():
    if 'user' not in session:
        flash("Login required", "warning")
        return redirect(url_for('home'))

    name = request.form.get('name')

    if name:
        cursor.execute("INSERT INTO workouts (name) VALUES (%s)", (name,))
        db.commit()
        flash("Workout added successfully!", "success")
    else:
        flash("Please enter a workout name", "error")

    return redirect(url_for('workouts'))


# -------------------------------
# LOGOUT ROUTE
# -------------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
