# Next Bus Backend ⚙️

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-black?logo=fastapi)
[![Deploy on Render](https://img.shields.io/badge/Deploy-Render-black?logo=render)](https://render.com)

> **The backend service powering the offline-first Next Bus ecosystem.**

**Next Bus Backend** is a REST API built with **FastAPI** that supports the Next Bus mobile application.
Its primary responsibility is to **accept, validate, and persist crowdsourced transit data** while enforcing basic data-quality rules.

This repository exists mainly as a **supporting service** for the frontend, but it is also intentionally designed to demonstrate **backend system design, API discipline, and cost-aware engineering**.

---

## 📖 Context

> *Crowdsourced data is only useful if you can trust it.*

The frontend handles offline usage and UX.
The backend solves the **data integrity problem**:

* Who is allowed to write?
* How often can updates be sent?
* How do you prevent accidental or malicious spam without heavy infrastructure?

This service goes beyond simple CRUD by embedding **business rules directly into the API layer**.

---

## ✨ Features

### Core API Capabilities

* **Public Read APIs** — Fetch routes and timings without authentication
* **Authenticated Writes** — Reporting and modifications require Firebase login
* **Role-Based Access Control**

  * **Admins:** Manage routes and metadata
  * **Users:** Submit timing updates
* **Offline Client Sync Support** — Accepts delayed, batched updates

### Data Integrity Controls

* **Logic-Based Rate Limiting**

  * Enforces **1 update per user per route per minute**
  * Violations return **HTTP 429**
  * Idempotency handling is planned but not yet implemented
* **Strict Request Validation**

  * All payloads validated using Pydantic models

---

## 🧠 Engineering Highlights

### 1. Rate Limiting Without External Infrastructure

Instead of Redis or API gateways, rate limiting is implemented directly in application logic:

* Last update timestamps are checked in Firestore
* Requests exceeding limits are rejected early
* Keeps architecture simple and cloud costs low

This approach is intentional for a **low-traffic, cost-constrained system**.

---

### 2. Offline-First Friendly API Design

The backend is tolerant of:

* Delayed updates
* Batched writes
* Reordered submissions

This complements the frontend’s offline queue and sync engine.

---

### 3. Future-Ready Data Storage

While no ML models are currently active:

* Raw timing data is stored in a way that supports **future analysis or prediction**
* Schema decisions avoid locking into premature assumptions

---

## 🧑‍💼 What This Backend Demonstrates

This repository demonstrates:

* **API design with real constraints**
* **Authentication & RBAC using Firebase**
* **Backend business-logic enforcement**
* **Cost-aware architectural decisions**
* **Clear separation of concerns (frontend vs backend)**

It is intentionally **not over-engineered**.

---

## 🏗 Tech Stack

### Core

* **Python 3.10+**
* **FastAPI**
* **Uvicorn** (ASGI server)

### Cloud & Data

* **Firebase Authentication**
* **Google Cloud Firestore**
* **Render** (separate dev & stable services)

🔗 Frontend Repository
[https://github.com/Sourish-Kanna/Next-Bus-Frontend](https://github.com/Sourish-Kanna/Next-Bus-Frontend)

---

## 📡 API Overview

### Public (No Auth)

| Method | Endpoint                   | Description                |
| ------ | -------------------------- | -------------------------- |
| `GET`  | `/v1/route/routes`         | Fetch all available routes |
| `GET`  | `/v1/timings/{route_name}` | Get timings for a route    |

### Authenticated (Firebase ID Token)

| Method | Endpoint                    | Description                 | Role  |
| ------ | --------------------------- | --------------------------- | ----- |
| `PUT`  | `/v1/timings/update`        | Submit a bus arrival update | User  |
| `POST` | `/v1/route/add`             | Add a new route             | Admin |
| `GET`  | `/v1/user/get-user-details` | Fetch user role & metadata  | User  |

> Interactive Swagger docs are available at `/docs` when running locally.

---

## 🚀 Getting Started (Developers)

### Prerequisites

* Python 3.8+
* Firebase project with Firestore enabled
* Firebase service account credentials

---

### Setup

1. **Clone the repository**

```bash
git clone https://github.com/Sourish-Kanna/Next-Bus-Backend.git
cd Next-Bus-Backend
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Configure environment**

Create `dev.env` (see `.env.example`):

```env
DEV_ENV=true
FIREBASE_CREDENTIALS_JSON='{...service account json...}'
ORIGIN_LIST=*
```

> Do not commit secrets. Use secure environment variables in deployment.

1. **Run locally**

```bash
uvicorn --app-dir src main:app --reload
```

API will be available at `http://127.0.0.1:8000`.

---

## 🌿 Deployment

* Hosted on **Render**
* Separate services for:

  * **Development**
  * **Stable**
* API versioning uses `/v1` (contract may evolve)

---

## ⚠️ Disclaimer

* This backend is intended for **community and demonstration use**
* Rate limits are enforced
* No uptime or SLA guarantees are provided

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Open a Pull Request

---

## 📄 License

**MIT License**
*(subject to final confirmation)*

---

<div align="center">
  <small>The engine behind the commute.</small>
</div>