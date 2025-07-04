# QuickDeliver Lite

QuickDeliver Lite is a simple web application for managing package deliveries. It serves as a lightweight courier service platform connecting customers who need packages delivered with drivers who can perform the deliveries. The application supports two user roles: Customer and Driver, each with a dedicated dashboard and functionalities.

The project is built with Python using the Flask web framework and uses JSON files for data storage. The front-end is styled with Bootstrap 5 for a clean and responsive user interface.

## Key Features

*   **User Authentication:** Secure user registration and login for both customers and drivers.
*   **Role-Based Access Control:**
    *   **Customers:** Can create new delivery requests, view the status of their deliveries, and provide feedback (rating and comments) upon completion.
    *   **Drivers:** Can view pending delivery requests, accept them, update the delivery status (Accepted -> In Transit -> Delivered), and view feedback on their completed deliveries.
*   **Delivery Management:**
    *   Create, view, and manage delivery requests.
    *   Real-time status updates for deliveries.
    *   Detailed view for each delivery.
*   **Feedback System:** Customers can rate and comment on a driver's service after a delivery is completed.
*   **Responsive UI:** A clean, mobile-friendly interface built with Bootstrap 5.
*   **User Feedback:** Flash messages provide clear feedback to users after performing actions.

## Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kirito-sao62/QuickDeliver-Lite.git
    cd QuickDeliver-Lite
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```

5.  Open your web browser and navigate to `http://127.0.0.1:5000`.

## Known Bugs or Limitations

*   **Data Persistence:** The application uses JSON files (`users.json`, `deliveries.json`) as a database. This is not suitable for a production environment due to potential race conditions and performance issues. A proper database like SQLite, PostgreSQL, or MySQL should be used for a real-world application.
*   **Simple ID Generation:** Delivery IDs are generated by incrementing the last known ID, which is not robust.
*   **No Real-time Updates:** The pages need to be manually refreshed to see status changes.
