# Testing Guide for Next Bus Backend

Welcome to the testing guide! If you are new to testing, don't worry—this document will walk you through the basics of why we test our code, how to set it up, and how to write your own tests.

## 🧪 What is Testing and Why Do We Do It?

Testing is the process of writing code that checks if your main application code is working as expected. Think of it as a spell-checker or a grammar-checker for your code.

**Why is testing important?**
- **Catches bugs early:** Tests help you find mistakes before your code goes live to real users.
- **Makes changing code safer:** When you add new features or fix bugs, running your tests ensures you didn't accidentally break something else.
- **Serves as documentation:** Well-written tests show other developers (and your future self!) exactly how a piece of code is supposed to be used.

In Python, one of the most popular and easiest tools to write tests with is called **`pytest`**. We use `pytest` in this project.

---

## 🛠️ How to Set Up and Run Tests Locally

### Step 1: Install Testing Dependencies
To run tests, you need to install the extra tools required for development and testing. These are listed in the `requirements-dev.txt` file.

Open your terminal, make sure you are in the root directory of the project, and run:

```bash
pip install -r requirements-dev.txt
```
*(This will install tools like `pytest`, `pytest-env`, and a tool called `TestClient` used to test web endpoints).*

### Step 2: Run the Tests
We have pre-configured `pytest` to know where to find your tests. To run all the tests in your project, simply run:

```bash
pytest
```

If everything is working correctly, you will see a bunch of green dots and a message like `2 passed in 1.25s`. If a test fails, `pytest` will show you exactly where and why it failed so you can fix it.

---

## 📖 Understanding Our Tests

All of our tests are located in the `tests/` directory.

### Example: Testing an Endpoint
If you look inside `tests/test_main.py`, you'll see a basic test for our main API endpoint.

Here is how a typical test is structured:
1. **Setup:** We import our FastAPI app and wrap it in a `TestClient`. The `TestClient` acts like a fake web browser that we can use to make requests to our app without actually starting a real web server.
2. **Action:** We make a request to the app, for example: `response = client.get("/")`.
3. **Assertion:** We use the `assert` keyword to check if the result is what we expected. If the assertion is `True`, the test passes. If it is `False`, the test fails.

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    # 1. Action: Make a GET request to the root URL "/"
    response = client.get("/")

    # 2. Assertion: Check that the status code is 200 (OK)
    assert response.status_code == 200

    # 3. Assertion: Check that the response data matches what we expect
    assert response.json() == {"message": "Welcome to the API!"}
```

### Adding New Tests
When you add new endpoints or functions, you should write tests for them!
- Create a new file inside the `tests/` directory (make sure the filename starts with `test_`, e.g., `test_routes.py`).
- Write Python functions inside that file (make sure the function names also start with `test_`, e.g., `def test_get_routes():`).
- Use `pytest` to run them!

Happy testing! 🎉
