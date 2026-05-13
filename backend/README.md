# Backend - Trivia API

## Setting up the Backend

### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createdb trivia
```

If your local Postgres user or password differs from the default, put them in a `.env` file in the `backend` folder and the app will load them automatically.

Create a `.env` file with values like:

```bash
TRIVIA_DB_NAME=trivia
TRIVIA_TEST_DB_NAME=trivia_test
TRIVIA_DB_USER=postgres
TRIVIA_DB_PASSWORD=your_password
TRIVIA_DB_HOST=localhost:5432
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/trivia
TEST_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/trivia_test
```

Or export them in your shell if you prefer:

```bash
export TRIVIA_DB_USER=postgres
export TRIVIA_DB_PASSWORD=your_password
export TRIVIA_DB_HOST=localhost:5432
export TRIVIA_TEST_DB_NAME=trivia_test
export DATABASE_URL=postgresql://postgres:your_password@localhost:5432/trivia
export TEST_DATABASE_URL=postgresql://postgres:your_password@localhost:5432/trivia_test
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `./backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## To Do Tasks

These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle `GET` requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle `GET` requests for all available categories.
4. Create an endpoint to `DELETE` a question using a question `ID`.
5. Create an endpoint to `POST` a new question, which will require the question and answer text, category, and difficulty score.
6. Create a `POST` endpoint to get questions based on category.
7. Create a `POST` endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a `POST` endpoint to get questions to play the quiz. This endpoint should take a category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422, and 500.

## Documenting your Endpoints

You will need to provide detailed documentation of your API endpoints including the URL, request parameters, and the response body. Use the example below as a reference.

## API Endpoint Documentation

The Trivia API currently exposes the following endpoints. The backend listens on the Flask server base URL, for example `http://localhost:5000`.

### `GET /categories`

- Description: Fetches all trivia categories.
- Request Arguments: None
- Response Body:

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

### `GET /questions`

- Description: Fetches a paginated list of questions.
- Request Arguments:
  - `page` (optional, integer) - page number for pagination, defaults to 1.
- Response Body:

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "What is the capital of France?",
      "answer": "Paris",
      "category": "3",
      "difficulty": 2
    }
  ],
  "total_questions": 100,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null
}
```

### `DELETE /questions/<question_id>`

- Description: Deletes a specific question by its ID.
- Request Arguments: None in query string.
- URL Parameters:
  - `question_id` (integer) - ID of the question to delete.
- Response Body:

```json
{
  "success": true,
  "deleted": 5
}
```

### `POST /questions` (create a question)

- Description: Creates a new question.
- Request Body (JSON):
  - `question` (string) - text of the question.
  - `answer` (string) - answer text.
  - `category` (integer or string) - category ID.
  - `difficulty` (integer) - difficulty rating.
- Response Body:

```json
{
  "success": true,
  "created": 15
}
```

### `POST /questions` (search questions)

- Description: Searches questions by substring match on the question text.
- Request Body (JSON):
  - `searchTerm` (string) - text to search for in questions.
- Response Body:

```json
{
  "success": true,
  "questions": [
    {
      "id": 3,
      "question": "Who wrote Hamlet?",
      "answer": "William Shakespeare",
      "category": "2",
      "difficulty": 3
    }
  ],
  "total_questions": 1,
  "current_category": null
}
```

### `GET /categories/<category_id>/questions`

- Description: Fetches questions within a specific category.
- Request Arguments: None in query string.
- URL Parameters:
  - `category_id` (integer) - ID of the requested category.
- Response Body:

```json
{
  "success": true,
  "questions": [
    {
      "id": 7,
      "question": "What is the largest ocean?",
      "answer": "Pacific Ocean",
      "category": "3",
      "difficulty": 2
    }
  ],
  "total_questions": 15,
  "current_category": "Geography"
}
```

### `POST /quizzes`

- Description: Returns a random quiz question that has not been asked previously.
- Request Body (JSON):
  - `previous_questions` (array of integers) - list of question IDs already asked.
  - `quiz_category` (object) - category object with at least an `id` field. Use `0` or `{ "id": 0 }` for all categories.
- Response Body:

```json
{
  "success": true,
  "question": {
    "id": 10,
    "question": "What planet is known as the Red Planet?",
    "answer": "Mars",
    "category": "1",
    "difficulty": 2
  }
}
```

- If no questions remain for the chosen category, the response is:

```json
{
  "success": true,
  "question": null
}
```

### Error Responses

The API uses JSON error responses for invalid requests.

- `400 Bad Request`

```json
{
  "success": false,
  "error": 400,
  "message": "bad request"
}
```

- `404 Not Found`

```json
{
  "success": false,
  "error": 404,
  "message": "resource not found"
}
```

- `422 Unprocessable Entity`

```json
{
  "success": false,
  "error": 422,
  "message": "unprocessable"
}
```

- `500 Internal Server Error`

```json
{
  "success": false,
  "error": 500,
  "message": "internal server error"
}
```

## Testing

Write at least one test for the success and at least one error behavior of each endpoint using the unittest library.

To deploy the tests, run

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
