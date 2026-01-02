# Next Bus Backend ⚙️

[![Build Status](https://github.com/Sourish-Kanna/Next-Bus-Backend/actions/workflows/test.yml/badge.svg)](https://github.com/Sourish-Kanna/Next-Bus-Backend/actions)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688?logo=fastapi)
[![Deploy to Render](https://img.shields.io/badge/Deploy%20on-Render-black?logo=render)](https://render.com)

> **The intelligent, cost-optimized REST API powering the offline-first Next Bus ecosystem.**

**Next Bus Backend** is a high-performance REST API built with **FastAPI** that handles crowdsourced transit data. It doesn't just store data; it actively protects data integrity through logic-based rate limiting and serves as the synchronization hub for offline-first clients.

---

## 📖 The Context

> *Handling crowdsourced data requires trust, not just a database.*

While the frontend handles the offline experience, the backend solves the **"Trust Problem"**.
How do you allow the community to report bus timings without allowing spam or bad actors to corrupt the dataset?
This backend was engineered to answer that question, moving beyond simple CRUD operations to implement **business logic** that safeguards data quality while keeping cloud costs low.

---

## ✨ Features

### 🔌 Core API Capabilities

* **Real-time Synchronization** — Handles batched uploads from offline clients
* **Role-Based Access Control (RBAC)** — Distinct permissions for Admins, Users, and Guests
* **Route Management** — Dynamic creation and modification of transit routes
* **Live Updates** — Processes user-reported timings instantly

### 🛡️ Security & Integrity

* **Logic-Based Rate Limiting** — Prevents data spam (1 update/user/min)
* **Bearer Token Auth** — Secure verification via Firebase Admin SDK
* **Input Validation** — Strict Pydantic models for all requests

---

## 🧠 Engineering Highlights

### 1. Smart Rate Limiting (Without Redis)
To keep the architecture simple and cost-effective, I implemented a custom rate-limiting layer directly within the business logic.
* Checks the `lastUpdatedBy` timestamp in Firestore before accepting writes.
* Rejects spam attempts with `429 Too Many Requests` without needing expensive middleware.

### 2. Cost-Optimized Observability
Logging strategy designed for the free tier constraints of a student project:
* **Standard Traffic:** Logs to stdout (Cloud Logging) — *Zero Cost*.
* **Security Audits:** Critical actions (Admin access, Rate Limit hits) are written to Firestore (`systemLogs`) — *Persistent Audit Trail*.
* **ML Pipeline:** Raw data is separated into `historicalData` for future Arrival Prediction Models.

---

## 🧑‍💼 Why This Project Matters (For Recruiters)

This is not just a wrapper around Firebase.

It demonstrates:
* **Backend System Design** — Balancing security, cost, and performance.
* **Fiscal Responsibility** — Engineering decisions made to minimize cloud spend.
* **Data Pipeline Design** — Preparing data structures for future ML/AI use cases.
* **API Security** — Implementing RBAC and rate limiting from scratch.

---

## 🏗 Tech Stack

### Core
* **Python 3.10+**
* **FastAPI** — High-performance async framework
* **Uvicorn** — ASGI Server

### Data & Cloud
* **Google Cloud Firestore** — NoSQL Database
* **Firebase Authentication** — Identity Management
* **Render** — Cloud Hosting (Infrastructure as Code via `render.yaml`)

🔗 Frontend Repository:
[https://github.com/Sourish-Kanna/Next-Bus-Frontend](https://github.com/Sourish-Kanna/Next-Bus-Frontend)

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/v1/route/routes` | Fetch all active bus routes | Public |
| `PUT` | `/v1/timings/update` | Submit a new bus arrival time | User |
| `POST` | `/v1/route/add` | Create a new route configuration | Admin |
| `GET` | `/v1/user/get-user-details` | Fetch profile & permissions | User |

> *Full interactive documentation available at `/docs` (Swagger UI) when running locally.*

---

## 🚀 Getting Started (Developers)

### Prerequisites
* Python 3.8+
* Firebase Service Account (`google-services.json` equivalent)

### Setup

1. **Clone the repo**
   ```bash
   git clone [https://github.com/Sourish-Kanna/Next-Bus-Backend.git](https://github.com/Sourish-Kanna/Next-Bus-Backend.git)
   cd Next-Bus-Backend

```

1. **Install Dependencies**

```bash
pip install -r requirements.txt

```

1. **Configure Environment**
Create a `.env` file:

```env
DEV_ENV=true
FIREBASE_CREDENTIALS_JSON='{...your_service_account_key...}'

```

1. **Run Server**

```bash
uvicorn main:app --reload

```

---

## ⚠️ Disclaimer

* This API is for **demonstration and community use**.
* **Rate limits are active** to prevent abuse.
* No SLA is guaranteed for the hosted instance.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch
3. Open a Pull Request

---

## 📄 License

**MIT License**

---

<div align="center">
<small>The engine behind the commute.</small>
</div>
