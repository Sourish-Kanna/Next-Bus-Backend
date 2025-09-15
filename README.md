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

## License

This project is licensed under the MIT License.
