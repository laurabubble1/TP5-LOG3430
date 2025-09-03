# Social Media API

A FastAPI application that provides basic social media functionality.

## Features

- User authentication
- Create and view posts
- Like posts
- Follow users
- View user profiles

## Installation and Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python server/main.py
   ```

## Usage

1. The application will start with sample data (10 users with adjective-noun names and 17 posts)
2. Use the `/login` endpoint to authenticate with one of the sample users:
   - username: creative_beaver, password: password1
   - username: thoughtful_elephant, password: password2
   - username: adventurous_tiger, password: password3
   - username: curious_walrus, password: password4
   - username: sleepy_panda, password: password5
   - and more...
3. Use the returned token in the Authorization header for subsequent requests

## API Documentation

Once the application is running, you can access the auto-generated API documentation at:
- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc