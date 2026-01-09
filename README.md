# Smart Study Companion

A college-level mini project using Flask and AI (Mock/Real).

## Prerequisities
- Python 3.x installed
- `pip` package manager

## Installation

1.  **Clone/Download** this repository.
2.  **Install Dependencies**:
    ```bash
    pip install flask
    ```

## Running the Project

1.  Navigate to the project directory:
    ```bash
    cd smart_study_ai
    ```
2.  Run the application:
    ```bash
    python app.py
    ```
3.  Open your browser and visit: `http://127.0.0.1:5000`

## Login Credentials (Demo)

| Role | Username | Roll Number |
| :--- | :--- | :--- |
| **Student** | `student` | `1001` |
| **Demo User** | `demo` | `12345` |

## Features

-   **Dashboard**: View syllabus progress and subjects.
-   **AI Learning**: Get explanations for topics (currently in Mock Mode).
-   **Quiz**: Take quizzes and get instant feedback.
-   **Analysis**: View your performance level.

## Configuration

To enable real AI (OpenAI/Gemini), edit `config.py`:
-   Set `AI_PROVIDER` to `"openai"` or `"gemini"`.
-   Add your API key.
