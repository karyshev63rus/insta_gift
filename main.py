from instabot import Bot
import os
import argparse
from dotenv import load_dotenv
import re
import time
from collections import defaultdict

MEDIA_LINK='beautybar.rus'


def get_arg_link() -> str:
    """It takes a link from from command line arg."""
    parser = argparse.ArgumentParser()
    parser.add_argument('post_link')
    arg = parser.parse_args()
    return arg.post_link
    
def get_all_comments(post_link, bot) -> list:
    """It gets some data about all users who commented that post."""
    id_link = bot.get_media_id_from_link(post_link)
    all_comments = bot.get_media_comments_all(id_link)
    return all_comments

def get_id_of_likers(post_link, bot) -> list:
    """It collects a set of likers id."""
    id_link = bot.get_media_id_from_link(post_link)
    id_of_likers = [int(id_of_liker) for id_of_liker in 
        bot.get_media_likers(str(id_link))]
    return id_of_likers

def get_id_of_users_who_commented_liked_and_followed(post_link, MEDIA_LINK, 
        bot) -> list:
    """It collects a set of users id who comment, likes and followed."""
    all_comments = get_all_comments(post_link, bot)
    id_of_comments = [comment['user_id'] for comment in all_comments]
    id_of_likers = get_id_of_likers(post_link, bot)
    id_of_followers = [int(id_of_follower) for id_of_follower in 
        bot.get_user_followers(MEDIA_LINK)]
    id_of_users_who_commented_liked_and_followed = list(set(id_of_comments) 
        & set(id_of_likers) & set(id_of_followers))
    return id_of_users_who_commented_liked_and_followed

def get_favorite_comments(post_link, MEDIA_LINK, bot) -> list:
    """It collects a list of tupples with user_id, username and comment."""
    id_of_potential_winners = \
    get_id_of_users_who_commented_liked_and_followed(post_link, 
        MEDIA_LINK, bot)
    all_comments = get_all_comments(post_link, bot)
    favorite_comments = []
    for comment in all_comments:
        if comment['user_id'] in id_of_potential_winners:
            favorite_comments.append((comment['user_id'], 
                comment['user']['username'], comment['text']))
    return favorite_comments
  
def get_usernames_from_comment(text) -> str:
    """It makes a list of usernames from a comment."""
    usernames_from_comment = re.findall(r'@(\w+)', text)
    return usernames_from_comment

def check_usernames(usernames_from_comment, bot) -> list:
    """It authenticates a user id by its username."""
    return any(bot.get_user_id_from_username(username) for username 
        in usernames_from_comment)

def get_winners(post_link, MEDIA_LINK, bot):
    """It creates a list of winners."""
    favorite_comments = get_favorite_comments(post_link, MEDIA_LINK, bot)
    maybe_winners = defaultdict(list)
    for user_id, username, text in favorite_comments:
        usernames_from_comment = get_usernames_from_comment(text)
        maybe_winners[(user_id, username)].extend(usernames_from_comment)
    winners = [winners_id_name for winners_id_name, username_reference 
    in maybe_winners.items() if check_usernames(set(username_reference), bot)]
    return winners

if __name__=='__main__':

    load_dotenv()
    your_login = os.getenv('your_login')
    your_password = os.getenv('your_password')

    bot = Bot()
    bot.login(username=str(your_login), password=str(your_password))
    post_link =  get_arg_link()
    print(get_winners(post_link, MEDIA_LINK, bot))
    