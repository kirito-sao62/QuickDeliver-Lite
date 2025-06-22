from flask import Flask, render_template, request, redirect, url_for, session
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
                return render_template('register.html', error='Email already exists. Please use a different email.')

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

        return render_template('login.html', error='Invalid email or password.')

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
    if not ('logged_in' in session and session['role'] == 'customer'):
        return redirect(url_for('login'))
    
    deliveries = load_deliveries()
    customer_deliveries = [d for d in deliveries if d.get('customer_email') == session['email']]
    return render_template('customer_dashboard.html', email=session['email'], customer_deliveries=customer_deliveries)

@app.route('/driver_dashboard')
def driver_dashboard():
    if not ('logged_in' in session and session['role'] == 'driver'):
        return redirect(url_for('login'))
    
    return render_template('driver_dashboard.html', email=session['email'])

@app.route('/create_delivery', methods=['GET', 'POST'])
def create_delivery():
    if not ('logged_in' in session and session['role'] == 'customer'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        pickup_address = request.form['pickup_address']
        dropoff_address = request.form['dropoff_address']
        package_note = request.form['package_note']
        customer_email = session['email']
        timestamp = int(time.time()) # Timestamp in seconds

        deliveries = load_deliveries()

        # Generate a simple unique ID (incrementing)
        if deliveries:
            new_delivery_id = deliveries[-1]['id'] + 1
        else:
            new_delivery_id = 1

        new_delivery = {
            'id': new_delivery_id,
            'customer_email': customer_email,
            'pickup_address': pickup_address,
            'dropoff_address': dropoff_address,
            'package_note': package_note,
            'status': 'Pending',
            'timestamp': timestamp
        }
        deliveries.append(new_delivery)
        save_deliveries(deliveries)

        return redirect(url_for('customer_dashboard')) # Redirect to customer dashboard after creating

    return render_template('create_delivery.html')

@app.route('/pending_deliveries')
def pending_deliveries():
    if not 'logged_in' in session:
        return redirect(url_for('login'))
    
    deliveries = load_deliveries()
    pending = [d for d in deliveries if d['status'] == 'Pending']
    pending.sort(key=lambda x: x['timestamp'], reverse=True) # Sort by timestamp newest first
    return render_template('pending_deliveries.html', pending_deliveries=pending)

@app.route('/accept_delivery/<int:delivery_id>')
def accept_delivery(delivery_id):
    # Ensure only logged-in drivers can accept deliveries
    if not ('logged_in' in session and session['role'] == 'driver'):
        return redirect(url_for('login'))

    deliveries = load_deliveries()
    delivery_to_accept = None

    # Find the delivery with the given ID
    for delivery in deliveries:
        if delivery['id'] == delivery_id:
            delivery_to_accept = delivery
            break

    # Handle the case where the delivery ID is not found
    if delivery_to_accept is None:
        # Optionally, flash a message or render an error page
        return redirect(url_for('pending_deliveries'))

    # Implement race condition check: Only accept if the status is still 'Pending'
    if delivery_to_accept['status'] == 'Pending':
        delivery_to_accept['status'] = 'Accepted'
        delivery_to_accept['assigned_driver'] = session['email'] # Assign driver's email
        save_deliveries(deliveries)
        # Optionally, flash a success message
    else:
        # Handle race condition: Another driver accepted it already
        # Optionally, flash a message informing the driver
        pass

    # Redirect back to the pending deliveries page or a success page
    return redirect(url_for('pending_deliveries'))

@app.route('/my_deliveries')
def my_deliveries():
    # Ensure only logged-in drivers can view their accepted deliveries
    if not ('logged_in' in session and session['role'] == 'driver'):
        return redirect(url_for('login'))

    deliveries = load_deliveries()
    driver_deliveries = [d for d in deliveries if d.get('assigned_driver') == session['email']]
    return render_template('my_deliveries.html', my_deliveries=driver_deliveries)

@app.route('/delivery_details/<int:delivery_id>')
def delivery_details(delivery_id):
    # Ensure user is logged in
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    deliveries = load_deliveries()
    delivery = None

    # Find the delivery by ID
    for d in deliveries:
        if d['id'] == delivery_id:
            delivery = d
            break

    # Handle case where delivery is not found
    if delivery is None:
        # Optionally, flash a message or render an error page
        return redirect(url_for('dashboard_redirect')) # Redirect to dashboard if delivery not found

    # Access control: Only the customer who created the delivery or the assigned driver can view details
    # Also allow any driver to view pending deliveries
    allowed_to_view = session['email'] == delivery['customer_email'] or \
                      (session.get('role') == 'driver' and (delivery.get('assigned_driver') == session['email'] or delivery.get('status') == 'Pending'))
    if not allowed_to_view:
        # Optionally, flash a message indicating unauthorized access
        return redirect(url_for('dashboard_redirect'))

    return render_template('delivery_details.html', delivery=delivery)

@app.route('/update_delivery_status/<int:delivery_id>', methods=['POST'])
def update_delivery_status(delivery_id):
    # Ensure only logged-in drivers can update status
    if not ('logged_in' in session and session['role'] == 'driver'):
        return redirect(url_for('login'))

    new_status = request.form.get('new_status')

    deliveries = load_deliveries()
    delivery_to_update = None

    # Find the delivery with the given ID
    for delivery in deliveries:
        if delivery['id'] == delivery_id:
            delivery_to_update = delivery
            break

    # Handle the case where the delivery ID is not found
    if delivery_to_update is None:
        # Optionally, flash a message
        return redirect(url_for('driver_dashboard'))

    # Access control: Only the assigned driver can update the status
    if delivery_to_update.get('assigned_driver') != session['email']:
        # Optionally, flash a message indicating unauthorized access
        return redirect(url_for('driver_dashboard'))

    # Enforce valid status transitions
    allowed_transitions = {
        'Accepted': 'In Transit',
        'In Transit': 'Delivered'
    }

    if delivery_to_update['status'] in allowed_transitions and allowed_transitions[delivery_to_update['status']] == new_status:
        delivery_to_update['status'] = new_status
        save_deliveries(deliveries)
        # Optionally, flash a success message
    else:
        # Optionally, flash a message indicating invalid status transition
        pass

    return redirect(url_for('delivery_details', delivery_id=delivery_id)) # Redirect back to delivery details

if __name__ == '__main__':
    app.run(debug=True)