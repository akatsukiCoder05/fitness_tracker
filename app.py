from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
from flask import jsonify  # JSON response ke liye ye import zaroor add karein
import mysql.connector
import requests  # Ye line add karna zaroori hai
import json
import markdown
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import login_user, current_user, login_required




app = Flask(__name__)
app.secret_key = "arambh_secret_key"

# Configure database URI (SQLite example)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arambh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database  = SQLAlchemy(app)

UPLOAD_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ FUNCTION MUST BE ABOVE ROUTE
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -------------------------------
# MySQL configuration
# -------------------------------
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",        # your MySQL username
#     password="",        # your MySQL password
#     database="login_db" # existing database
# )
# cursor = db.cursor(dictionary=True)

# Create nutrition table
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS nutrition (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT NOT NULL,
#     age INT NOT NULL,
#     height FLOAT NOT NULL,
#     weight FLOAT NOT NULL,
#     gender VARCHAR(10) NOT NULL,
#     daily_activity_level VARCHAR(50) NOT NULL,
#     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (user_id) REFERENCES users(id)
# )
# """)
# db.commit()


# User Table Schema
class User(database.Model):
    __tablename__ = 'users'

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(120), nullable=False)
    email = database.Column(database.String(150), unique=True, nullable=False)
    dob = database.Column(database.Date, nullable=False)
    password = database.Column(database.String(255), nullable=False)

    # ✅ NEW FIELD (Profile Picture Path)
    profile_image = database.Column(
        database.String(255),
        nullable=True,
        default="default.png"
    )

    # ✅ Recommended extra fields
    created_at = database.Column(
        database.DateTime,
        default=datetime.utcnow
    )

    updated_at = database.Column(
        database.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    workouts = database.relationship('WorkoutSession', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"
        return f"<User {self.email}>"

        



#  Workout Session Table Schema
# class WorkoutSession(database.Model):
#     __tablename__ = 'workout_sessions'

#     id = database.Column(database.Integer, primary_key=True)

#     user_id = database.Column(
#         database.Integer,
#         database.ForeignKey('users.id'),
#         nullable=False
#     )

#     duration_seconds = database.Column(database.Integer, nullable=False)
#     calories_burned = database.Column(database.Integer, nullable=False)

#     created_at = database.Column(
#         database.DateTime,
#         default=datetime.utcnow
#     )

#     def __repr__(self):
#         return f"<Workout {self.user_id} - {self.calories_burned} kcal>"

class WorkoutSession(database.Model):
    __tablename__ = 'workout_sessions'

    id = database.Column(database.Integer, primary_key=True)

    user_id = database.Column(
        database.Integer,
        database.ForeignKey('users.id'),
        nullable=False
    )

    duration_seconds = database.Column(database.Integer, nullable=True)
    calories_burned = database.Column(database.Integer, nullable=True)

    # ✅ NEW FIELD
    daily_steps = database.Column(database.Integer, nullable=True)

    created_at = database.Column(
        database.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<Workout {self.user_id} - {self.calories_burned} kcal - {self.daily_steps} steps>"
class WeeklyWorkoutPlan(database.Model):
    __tablename__ = 'weekly_workout_plans'

    id = database.Column(database.Integer, primary_key=True)

    user_id = database.Column(
        database.Integer,
        database.ForeignKey('users.id'),
        nullable=False,
        unique=True
    )

    monday = database.Column(database.String(100), nullable=False, default='Rest Day')
    tuesday = database.Column(database.String(100), nullable=False, default='Rest Day')
    wednesday = database.Column(database.String(100), nullable=False, default='Rest Day')
    thursday = database.Column(database.String(100), nullable=False, default='Rest Day')
    friday = database.Column(database.String(100), nullable=False, default='Rest Day')
    saturday = database.Column(database.String(100), nullable=False, default='Rest Day')
    sunday = database.Column(database.String(100), nullable=False, default='Rest Day')

    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    updated_at = database.Column(
        database.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<WeeklyWorkoutPlan user_id={self.user_id}>"

# -------------------------------
# HOME (Login Page)
# -------------------------------
@app.route('/')
def home():
    return render_template('login.html')

    
# OpenRouter Configuration
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

@app.route('/ai-coach', methods=['GET', 'POST'])
def ai_coach():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        user_input = request.json.get('message')
        
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a professional fitness coach."},
                        {"role": "user", "content": user_input}
                    ]
                })
            )
            
            res_json = response.json()

            # DEBUG: Terminal mein check karein ki kya response aaya
            print("OpenRouter Response:", res_json)

            if 'choices' in res_json:
                reply = res_json['choices'][0]['message']['content']
                return jsonify({"reply": reply})
            else:
                # Agar 'choices' nahi hai, toh OpenRouter ne error bheja hai
                error_info = res_json.get('error', {}).get('message', 'Unknown AI Error')
                return jsonify({"reply": f"AI Error: {error_info}"})
            
        except Exception as e:
            print(f"Server Error: {e}")
            return jsonify({"reply": "System busy. Try again!"}), 500

    return render_template('ai_coach.html', user=session['user_name'])


    

# -------------------------------
# LOGIN ROUTE
# -------------------------------
@app.route('/login', methods=['POST', 'GET'])
def login():
    email = request.form['email']
    password = request.form['password']

    # 🔥 SQLAlchemy Query (No cursor)
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        flash("Login Successful!", "success")

        # Store only required info in session
        session['user_id'] = user.id
        session['user_name'] = user.name

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
            flash("All fields are required!", "danger")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
        full_name = f"{first_name} {last_name}"

        new_user = User(
            name=full_name,
            dob=dob_date,
            email=email,
            password=hashed_password
        )

        database.session.add(new_user)
        database.session.commit()

        # ✅ AUTO LOGIN USING SESSION
        session['user_id'] = new_user.id
        session['user_name'] = new_user.name

        flash("Registration successful!", "success")
        return redirect(url_for('dashboard'))

    return render_template('register.html')
# -------------------------------
# DASHBOARD (After login)
# -------------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    # 🔒 Login Check
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))

    # Logged-in user fetch from DB
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        total_seconds = int(request.form.get('total_seconds', 0))
        total_calories = int(request.form.get('total_calories', 0))
        steps = int(request.form.get('steps', 0))

        print("Workout Time:", total_seconds)
        print("Calories Burned:", total_calories)
        print("Steps:", steps)

        # ✅ Save workout in database only seconds and burned calories are greater than 0
        if total_seconds > 0 and total_calories > 0:
            new_workout = WorkoutSession(
                user_id=user.id,
                duration_seconds=total_seconds,
                calories_burned=total_calories,
            )

            database.session.add(new_workout)
            database.session.commit()

        # ✅ Save steps in database
        if steps > 0:
            new_workout_steps = WorkoutSession(
                user_id=user.id,
                daily_steps=steps
            )

            database.session.add(new_workout_steps)
            database.session.commit()

        flash("Workout Saved Successfully!", "success")
        return redirect(url_for('dashboard'))

    # 🔥 Latest workout
    workout = WorkoutSession.query \
        .with_entities(WorkoutSession.calories_burned, WorkoutSession.duration_seconds) \
        .filter(
            WorkoutSession.user_id == user.id,
            WorkoutSession.calories_burned.is_not(None),
            WorkoutSession.duration_seconds.is_not(None)
        ) \
        .order_by(WorkoutSession.created_at.desc()) \
        .first()

    # 🔥 Latest steps
    daily_steps = WorkoutSession.query \
        .with_entities(WorkoutSession.daily_steps) \
        .filter(
            WorkoutSession.user_id == user.id,
            WorkoutSession.daily_steps.is_not(None)
        ) \
        .order_by(WorkoutSession.created_at.desc()) \
        .first()

    # 🔥 Weekly workout plan
    workoutplan = WeeklyWorkoutPlan.query.filter_by(user_id=user.id).first()

    today_day = datetime.now().strftime('%A').lower()
    today_workout = 'No Workout Plan'

    if workoutplan and hasattr(workoutplan, today_day):
        today_workout = getattr(workoutplan, today_day)

    return render_template(
        'dashboard.html',
        user=user,
        workout=workout,
        daily_steps=daily_steps,
        workoutplan=workoutplan,
        today_day=today_day.capitalize(),
        today_workout=today_workout
    )

@app.route('/startworkout')
def startworkout():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))
    return render_template('startworkout.html')    



# -------------------------------
# WORKOUTS PAGE (Protected)
# -------------------------------
@app.route('/workouts/gym/chest')
def chest_gym_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    return render_template('chest.html')

@app.route('/workouts/gym')
def gym_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    return render_template('gym.html')

@app.route('/workouts')
def workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    
    return render_template('workouts.html')

@app.route('/workouts/gym/chest')
def chest_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    
    return render_template('chest.html')

@app.route('/workouts/gym/shoulder')
def shoulder_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('shoulder.html')


@app.route('/workouts/gym/bicep')
def bicep_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('bicep.html')

@app.route('/workouts/gym/back')
def back_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('back.html')    

@app.route('/workouts/gym/leg')
def leg_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('leg.html')      

@app.route('/workouts/gym/abs')
def abs_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('abs.html')

@app.route('/workouts/gym/forearm')
def forearm_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('forearm.html')

@app.route('/workouts/calisthenic')
def calisthenic_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('calisthenic.html')

@app.route('/workouts/calisthenic/upperbody')
def upperbody_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('upperbody.html')

@app.route('/workouts/calisthenic/lowerbody')
def lowerbody_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('lowerbody.html')    

@app.route('/workouts/calisthenic/corepart')
def corepart_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('corepart.html')
   
@app.route('/workouts/calisthenic/fullbody')
def fullbody_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('fullbody.html')

@app.route('/workouts/homeworkout')
def homeworkout_workouts():
    if 'user_id' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))

    return render_template('homeworkout.html')   

# -------------------------------
# ADD WORKOUT ROUTE
# -------------------------------
@app.route('/add_workout', methods=['POST'])
def add_workout():
    if 'user_id' not in session:
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

@app.route('/testing')
def testing():
    return render_template('header.html')

@app.route('/testing2')
def testing2():
    return render_template('testing2.html')

# -------------------------------
# NUTRITION ROUTE
# -------------------------------

# @app.route('/cuttingg', methods=['GET', 'POST'])
# def cuttingg():
#     if 'user' not in session:
#         flash("Please login first", "warning")
#         return redirect(url_for('home'))

#     if request.method == 'POST':
#         try:
#             cursor.execute("""
#                 INSERT INTO nutrition 
#                 (user_id, weight, height, age, gender, activity, tdee)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             """, (
#                 session['user']['id'],
#                 request.form['weight'],
#                 request.form['height'],
#                 request.form['age'],
#                 request.form['gender'],
#                 request.form['activity']
#             ))
#             db.commit()
#             flash("Nutrition information saved!", "success")
#         except Exception as e:
#             flash(f"Error: {str(e)}", "error")
#         return redirect(url_for('caloriegoal'))
    
#     return render_template('cuttingg.html')


# @app.route('/')
# def cutting_page():
#     return render_template('cutting.html')


# @app.route('/cutting', methods=['POST'])
# def cutting():
#     data = request.get_json()
#     try:
#         weight = float(data['weight'])
#         height = float(data['height'])
#         age = int(data['age'])
#         gender = data['gender']
#         activity = float(data['activity'])
#         tdee = float(data['tdee'])

#         cursor.execute("""
#             INSERT INTO cutting_data (weight, height, age, gender, activity_level, tdee)
#             VALUES (%s, %s, %s, %s, %s, %s)
#         """, (weight, height, age, gender, activity, tdee))
#         db.commit()

#         flash(f"✅ TDEE saved successfully: {tdee:.0f} calories/day!", "success")
#         return jsonify({"status": "ok"})

#     except Exception as e:
#         print("Error:", e)
#         flash("⚠️ Failed to save data. Please try again.", "error")
#         return jsonify({"status": "error"})


# @app.route('/result')
# def result_page():
#     return render_template('cutting.html')




@app.route('/caloriegoal')
def caloriegoal():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))
    return render_template('caloriegoal.html')  

@app.route('/caloriegoal/cutting')
def cutting():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))
    return render_template('cutting.html')  

@app.route('/caloriegoal/bulking')
def bulking():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))
    return render_template('bulking.html')  

@app.route('/caloriegoal/maintenance')      
def maintenance():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))
    return render_template('maintenance.html') 

@app.route('/caloriegoal/tipsforsuccess')
def tipsforsuccess():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))
    return render_template('tips for success.html') 

    
@app.route('/caloriescalculator')
def caloriescalculator():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))
    return render_template('caloriescalculator.html')



@app.route('/profile', methods=['GET', 'POST'])
def profile():

    total_calories = {}
    ai_tips = None

    if request.method == 'POST':
        weight = request.form.get('weight')
        height = request.form.get('height')
        age = request.form.get('age')
        calories = request.form.get('calories')
        dietary_preference = request.form.get('dietary_preference')
        goal = request.form.get('goal')

        total_calories = {
            'weight': weight,
            'height': height,
            'age': age,
            'calories': calories,
            'dietary_preference': dietary_preference,
            'goal': goal
        }

        # 🔥 AI Prompt
        prompt = f"""
        You are a professional fitness and nutrition coach. 

        User Profile:
        - Weight: {weight} kg
        - Height: {height} cm
        - Age: {age} years
        - Daily Maintenance Calories: {calories}
        - Dietary Preference: {dietary_preference}
       - Fitness Goal: {goal}  # goal can be "cutting", "maintenance", or "bulking"

       Task:
       1. Provide personalized nutrition advice based on the user's goal.
       2. Suggest approximate daily calories for the goal.
    3. Give a protein intake recommendation (grams/day).
    4. Suggest one sample meal plan suitable for the goal and dietary preference.
    5. Format the output with clear headings:
    - Goal Summary
    - Calories Recommendation
    - Protein Recommendation
    - Sample Meal Plan

    Use concise, actionable advice suitable for someone following the specified goal.
    """
        OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a professional fitness and nutrition coach."},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        res_json = response.json()
        print("AI Response JSON:", res_json)

        if 'choices' in res_json:
            ai_tips = res_json['choices'][0]['message']['content']
        else:
            ai_tips = "AI tips unavailable."

    return render_template('profile.html',
                           total_calories=total_calories,
                           ai_tips=ai_tips)

@app.route('/info')
def info():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])

    return render_template('info.html', user=user)


from datetime import datetime
from werkzeug.utils import secure_filename
import os

@app.route('/update_info', methods=['POST'])
def update_info():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])

    name = request.form.get('name')
    dob = request.form.get('dob')
    file = request.files.get('profile_image')

    if user:

        if name:
            user.name = name

        if dob:
            user.dob = datetime.strptime(dob, "%Y-%m-%d").date()

        # ✅ PROFILE IMAGE UPLOAD
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Unique filename
            filename = f"user_{user.id}_{filename}"

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            user.profile_image = filename

        database.session.commit()
        flash("Profile updated successfully!", "success")

    return redirect(url_for('info'))
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))

    name = request.form.get('name')
    dob = request.form.get('dob')

    user = User.query.get(session['user_id'])

    if user:
        if name:
            user.name = name

        if dob:
            user.dob = datetime.strptime(dob, "%Y-%m-%d").date()

        database.session.commit()
        flash("Information updated successfully!", "success")

    return redirect(url_for('info'))


@app.route('/workoutplans', methods=['GET', 'POST'])
def workoutplans():
    if 'user_id' not in session:
        flash("Please login first", "warning")
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    plan = WeeklyWorkoutPlan.query.filter_by(user_id=user.id).first()

    if request.method == 'POST':
        if not plan:
            plan = WeeklyWorkoutPlan(user_id=user.id)

        plan.monday = request.form.get('monday', 'Rest Day')
        plan.tuesday = request.form.get('tuesday', 'Rest Day')
        plan.wednesday = request.form.get('wednesday', 'Rest Day')
        plan.thursday = request.form.get('thursday', 'Rest Day')
        plan.friday = request.form.get('friday', 'Rest Day')
        plan.saturday = request.form.get('saturday', 'Rest Day')
        plan.sunday = request.form.get('sunday', 'Rest Day')

        database.session.add(plan)
        database.session.commit()

        flash("Workout plan saved successfully!", "success")
        return redirect(url_for('workoutplans'))

    return render_template('workoutplans.html', user=user, plan=plan)

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
     with app.app_context():
        database.create_all()
        app.run(debug=True)