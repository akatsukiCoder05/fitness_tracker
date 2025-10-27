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

# Create nutrition table
cursor.execute("""
CREATE TABLE IF NOT EXISTS nutrition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    age INT NOT NULL,
    height FLOAT NOT NULL,
    weight FLOAT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    daily_activity_level VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")
db.commit()

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
@app.route('/workouts/gym/chest')
def chest_gym_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    return render_template('chest.html')

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
    
    return render_template('workouts.html')

@app.route('/workouts/gym/chest')
def chest_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    
    return render_template('chest.html')

@app.route('/workouts/gym/shoulder')
def shoulder_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('shoulder.html')


@app.route('/workouts/gym/bicep')
def bicep_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('bicep.html')

@app.route('/workouts/gym/back')
def back_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('back.html')    

@app.route('/workouts/gym/leg')
def leg_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('leg.html')      

@app.route('/workouts/gym/abs')
def abs_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('abs.html')

@app.route('/workouts/gym/forearm')
def forearm_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('forearm.html')

@app.route('/workouts/calisthenic')
def calisthenic_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('calisthenic.html')

@app.route('/workouts/calisthenic/upperbody')
def upperbody_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('upperbody.html')

@app.route('/workouts/calisthenic/lowerbody')
def lowerbody_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('lowerbody.html')    

@app.route('/workouts/calisthenic/corepart')
def corepart_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('corepart.html')
   
@app.route('/workouts/calisthenic/fullbody')
def fullbody_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('fullbody.html')

@app.route('/workouts/homeworkout')
def homeworkout_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('homeworkout.html')   

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
# NUTRITION ROUTE
# -------------------------------

@app.route('/nutrition', methods=['GET', 'POST'])
def nutrition():
    if 'user' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))

    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO nutrition 
                (user_id, age, height, weight, gender, daily_activity_level)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session['user']['id'],
                request.form['age'],
                request.form['height'],
                request.form['weight'],
                request.form['gender'],
                request.form['daily_activity_level']
            ))
            db.commit()
            flash("Nutrition information saved!", "success")
        except Exception as e:
            flash(f"Error: {str(e)}", "error")
        return redirect(url_for('dashboard'))
    
    return render_template('nutrition.html')


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
