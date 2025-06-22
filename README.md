# QuickDeliver Lite

This is a simplified, real-time delivery management system built as part of an internship project. It's designed to function like a lightweight logistics platform, simulating real-world development step by step.

## Getting Started

## Week 1: Authentication System

This week's focus is on building the core authentication system, including user registration, login, and logout, with support for two user roles: Customer and Driver.

### Features Implemented:

*   **User Registration:** Users can register with their name, email, password, and specify their user type (Customer or Driver).
*   **Unique Email Enforcement:** Prevents duplicate registration attempts with the same email address.
*   **Secure Password Handling:** Passwords are securely hashed before being stored.
*   **User Login:** Authenticates users based on their registered email and password.
*   **User Logout:** Clears session data to log out the user.
*   **Session Management:** User's role and identity are persisted during active sessions.
*   **Role-Based Access Control:** Basic access control is implemented to restrict users to relevant parts of the application based on their role (e.g., separate dashboards for customers and drivers).
*   **Basic UI with Bootstrap:** The user interface for registration, login, and dashboards is styled using Bootstrap.

### Technologies Used (Week 1):

*   **Backend:** Python (Flask)
*   **Frontend:** HTML, Bootstrap
*   **Data Storage:** JSON file (for user data - initial implementation)

### Setup and Installation:

1.  **Clone the repository:** If you have the project on GitHub, clone it to your local machine. If you are setting it up locally for the first time, create a project directory and save the project files (`/app.py`, `/users.json`, `/templates/`, `/static/` if applicable) inside it.
2.  **Create a virtual environment (Recommended):**
