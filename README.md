# AskOut - Restaurant Reservation Backend

AskOut is a backend service for a restaurant reservation app. The backend identifies suitable restaurant matches for users and their friends based on cuisine preferences, dining times, and distances between users, their friends, and restaurants. This project uses several APIs to gather relevant data and generate optimal matches, providing a seamless dining experience.

## Features

- **Restaurant Matching**: Based on user and friend preferences for cuisines and dining times.
- **Distance Calculation**: Calculates the distance between a restaurant and user/friend addresses using Google Maps API.
- **AI-driven Suggestions**: Uses LangChain's API to generate tailored restaurant recommendations.

## Tech Stack

- **FastAPI**: Framework for building the API.
- **Google Maps API**: For geocoding, distance calculations, and restaurant searches.
- **LangChain API**: To process and generate restaurant match suggestions based on user and friend preferences.

## Setup and Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/AskOut.git
    cd AskOut
    ```

2. Create a virtual environment:

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up API keys:

    - Create a `config.json` file in the project directory with your Google Maps and LangChain API keys:

    ```json
    {
      "USER": "your_username",
      "GOOGLE_MAPS_KEY": "your_google_maps_api_key",
      "GEMINI_API": "your_langchain_api_key"
    }
    ```

5. Run the application:

    ```bash
    uvicorn main:app --reload
    ```

## API Endpoints

### `/`

- **Method**: POST
- **Description**: Generates restaurant recommendations for users and their friends based on preferences.
- **Request**: User and friend preferences, including location, cuisine, and dining time.
- **Response**: A JSON string with restaurant recommendations, including restaurant names, timings, distances, and reasons for the match.

### Example Request:

```json
{
  "user": {
    "name": "Alice",
    "Address": "123 Main St, City",
    "cuisines": "Italian, Chinese",
    "preferred_time": "7:00 PM"
  },
  "friend1": {
    "name": "Bob",
    "Address": "456 Elm St, City",
    "cuisines": "Italian, Mexican",
    "preferred_time": "8:00 PM"
  }
}
