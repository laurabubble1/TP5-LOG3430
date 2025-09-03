from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Any
import models
import database
import logging

app = FastAPI(title="Social Media API")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Create a logger for our middleware
request_logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s]%(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
request_logger.addHandler(handler)
request_logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Extract method and path
    method = request.method
    path = request.url.path
    
    # Try to extract user from authorization header
    user = "anonymous"
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        # In this app, the token is simply the username
        user = token

    # Log the request
    request_logger.info(f"[{user}] {method} {path}")

    # Process the request and return the response
    response = await call_next(request)
    return response


# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = database.get_user_by_username(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@app.get("/feed", response_model=List[models.Post])
async def get_feed(current_user: models.User = Depends(get_current_user)):
    """
    Get all posts from users that the current user follows
    """
    return database.get_feed(current_user.id)


@app.post("/post", response_model=models.Post, status_code=status.HTTP_201_CREATED)
async def create_post(post: models.PostCreate, current_user: models.User = Depends(get_current_user)):
    """
    Create a new post
    """
    return database.create_post(post, current_user.id)


@app.post("/like/{post_id}", status_code=status.HTTP_200_OK)
async def like_post(post_id: int, current_user: models.User = Depends(get_current_user)):
    """
    Like a post
    """
    if not database.like_post(post_id, current_user.id):
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post liked successfully"}


@app.post("/follow/{user_id}", status_code=status.HTTP_200_OK)
async def follow_user(user_id: int, current_user: models.User = Depends(get_current_user)):
    """
    Follow a user
    """
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")

    if not database.follow_user(current_user.id, user_id):
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User followed successfully"}


@app.get("/profile/{user_id}", response_model=models.UserProfile)
async def get_profile(user_id: int, current_user: models.User = Depends(get_current_user)):
    """
    Get user profile
    """
    profile = database.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login to get access token
    """
    user = database.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # For simplicity, we're just returning the username as the token
    return {"access_token": user.username, "token_type": "bearer"}


LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "logging.Formatter",
            "fmt": "[%(asctime)s][%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080, log_config=LOGGING_CONFIG, access_log=False)
