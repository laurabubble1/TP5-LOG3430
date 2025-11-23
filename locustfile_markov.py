from locust import HttpUser, constant, between
from locust.user.markov_taskset import MarkovTaskSet, transition, transitions
from client import SocialMediaClient

class MarkovChainTaskSet(MarkovTaskSet):
    wait_time = between(1, 5)
    
    def __init__(self, user):
        super().__init__(user)
        self.social_media_client = SocialMediaClient(self.client)

    def on_start(self):
        self.social_media_client.login()

    @transitions({
        "like_post": 673,
        "view_profile": 178,
        "create_post": 149
    })
    def view_feed(self):
        self.social_media_client.view_feed()

    @transitions({
        "view_profile": 688,
        "view_feed": 312
    })
    def like_post(self):
        self.social_media_client.like_post()

    @transitions({
        "follow_user": 680,
        "view_feed": 320
    })
    def view_profile(self):
        self.social_media_client.view_profile()

    @transition("view_feed")
    def follow_user(self):
        self.social_media_client.follow_user()

    @transition("view_feed")
    def create_post(self):
        self.social_media_client.create_post()

class ExampleSocialMediaUser(HttpUser):
    wait_time = between(1, 5)
    tasks = {MarkovChainTaskSet: 1}
