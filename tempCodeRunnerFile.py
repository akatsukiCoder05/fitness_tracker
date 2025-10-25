@app.route('/workouts/gym')
def gym_workouts():
    if 'user' not in session:
        flash("Please login to access workouts", "warning")
        return redirect(url_for('home'))
    return render_template('gym.html')