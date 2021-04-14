# DTO for aggregated information from a Reddit post
import discord


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
        self.color = 0xDB5172

    def __str__(self):
        return f'{self.title} : {self.post_url}'

    def __repr__(self):
        return self.__str__()

    # Transforms this FoodPost object into the discord Embed object that
    # should be posted by the bot.
    def to_embed(self) -> discord.Embed:
        em = discord.Embed(title=FoodPost.truncate(self.title), description=self.post_url, color=self.color)
        if self.image_url != '':
            em.set_image(url=self.image_url)
        return em

    # Given a Reddit submission title, truncate the title if it's too long
    # https://github.com/SaxyPandaBear/discord-food-bot/issues/28
    # If the title is not too long, return the input unchanged
    @staticmethod
    def truncate(title: str) -> str:
        if title is None:
            return None

        # truncate with an ellipsis, so we need some leeway
        if len(title) > 256:
            return title[:253] + '...'  # take first 253 characters
        return title

    # Take a Reddit submission object, and transform that into a FoodPost
    @staticmethod
    def from_submission(submission):
        sub_id = submission.id
        url = submission.url
        # permalink does not give the full URL, so build it instead.
        permalink = f'https://www.reddit.com{submission.permalink}'
        title = submission.title
        return FoodPost(id=sub_id, title=title, image_url=url, permalink=permalink)
