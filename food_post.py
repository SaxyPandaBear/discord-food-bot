# DTO for aggregated information from a Reddit post
class FoodPost:
    # Attributes
    # title - the Post title
    # subreddit - the subreddit that this post was found in
    # post_url - the permalink for this post
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.title = kwargs.get('title')
        self.post_url = kwargs.get('permalink')
        self.image_url = kwargs.get('image_url')
