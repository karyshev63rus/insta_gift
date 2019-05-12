from instabot import Bot
import os
import argparse
from dotenv import load_dotenv
import re
import time
from collections import defaultdict

media_link='BEAUTYBAR.RUS'


def init_bot() -> object:
    """It inits an instagram bot."""
    bot = Bot()
    bot.login(username=str(your_login), password=str(your_password))
    return bot

def get_arg_link() -> str:
    """It takes a link from from command line arg."""
    parser = argparse.ArgumentParser()
    parser.add_argument('post_link')
    arg = parser.parse_args()
    return arg.post_link
    
def get_all_commenters(post_link, bot) -> list:
    """It gets some data about all users who commented that post."""
    id_link = bot.get_media_id_from_link(post_link)
    all_commenters = bot.get_media_comments_all(id_link)
    return all_commenters

def get_id_of_all_commenters(post_link, bot) -> list:
    """It collects a set of users id, that have commented a post."""
    all_commenters = get_all_commenters(post_link, bot)
    id_of_commenters = [commenter['user_id'] for commenter in 
        all_commenters]
    return id_of_commenters

def get_id_of_likers(post_link, bot) -> list:
    """It collects a set of likers id."""
    id_link = bot.get_media_id_from_link(post_link)
    id_of_likers = [int(id_of_liker) for id_of_liker in 
        bot.get_media_likers(str(id_link))]
    return id_of_likers

def get_id_of_followers(media_link, bot) -> list:
    """It collects a set of followers id."""
    id_of_followers = [int(id_of_follower) for id_of_follower in 
        bot.get_user_followers(media_link)]
    return id_of_followers

def get_common_id(post_link, media_link, bot) -> list:
    """It collects a set of users id who comment, likes and followed."""
    id_of_commenters = get_id_of_all_commenters(post_link, bot)
    id_of_likers = get_id_of_likers(post_link, bot)
    id_of_followers = get_id_of_followers(media_link, bot)
    id_of_users_who_commented_liked_and_followed = list(set(id_of_commenters) 
        & set(id_of_likers) & set(id_of_followers))
    return id_of_users_who_commented_liked_and_followed

def get_favorite_commenters(post_link, media_link, bot) -> list:
    """It collects a list of tupples with user_id, username and comment."""
    id_of_potential_winners = get_common_id(post_link, 
        media_link, bot)
    all_commenters = get_all_commenters(post_link, bot)
    favorite_commenters = []
    for commenter in all_commenters:
        if commenter['user_id'] in id_of_potential_winners:
            favorite_commenters.append((commenter['user_id'], 
                commenter['user']['username'], commenter['text']))
    return favorite_commenters
  
def get_usernames_from_comment(text) -> str:
    """It makes a list of usernames from a comment."""
    usernames_from_comment = re.findall(r'@(\w+)', text)
    return usernames_from_comment

def check_usernames(usernames_from_comment, bot) -> list:
    """It authenticates a user id by its username."""
    check_usernames = []
    for username in usernames_from_comment:
        if bot.get_user_id_from_username(username):
            check_usernames.append(True)
    return any(check_usernames)

def main():
    """It's a general function."""
    bot = init_bot()
    post_link =  get_arg_link()
    favorite_commenters = get_favorite_commenters(post_link, media_link, bot)
    maybe_winners = defaultdict(list)
    for user_id, username, text in favorite_commenters:
        usernames_from_comment = get_usernames_from_comment(text)
        maybe_winners[(user_id, username)].extend(usernames_from_comment)
    winners = [winners_id_name for winners_id_name, username_reference 
    in maybe_winners.items() if check_usernames(set(username_reference), bot)]
    print(winners)


if __name__=='__main__':

    load_dotenv()
    your_login = os.getenv('your_login')
    your_password = os.getenv('your_password')

    main()
