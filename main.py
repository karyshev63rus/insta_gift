from instabot import Bot
import os
import argparse
from dotenv import load_dotenv
import re
import time
from collections import defaultdict

media_link='beautybar.rus'


def init_bot() -> object:
    """This function inits an instagram bot."""
    bot = Bot()
    bot.login(username=str(your_login), password=str(your_password))
    user_id = bot.get_user_id_from_username("lego")
    user_info = bot.get_user_info(user_id)
    return bot

def get_arg_link():
    """This function takes a link from from command line arg."""
    parser = argparse.ArgumentParser()
    parser.add_argument('post_link')
    arg = parser.parse_args()
    return arg.post_link
    
def get_data(post_link, bot) -> list:
    """This function get data about all users who commented that post."""
    id_link = bot.get_media_id_from_link(post_link)
    data_about_commenters = bot.get_media_comments_all(id_link)
    return data_about_commenters

def get_commenters_id(post_link, bot) -> list:
    """This function collect a set of users id, that have commented a post."""
    data_about_commenters = get_data(post_link, bot)
    commenters_id = [comment['user_id'] for comment in 
        data_about_commenters]
    return commenters_id

def get_likers_id(post_link, bot) -> list:
    """This function collect a set of likers id."""
    id_link = bot.get_media_id_from_link(post_link)
    likers_id = [int(liker_id) for liker_id in 
        bot.get_media_likers(str(id_link))]
    return likers_id

def get_followers_id(media_link, bot) -> list:
    """This function collect a set of followers id."""
    followers_id = [int(follower_id) for follower_id in 
        bot.get_user_followers(media_link)]
    return followers_id

def get_intersection_id(post_link, media_link, bot) -> list:
    """This function collect a set of users id who comment, likes and followed."""
    commenters_id = get_commenters_id(post_link, bot)
    likers_id = get_likers_id(post_link, bot)
    followers_id = get_followers_id(media_link, bot)
    comments_users_likers_followers_id = list(set(commenters_id) 
        & set(likers_id) & set(followers_id))
    return comments_users_likers_followers_id

def get_comments(post_link, media_link, bot) -> list:
    """This function collect a list of tupples with user_id, username, comment."""
    maybe_winners_id = get_intersection_id(post_link, 
        media_link, bot)
    comments = get_data(post_link, bot)
    comments_users_id_username_text = []
    for comment in comments:
        if comment['user_id'] in maybe_winners_id:
            comments_users_id_username_text.append((comment['user_id'], 
                comment['user']['username'], comment['text']))
    return comments_users_id_username_text
  
def parse_comment(text) -> str:
    """This function makes a list of usernames from a comment."""
    usernames_from_comment = re.findall(r'@(\w+)', text)
    return usernames_from_comment

def check_usernames(usernames_from_comment, bot) -> list:
    """This function authenticates a user id by its username."""
    check_usernames = []
    for username in usernames_from_comment:
        if bot.get_user_id_from_username(username):
            check_usernames.append(True)
    return any(check_usernames)

def get_winners(media_link) -> list:
    """This function create a list of winners."""
    bot = init_bot()
    post_link =  get_arg_link()
    comments_users_id_username_text = get_comments(post_link, media_link, bot)
    maybe_winners = defaultdict(list)
    for user_id, username, text in comments_users_id_username_text:
        parsed_text = parse_comment(text)
        maybe_winners[(user_id, username)].extend(parsed_text)
    winners = [winners_id_name for winners_id_name, username_reference 
    in maybe_winners.items() if check_usernames(set(username_reference), bot)]
    return winners

def main():
    winners = get_winners(media_link)
    print(winners)

if __name__=='__main__':

    load_dotenv()
    your_login = os.getenv('your_login')
    your_password = os.getenv('your_password')

    main()
