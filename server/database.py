from datetime import datetime
from typing import List, Dict, Set, Optional
import models

# In-memory database
users: Dict[int, models.User] = {}
posts: Dict[int, models.Post] = {}
follows: Dict[int, Set[int]] = {}  # user_id -> set of followed user_ids
likes: Dict[int, Set[int]] = {}  # post_id -> set of user_ids who liked the post
user_credentials: Dict[str, str] = {}  # username -> password
username_to_id: Dict[str, int] = {}  # username -> user_id

# Counter for generating IDs
user_id_counter = 1
post_id_counter = 1

# Initialize with some sample data
def init_db():
    global user_id_counter, post_id_counter
    
    # Create users with adjective-noun names
    create_user(models.UserCreate(username="creative_beaver", email="creative_beaver@example.com", password="password1"))
    create_user(models.UserCreate(username="thoughtful_elephant", email="thoughtful_elephant@example.com", password="password2"))
    create_user(models.UserCreate(username="adventurous_tiger", email="adventurous_tiger@example.com", password="password3"))
    create_user(models.UserCreate(username="curious_walrus", email="curious_walrus@example.com", password="password4"))
    create_user(models.UserCreate(username="sleepy_panda", email="sleepy_panda@example.com", password="password5"))
    create_user(models.UserCreate(username="energetic_fox", email="energetic_fox@example.com", password="password6"))
    create_user(models.UserCreate(username="clever_raven", email="clever_raven@example.com", password="password7"))
    create_user(models.UserCreate(username="friendly_dolphin", email="friendly_dolphin@example.com", password="password8"))
    create_user(models.UserCreate(username="mysterious_owl", email="mysterious_owl@example.com", password="password9"))
    create_user(models.UserCreate(username="playful_otter", email="playful_otter@example.com", password="password10"))
    
    # Create posts for users
    create_post(models.PostCreate(content="Just finished designing a new art project using recycled materials. Creativity is all about seeing new possibilities!"), 1)
    create_post(models.PostCreate(content="Working on a DIY home studio setup. Anyone have tips for sound insulation on a budget?"), 1)

    create_post(models.PostCreate(content="Spent the morning meditating and reflecting on the nature of happiness. What brings you joy?"), 2)
    create_post(models.PostCreate(content="Reading philosophy under my favorite oak tree today. The wisdom of the ancients is still so relevant."), 2)

    create_post(models.PostCreate(content="Just returned from backpacking across South America! The Andes mountains were breathtaking."), 3)
    create_post(models.PostCreate(content="Planning my next expedition to Iceland. Any recommendations for off-the-beaten-path locations?"), 3)
    
    create_post(models.PostCreate(content="Just discovered a fascinating documentary about deep-sea creatures. Anyone else interested in marine biology?"), 4)
    create_post(models.PostCreate(content="Question of the day: Why do we drive on parkways but park on driveways? 🤔"), 4)
    
    create_post(models.PostCreate(content="Napped for 3 hours today. Still tired. Is this normal? 😴"), 5)
    create_post(models.PostCreate(content="My perfect weekend: sleep, eat bamboo, repeat. What's yours?"), 5)
    
    create_post(models.PostCreate(content="Just completed my morning 10k run! Starting the day with energy and positivity!"), 6)
    create_post(models.PostCreate(content="Life hack: sunrise yoga followed by a cold shower. You'll thank me later! #MorningRoutine"), 6)
    
    create_post(models.PostCreate(content="Finished reading 'Thinking, Fast and Slow' - highly recommend for anyone interested in cognitive biases."), 7)
    create_post(models.PostCreate(content="Chess tournament this weekend! Any other players here? Looking for practice partners."), 7)
    
    create_post(models.PostCreate(content="Beach cleanup organized for this Saturday! Join us at Sunset Beach, 9 AM. Bring friends! 🏖️"), 8)
    create_post(models.PostCreate(content="Made new friends at the community garden today. Love how plants bring people together! 🌱"), 8)
    
    create_post(models.PostCreate(content="3 AM thoughts: What if the universe is just one atom in a larger cosmos?"), 9)
    create_post(models.PostCreate(content="Sometimes the quietest person in the room has the loudest mind."), 9)
    
    create_post(models.PostCreate(content="Found the best water slide at the new aqua park! Who's joining me this weekend? 💦"), 10)
    create_post(models.PostCreate(content="Life motto: If you're not having fun, you're doing it wrong! 😄"), 10)

    # Set up follows for users
    follow_user(1, 2)  # creative_beaver follows thoughtful_elephant
    follow_user(2, 1)  # thoughtful_elephant follows creative_beaver
    follow_user(3, 1)  # adventurous_tiger follows creative_beaver
    follow_user(3, 2)  # adventurous_tiger follows thoughtful_elephant
    follow_user(4, 5)  # curious_walrus follows sleepy_panda
    follow_user(4, 6)  # curious_walrus follows energetic_fox
    follow_user(5, 4)  # sleepy_panda follows curious_walrus
    follow_user(5, 7)  # sleepy_panda follows clever_raven
    follow_user(6, 8)  # energetic_fox follows friendly_dolphin
    follow_user(6, 10) # energetic_fox follows playful_otter
    follow_user(7, 9)  # clever_raven follows mysterious_owl
    follow_user(7, 6)  # clever_raven follows energetic_fox
    follow_user(8, 10) # friendly_dolphin follows playful_otter
    follow_user(8, 4)  # friendly_dolphin follows curious_walrus
    follow_user(9, 7)  # mysterious_owl follows clever_raven
    follow_user(9, 5)  # mysterious_owl follows sleepy_panda
    follow_user(10, 8) # playful_otter follows friendly_dolphin
    follow_user(10, 6) # playful_otter follows energetic_fox

# User operations
def create_user(user_create: models.UserCreate) -> models.User:
    global user_id_counter
    
    user = models.User(
        id=user_id_counter,
        username=user_create.username,
        email=user_create.email,
        created_at=datetime.now()
    )
    
    users[user.id] = user
    follows[user.id] = set()  # Initialize empty set of follows
    user_credentials[user.username] = user_create.password
    username_to_id[user.username] = user.id
    
    user_id_counter += 1
    return user

def get_user(user_id: int) -> Optional[models.User]:
    return users.get(user_id)

def get_user_by_username(username: str) -> Optional[models.User]:
    user_id = username_to_id.get(username)
    if user_id:
        return users.get(user_id)
    return None

def authenticate_user(username: str, password: str) -> Optional[models.User]:
    if username in user_credentials and user_credentials[username] == password:
        return get_user_by_username(username)
    return None

def follow_user(follower_id: int, followed_id: int) -> bool:
    if follower_id not in users or followed_id not in users:
        return False
    
    follows[follower_id].add(followed_id)
    return True

def get_profile(user_id: int) -> Optional[models.UserProfile]:
    user = get_user(user_id)
    if not user:
        return None
    
    # Count posts by this user
    post_count = sum(1 for post in posts.values() if post.author_id == user_id)
    
    # Count followers (users who follow this user)
    follower_count = sum(1 for followed_set in follows.values() if user_id in followed_set)
    
    # Count following (users this user follows)
    following_count = len(follows.get(user_id, set()))
    
    return models.UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        post_count=post_count,
        follower_count=follower_count,
        following_count=following_count
    )

# Post operations
def create_post(post_create: models.PostCreate, author_id: int) -> models.Post:
    global post_id_counter
    
    author = users[author_id]
    
    post = models.Post(
        id=post_id_counter,
        content=post_create.content,
        author_id=author_id,
        author_username=author.username,
        created_at=datetime.now(),
        likes=0
    )
    
    posts[post.id] = post
    likes[post.id] = set()  # Initialize empty set of likes
    
    post_id_counter += 1
    return post

def get_post(post_id: int) -> Optional[models.Post]:
    return posts.get(post_id)

def like_post(post_id: int, user_id: int) -> bool:
    global likes
    
    if post_id not in posts or user_id not in users:
        return False
    
    # Add user to the set of users who liked this post
    if post_id in likes and user_id not in likes[post_id]:
        likes[post_id].add(user_id)
        posts[post_id].likes += 1
    
    return True

def get_feed(user_id: int) -> List[models.Post]:
    if user_id not in follows:
        return []
    
    # Get posts from users that this user follows
    followed_users = follows[user_id]
    feed_posts = [post for post in posts.values() if post.author_id in followed_users]
    
    # Sort by creation time (newest first)
    feed_posts.sort(key=lambda post: post.created_at, reverse=True)
    
    return feed_posts

# Initialize the database with sample data
init_db()