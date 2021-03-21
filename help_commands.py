# returns a formatted string that describes the bot's usage
def bot_description() -> str:
    return 'This bot posts pictures of food on request, and on an hourly schedule.\n' \
           'Read more about this bot, or contribute to it at https://github.com/SaxyPandaBear/food_waifu'


# returns a string that details the usage of the 'random' function of the bot
def help_bot_random() -> str:
    return 'The bot posts a random embedded Discord message with a picture of food, sourced from Reddit.'


# returns a string that details the usage of the 'search' function of the bot
def help_bot_search() -> str:
    return 'The bot takes in search terms and posts the first picture it finds ' \
           'based on those terms. If the picture has already been posted, the bot attempts ' \
           'to post the next picture, until it exhausts all of its options.'


# returns a string that details the usage of the 'clear' function of the bot
def help_bot_clear() -> str:
    return 'The bot wipes the contents of the file that keeps track of all of the ' \
           'previously posted food items. *Administrator Only*'


# returns a string that details the usage of the 'restart' function of the bot
def help_bot_restart() -> str:
    return 'The bot restarts itself. *Administrator Only*'


def help_bot_list_keys() -> str:
    return 'The bot enumerates all of the current keys stored in Redis,' \
           'printing the values to the logger for debugging. *Administrator Only*'
