# Next Bus Backend ⚙️

The robust REST API powering the **Next Bus** application. Built with **FastAPI** and **Firebase**, this service handles crowdsourced transit data, user authentication, and route management with a focus on data integrity and scalability.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)

## 🚀 Features

### Core API Capabilities

* **Route Management:** Full CRUD (Create, Read, Update, Delete) endpoints for Bus Routes and Stops.
* **Real-Time Updates:** Handles live timing reports from users in the field.
* **Authentication:** Secure user verification using Firebase Auth (Bearer Tokens).
* **Role-Based Access (RBAC):**
  * **Admins:** Full access to modify routes and schedules.
  * **Users:** Can report live timings.
  * **Guests:** Read-only access to view schedules.

### Engineering & Security

* **Logic-Based Rate Limiting:** Prevents data spam by enforcing a "1 update per user per minute" rule on specific routes. This ensures high-quality crowdsourced data.
* **Cost-Optimized Logging:**
  * **Standard Logs:** Streamed to stdout (Cloud Logging) to stay within free tiers.
  * **Audit Trails:** Critical actions (Admin access, Rate Limit warnings) are securely logged to Firestore for auditing.
* **ML Data Pipeline:** Raw arrival data is preserved in a dedicated `historicalData` collection to train future Arrival Prediction Models.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Database:** Google Cloud Firestore (NoSQL)
* **Hosting:** Render (via `render.yaml`)
* **Authentication:** Firebase Auth

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Role |
| :--- | :--- | :--- | :--- |
| `GET` | `/v1/route/routes` | Get all available routes | Public |
| `POST` | `/v1/route/add` | Create a new bus route | Admin |
| `PUT` | `/v1/timings/update` | Report a bus arrival | User |
| `GET` | `/v1/user/get-user-details` | Fetch profile & permissions | User |

---

## 🚀 Getting Started

### Prerequisites

* Python 3.8+
* A Firebase Project with Firestore enabled.

### Installation

1. **Clone the repo**

    ```bash
    git clone [https://github.com/Sourish-Kanna/Next-Bus-Backend.git](https://github.com/Sourish-Kanna/Next-Bus-Backend.git)
    cd next-bus-backend
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Environment Setup**
    Create a `.env` file (or set environment variables):

    ```ini
    DEV_ENV=true
    FIREBASE_CREDENTIALS_JSON='{"type": "service_account", ...}'
    ```

4. **Run Locally**

    ```bash
    uvicorn main:app --reload
    ```

    The API will be available at `http://127.0.0.1:8000`.

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📬 Connect

[Your Name] - [LinkedIn Profile Link]
