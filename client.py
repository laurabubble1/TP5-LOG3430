import time
import random

from locust.clients import HttpSession


class SocialMediaClient:
    """
    A base API class that handles authentication and API interactions for the Social Media API.
    This class provides the core functionality for interacting with the API endpoints.
    """

    user_index = 0

    def __init__(self, client: HttpSession):
        """
        Create a new SocialMediaClient instance.
        :param client: The Locust HttpSession client from the User or TaskSet.
        """
        self.client = client

    def login(self):
        """
        Initialize the client by logging in and storing the access token.
        """
        user_options = [
            {"username": "creative_beaver", "password": "password1", "id": 1},
            {"username": "thoughtful_elephant", "password": "password2", "id": 2},
            {"username": "adventurous_tiger", "password": "password3", "id": 3},
            {"username": "curious_walrus", "password": "password4", "id": 4},
            {"username": "sleepy_panda", "password": "password5", "id": 5},
            {"username": "energetic_fox", "password": "password6", "id": 6},
            {"username": "clever_raven", "password": "password7", "id": 7},
            {"username": "friendly_dolphin", "password": "password8", "id": 8},
            {"username": "mysterious_owl", "password": "password9", "id": 9},
            {"username": "playful_otter", "password": "password10", "id": 10}
        ]

        # Select a user
        user = user_options[SocialMediaClient.user_index % len(user_options)]
        SocialMediaClient.user_index += 1
        self.username = user["username"]
        self.password = user["password"]
        self.user_id = user["id"]

        # Login to get access token
        response = self.client.post("/login",
                                   data={"username": self.username, "password": self.password},
                                   name="Login")

        # Check if login was successful
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}

            # Store IDs of users to follow and posts to like
            self.users_to_follow = [i for i in range(1, 11) if i != self.user_id]
            self.posts_to_like = list(range(1, 21))

    def view_feed(self):
        """
        API method to view the user's feed.
        """
        return self.client.get("/feed", headers=self.headers, name="View Feed")

    def create_post(self):
        """
        API method to create a new post.
        """
        return self.client.post("/post", 
                        json={"content": self.__generate_post_content()},
                        headers=self.headers,
                        name="Create Post")

    def like_post(self):
        """
        API method to like a post.
        """
        post_id = random.choice(self.posts_to_like)
        return self.client.post(f"/like/{post_id}",
                        headers=self.headers,
                        name="Like Post")

    def follow_user(self):
        """
        API method to follow a user.
        """
        user_id = random.choice(self.users_to_follow)
        return self.client.post(f"/follow/{user_id}",
                        headers=self.headers,
                        name="Follow User")

    def view_profile(self):
        """
        API method to view a user's profile.
        """
        user_id = random.randint(1, 10)
        return self.client.get(f"/profile/{user_id}",
                       headers=self.headers,
                       name="View Profile")


    def __generate_post_content(self):
        """
        Generate post content based on user personality.

        Args:
            username (str): The username of the user creating the post.

        Returns:
            str: The generated post content with a timestamp.
        """

        # Post templates for different user personalities
        post_templates = {
            "creative_beaver": [
                "Just designed a new sculpture using driftwood I collected from the beach. Art is everywhere!",
                "Looking for collaborators on a community mural project. DM me if interested!",
                "My studio is a beautiful mess today. The creative process isn't always tidy!"
            ],
            "thoughtful_elephant": [
                "Been contemplating the concept of time lately. How do you make the most of yours?",
                "Just finished reading a fascinating book on mindfulness. Changed my perspective completely.",
                "Sometimes sitting quietly with your thoughts is the most productive thing you can do."
            ],
            "adventurous_tiger": [
                "Conquered that mountain trail everyone said was too difficult! The view was worth every step.",
                "Packing for my next wilderness expedition. What's one item you never travel without?",
                "Life begins at the edge of your comfort zone. What adventure are you planning next?"
            ],
            "curious_walrus": [
                "Just learned about quantum computing. Mind = blown! Anyone else interested?",
                "Why do we say 'sleep like a baby' when babies wake up crying every 2 hours? 🤔",
                "Found this fascinating article about deep ocean creatures. Link in comments!"
            ],
            "sleepy_panda": [
                "Best nap spots in the city? Asking for a friend...",
                "Is it normal to need 12 hours of sleep? Asking for me.",
                "Just woke up from a nap. What year is it?"
            ],
            "energetic_fox": [
                "5 mile run before breakfast - best way to start the day!",
                "Who's up for a weekend hiking trip? The mountains are calling!",
                "New personal record at the gym today! #FitnessGoals"
            ],
            "clever_raven": [
                "Just solved that puzzle everyone's been talking about. The key is to think laterally.",
                "Interesting philosophical question: if a tree falls in a forest...",
                "Reading list update: just finished three books on cognitive psychology."
            ],
            "friendly_dolphin": [
                "Community garden meetup this weekend! Everyone welcome!",
                "Made cookies for the new neighbors. Building community one treat at a time!",
                "Beach cleanup was a success! Thanks to all 30 volunteers who showed up!"
            ],
            "mysterious_owl": [
                "Sometimes I wonder if we're all just characters in someone else's dream...",
                "The stars were particularly bright last night. Makes you think about our place in the universe.",
                "Found an old abandoned building. The stories these walls could tell..."
            ],
            "playful_otter": [
                "Water slide competition at the aqua park! I'm the reigning champion!",
                "Life's too short not to have fun every day! What made you smile today?",
                "Just invented a new game with my friends. We call it 'Splash Tag'!"
            ]
        }

        # Select a random post template for this user
        if self.username in post_templates:
            post_content = random.choice(post_templates[self.username])
        else:
            # Fallback for any user not in our templates
            post_content = f"Just sharing some thoughts on this {random.choice(['beautiful', 'rainy', 'sunny', 'cloudy'])} day!"

        # Add a timestamp to make each post unique
        current_time = time.strftime("%Y-%m-%d %H:%M")
        post_content = f"{post_content} [{current_time}]"

        return post_content
