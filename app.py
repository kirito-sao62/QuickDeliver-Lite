from flask import Flask, render_template, request, redirect, url_for, session
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key' # Replace with a strong secret key

# Load user data from JSON file
def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save user data to JSON file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect(url_for('dashboard_redirect')) # Redirect logged-in users

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        users = load_users()

        # Check for duplicate email
        for user in users:
            if user['email'] == email:
                return "Email already exists. Please use a different email." # Or render the registration page again with an error message

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Add new user
        new_user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': user_type
        }
        users.append(new_user)
        save_users(users)

        return redirect(url_for('login')) # Redirect to login page after successful registration

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard_redirect')) # Redirect logged-in users

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = load_users()

        # Check if the user exists and the password is correct
        for user in users:
            if user['email'] == email and check_password_hash(user['password'], password):
                # Store user information in the session
                session['logged_in'] = True
                session['email'] = user['email']
                session['role'] = user['role']
                return redirect(url_for('dashboard_redirect')) # Redirect to the appropriate dashboard

        return "Invalid email or password." # Or render the login page again with an error message

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Clear all session data
    return redirect(url_for('login')) # Redirect to the login page

@app.route('/dashboard_redirect')
def dashboard_redirect():
    if 'logged_in' in session:
        if session['role'] == 'customer':
            return redirect(url_for('customer_dashboard'))
        elif session['role'] == 'driver':
            return redirect(url_for('driver_dashboard'))
    return redirect(url_for('login'))

@app.route('/customer_dashboard')
def customer_dashboard():
    if 'logged_in' in session and session['role'] == 'customer':
        return f"Welcome, Customer {session['email']}!<br><a href='{url_for('logout')}'>Logout</a>"
    else:
        return redirect(url_for('login'))

@app.route('/driver_dashboard')
def driver_dashboard():
    if 'logged_in' in session and session['role'] == 'driver':
        return f"Welcome, Driver {session['email']}!<br><a href='{url_for('logout')}'>Logout</a>"
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)