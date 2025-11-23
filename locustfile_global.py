from locust import task, between, TaskSet, User, HttpUser
from client import SocialMediaClient

class ExampleTaskSet(TaskSet):
    def __init__(self, user: User):
        super().__init__(user)
        self.social_media_client = SocialMediaClient(self.client)

    def on_start(self):
        self.social_media_client.login()

    @task(345)
    def view_feed_api(self):
        self.social_media_client.view_feed()
    
    @task(230)
    def like_post(self):
        self.social_media_client.like_post()
    
    @task(218)
    def view_profile(self):
        self.social_media_client.view_profile()
    
    @task(146)
    def follow_user(self):
        self.social_media_client.follow_user()
    
    @task(51)
    def create_post(self):
        self.social_media_client.create_post()
    
    @task(10)
    def login_task(self):
        self.social_media_client.login()

class ExampleSocialMediaUser(HttpUser):
    wait_time = between(1, 5)
    tasks = [ExampleTaskSet]