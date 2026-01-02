# Next Bus Backend

Next Bus Backend is a RESTful API service built with FastAPI to provide real-time bus arrival information. It is designed to serve as the backend for the Next Bus application, supporting features such as route lookup, stop times, and live bus tracking.

## Features

- FastAPI-powered REST API
- Real-time and scheduled bus arrival data
- Endpoints for routes, stops, and live tracking
- Easy to extend and integrate

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn (for running the server)
- Any other dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Sourish-Kanna/Next-Bus-Backend.git
    cd next-bus-backend
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

Start the development server with:

```bash
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## Usage

- Access the interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs)
- Use the available endpoints to query bus routes, stops, and arrival times.

## Project Structure

``` text
next-bus-backend/
├── main.py
├── v1/
│   ├── auth.py
│   ├── firebase.py
|   ├── test.py
│   └── __init__.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements and bug fixes.

## Environment setup

This project uses environment variables for configuration. It uses `FIREBASE_CREDENTIALS_JSON` (stringified JSON) for Firebase service account credentials.

Key environment variables you might set locally or in your host provider (e.g., Render):

- `DEV_ENV` - Set to `true` to load `dev.env` locally. When `DEV_ENV` is not `true`, the app will not load `dev.env` automatically.
- `ORIGIN_LIST` - Comma-separated list of allowed CORS origins. Use `*` to allow any origin (not recommended for production).
- `FIREBASE_CREDENTIALS_JSON` - JSON contents of the Firebase service account, provided when file path is not available.
- `FIREBASE_WEB_API_KEY` - Firebase web API key for client-side interactions (dev only).
- `FIREBASE_TEST_USER_ID` - Optional dev-only test user ID.

Local development example: copy `.env.example` to `dev.env`, fill in values, and set `DEV_ENV=true` to have the application load it. Do not commit `dev.env` or any private key files to the repository. Place credentials in a secure store when deploying (Render/GCP/Github Secrets).
