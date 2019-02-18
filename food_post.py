# DTO for aggregated information from a Reddit post
class FoodPost:
    # Attributes
    # id - the submission ID given by Reddit
    # title - the Post title
    # post_url - the permalink for this post
    # image_url - the url for the associated image of a submission
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.title = kwargs.get('title')
        self.post_url = kwargs.get('permalink')
        self.image_url = kwargs.get('image_url')

    def __str__(self):
        return '{0} : {1}'.format(self.title, self.post_url)

    def __repr__(self):
        return __str__()
