from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import time

app = Flask(__name__, template_folder='templates')
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

# Load delivery data from JSON file
def load_deliveries():
    try:
        with open('deliveries.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save delivery data to JSON file
def save_deliveries(deliveries):
    with open('deliveries.json', 'w') as f:
        json.dump(deliveries, f, indent=4)


def format_timestamp(timestamp):
    """Formats a timestamp (integer) into a human-readable string."""
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

app.jinja_env.globals['format_timestamp'] = format_timestamp
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard_redirect'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect(url_for('dashboard_redirect'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        users = load_users()

        if any(user['email'] == email for user in users):
            flash('Email already exists. Please use a different email.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        new_user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': user_type
        }
        users.append(new_user)
        save_users(users)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard_redirect'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = load_users()
        user_found = None
        for user in users:
            if user['email'] == email:
                user_found = user
                break

        if user_found and check_password_hash(user_found['password'], password):
            session['logged_in'] = True
            session['email'] = user_found['email']
            session['role'] = user_found['role']
            flash(f'Welcome back, {user_found["name"]}!', 'success')
            return redirect(url_for('dashboard_redirect'))

        flash('Invalid email or password.', 'danger')
        return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

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
    if not ('logged_in' in session and session['role'] == 'customer'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    deliveries = load_deliveries()
    customer_deliveries = [d for d in deliveries if d.get('customer_email') == session['email']]
    return render_template('customer_dashboard.html', email=session['email'], customer_deliveries=customer_deliveries)

@app.route('/driver_dashboard')
def driver_dashboard():
    if not ('logged_in' in session and session['role'] == 'driver'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('driver_dashboard.html', email=session['email'])

@app.route('/create_delivery', methods=['GET', 'POST'])
def create_delivery():
    if not ('logged_in' in session and session['role'] == 'customer'):
        flash('Only customers can create delivery requests.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        pickup_address = request.form['pickup_address']
        dropoff_address = request.form['dropoff_address']
        package_note = request.form['package_note']
        customer_email = session['email']
        timestamp = int(time.time())

        deliveries = load_deliveries()

        new_delivery_id = (deliveries[-1]['id'] + 1) if deliveries else 1

        new_delivery = {
            'id': new_delivery_id,
            'customer_email': customer_email,
            'pickup_address': pickup_address,
            'dropoff_address': dropoff_address,
            'package_note': package_note,
            'status': 'Pending',
            'timestamp': timestamp,
            'assigned_driver': None,
            'rating': None,
            'comment': None
        }
        deliveries.append(new_delivery)
        save_deliveries(deliveries)

        flash('Delivery request created successfully!', 'success')
        return redirect(url_for('customer_dashboard'))

    return render_template('create_delivery.html')

@app.route('/pending_deliveries')
def pending_deliveries():
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))
    
    deliveries = load_deliveries()
    pending = [d for d in deliveries if d['status'] == 'Pending']
    pending.sort(key=lambda x: x['timestamp'], reverse=True)
    return render_template('pending_deliveries.html', pending_deliveries=pending)

@app.route('/accept_delivery/<int:delivery_id>')
def accept_delivery(delivery_id):
    if not ('logged_in' in session and session['role'] == 'driver'):
        flash('Only drivers can accept deliveries.', 'warning')
        return redirect(url_for('login'))

    deliveries = load_deliveries()
    delivery_to_accept = next((d for d in deliveries if d['id'] == delivery_id), None)

    if delivery_to_accept is None:
        flash(f'Delivery #{delivery_id} not found.', 'danger')
        return redirect(url_for('pending_deliveries'))

    if delivery_to_accept['status'] == 'Pending':
        delivery_to_accept['status'] = 'Accepted'
        delivery_to_accept['assigned_driver'] = session['email']
        save_deliveries(deliveries)
        flash(f'Delivery #{delivery_id} has been accepted.', 'success')
    else:
        flash(f'Delivery #{delivery_id} was already accepted by another driver.', 'warning')

    return redirect(url_for('pending_deliveries'))

@app.route('/my_deliveries')
def my_deliveries():
    if not ('logged_in' in session and session['role'] == 'driver'):
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    deliveries = load_deliveries()
    driver_deliveries = [d for d in deliveries if d.get('assigned_driver') == session['email']]
    return render_template('my_deliveries.html', my_deliveries=driver_deliveries)

@app.route('/delivery_details/<int:delivery_id>')
def delivery_details(delivery_id):
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    deliveries = load_deliveries()
    delivery = next((d for d in deliveries if d['id'] == delivery_id), None)

    if delivery is None:
        flash('Delivery not found.', 'danger')
        return redirect(url_for('dashboard_redirect'))

    is_customer = session['email'] == delivery['customer_email']
    is_assigned_driver = delivery.get('assigned_driver') == session.get('email')
    is_any_driver_for_pending = session.get('role') == 'driver' and delivery.get('status') == 'Pending'
    
    if not (is_customer or is_assigned_driver or is_any_driver_for_pending):
        flash('You are not authorized to view these delivery details.', 'danger')
        return redirect(url_for('dashboard_redirect'))

    return render_template('delivery_details.html', delivery=delivery)

@app.route('/profile')
def profile():
    if 'logged_in' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))

    deliveries = load_deliveries()
    user_email = session['email']
    user_deliveries = []

    if session['role'] == 'customer':
        user_deliveries = [d for d in deliveries if d.get('customer_email') == user_email]
    elif session['role'] == 'driver':
        user_deliveries = [d for d in deliveries if d.get('assigned_driver') == user_email and d.get('status') == 'Delivered']

    return render_template('profile.html', user_deliveries=user_deliveries)

@app.route('/submit_feedback/<int:delivery_id>', methods=['POST'])
def submit_feedback(delivery_id):
    if not ('logged_in' in session and session['role'] == 'customer'):
        flash('Only customers can submit feedback.', 'warning')
        return redirect(url_for('login'))

    deliveries = load_deliveries()
    delivery_to_update = next((d for d in deliveries if d['id'] == delivery_id), None)

    if (delivery_to_update is None or
            delivery_to_update.get('customer_email') != session['email'] or
            delivery_to_update.get('status') != 'Delivered' or
            delivery_to_update.get('rating') is not None):
        flash('Feedback cannot be submitted for this delivery.', 'danger')
        return redirect(url_for('delivery_details', delivery_id=delivery_id))

    try:
        rating = int(request.form.get('rating'))
        if not (1 <= rating <= 5):
            flash('Invalid rating. Please select a value from 1 to 5.', 'danger')
            return redirect(url_for('delivery_details', delivery_id=delivery_id))

        delivery_to_update['rating'] = rating
        delivery_to_update['comment'] = request.form.get('comment', '').strip()[:200]
        save_deliveries(deliveries)
        flash('Thank you for your feedback!', 'success')

    except (ValueError, TypeError):
        flash('Invalid rating provided. Please select a value from 1 to 5.', 'danger')

    return redirect(url_for('delivery_details', delivery_id=delivery_id))

@app.route('/update_delivery_status/<int:delivery_id>', methods=['POST'])
def update_delivery_status(delivery_id):
    if not ('logged_in' in session and session['role'] == 'driver'):
        flash('Only drivers can update delivery status.', 'warning')
        return redirect(url_for('login'))

    new_status = request.form.get('new_status')
    deliveries = load_deliveries()
    delivery_to_update = next((d for d in deliveries if d['id'] == delivery_id), None)

    if delivery_to_update is None:
        flash('Delivery not found.', 'danger')
        return redirect(url_for('driver_dashboard'))

    if delivery_to_update.get('assigned_driver') != session['email']:
        flash('You are not authorized to update this delivery.', 'danger')
        return redirect(url_for('driver_dashboard'))

    allowed_transitions = {
        'Accepted': ['In Transit'],
        'In Transit': ['Delivered']
    }
    current_status = delivery_to_update['status']

    if current_status in allowed_transitions and new_status in allowed_transitions[current_status]:
        delivery_to_update['status'] = new_status
        save_deliveries(deliveries)
        flash(f'Status for delivery #{delivery_id} updated to "{new_status}".', 'success')
    else:
        flash(f'Invalid status transition from "{current_status}" to "{new_status}".', 'danger')

    return redirect(url_for('delivery_details', delivery_id=delivery_id))

if __name__ == '__main__':
    app.run(debug=True, port=5000)