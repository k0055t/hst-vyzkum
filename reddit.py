import praw
import requests
import json
import os
import ollama
from datetime import datetime

# Function to download media
def download_media(url, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    local_filename = url.split('/')[-1]
    local_path = os.path.join(folder_path, local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

# Function to fetch random posts from a subreddit
def fetch_random_posts(subreddit_name, post_count):
    # Initialize Reddit API client
    reddit = praw.Reddit(
        client_id='TPW9DQUIKflNQPymHcjCug',
        client_secret='_gSi8g85NDnvJ9qPYMAIfrogIK9k-A',
        user_agent='SocialSpotter/0.1 by Salko-501'
    )
    
    subreddit = reddit.subreddit(subreddit_name)
    
    posts = []
    
    for submission in subreddit.top(limit=post_count):
        author_name = submission.author.name if submission.author else 'deleted'
        author_age = get_reddit_account_age(reddit, author_name) if submission.author else None

        post_data = {
            'title': submission.title,
            'selftext': submission.selftext,
            'url': submission.url,
            'author': {
                'name': author_name,
                'account_age_days': author_age
            },
            'media': [],
            'comments': []
        }
        
        # Download media if available
        if submission.url and ('jpg' in submission.url or 'png' in submission.url or 'jpeg' in submission.url):
            media_folder = f"media/{subreddit_name}"
            try:
                media_file = download_media(submission.url, media_folder)
                post_data['media'].append({'url': submission.url, 'file': media_file})
            except:
                pass
        
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            post_data['comments'].append({
                'author': comment.author.name if comment.author else 'deleted',
                'content': comment.body,
            })

        posts.append(post_data)
    
    return posts

# Function to get Reddit account age in days
def get_reddit_account_age(reddit, username):
    try:
        user = reddit.redditor(username)
        account_creation_date = datetime.utcfromtimestamp(user.created_utc)
        account_age_days = (datetime.utcnow() - account_creation_date).days
    except:
        account_age_days = 0
    return account_age_days

def query_model_image(post, subreddit_name):
    comments = ""
    for i in range(0, min(len(post["comments"]), 20)):
        comments += "Comment author: " + post["comments"][i]["author"] + " Comment: " + post["comments"][i]["content"] + " ; "
    res = ollama.chat(
        model="llama3.2-vision",
        messages=[
            {
                'role': 'user',
                'content': 'Describe this image:',
                'images': ["./media/" + subreddit_name + "/"+post["media"][0]["file"]]
            }
        ]
    )
    auth_rating = ollama.chat(
        model="llama3.2-vision",
        messages=[
            {
                'role': 'user',
                'content': f'The post title is: "{post['title']}". The image attached to the post (described in words): "{res['message']['content']}" The image is posted on reddit. Please give a rating to the post on reddit, if the image is not from reddit, it has been reposted to reddit and therefore mostly the title will affect the rating. And the comments are (you should judge the comments to add more context, but the actual rating should be relevant to the post author): "{comments}" Give a rating to this post on a range of -10 to 10 based on weather it is authoritarian or libertarian. -10 means very libertarian (advocates for maximum individual freedom with minimal or no government involvement in both personal and economic spheres) -4 means lightly libertarian (emphasizes personal freedom and individual choice with minimal government interference in both personal and economic matters) 0 means that it cannot be judged 4 means lightly authoritarian (supports a level of government control to maintain order and stability but allows for some individual freedoms. This position might endorse regulations on businesses and social behavior to promote societal welfare while still providing limited personal liberties) and 10 means very authoritarian (advocates for strong central control over all aspects of life, including the economy, personal freedoms, and social behavior). The response absolutely has to be just a number. This is going to be about the individual opinions of people on this topic, but I want you to give me just a number, on where in the before mentioned range it would belong.',
            }
        ]
    )
    lr_rating = ollama.chat(
        model="llama3.2-vision",
        messages=[
            {
                'role': 'user',
                'content': f'The post title is: "{post['title']}".  The image attached to the post (described in words): "{res['message']['content']}" The image is posted on reddit. Please give a rating to the post on reddit, if the image is not from reddit, it has been reposted to reddit and therefore mostly the title will affect the rating. And the comments are (you should judge the comments to add more context, but the actual rating should be relevant to the post author): "{comments}" Give a rating to this post on a range of -10 to 10 based on weather it is political left or right. -10 means far left (advocates for radical social change through communism or socialism, emphasizes collective ownership, wealth redistribution, and strong government intervention in the economy to achieve social equality), around -4 means light left (supports progressive policies, seeks to balance capitalism with social welfare, advocating for reforms that enhance social justice without completely overhauling existing economic systems) 0 means that it cannot be judged 4 meand light right (favors free-market capitalism and limited government intervention in the economy, advocates for individual liberties, lower taxes, and deregulation, believing that economic growth is best achieved through market forces) and 10 means far right (often associated with authoritarianism and nationalism, keeps extreme measures to maintain traditional values and social order, emphasizes strong national defense, strict immigration controls, and can include populist rhetoric against perceived threats to national identity). The response absolutely has to be just a number. This is going to be about the individual opinions of people on this topic, but I want you to give me just a number, on where in the before mentioned range it would belong.',
            }
        ]
    )
    return [auth_rating['message']['content'], lr_rating['message']['content']]

def query_model_title(post):
    comments = ""
    for i in range(0, min(len(post["comments"]), 20)):
        comments += "Comment author: " + post["comments"][i]["author"] + " Comment: " + post["comments"][i]["content"] + " ; "
    auth_rating = ollama.chat(
        model="llama3.2-vision",
        messages=[
            {
                'role': 'user',
                'content': f'The post title is: "{post['title']}". And the comments are (you should judge the comments to add more context, but the actual rating should be relevant to the post author): "{comments}" Give a rating to this post on a range of -10 to 10 based on weather it is authoritarian or libertarian. -10 means very libertarian (advocates for maximum individual freedom with minimal or no government involvement in both personal and economic spheres) -4 means lightly libertarian (emphasizes personal freedom and individual choice with minimal government interference in both personal and economic matters) 0 means that it cannot be judged 4 means lightly authoritarian (supports a level of government control to maintain order and stability but allows for some individual freedoms. This position might endorse regulations on businesses and social behavior to promote societal welfare while still providing limited personal liberties) and 10 means very authoritarian (advocates for strong central control over all aspects of life, including the economy, personal freedoms, and social behavior). The response absolutely has to be just a number. This is going to be about the individual opinions of people on this topic, but I want you to give me just a number, on where in the before mentioned range it would belong.',
            }
        ]
    )
    lr_rating = ollama.chat(
        model="llama3.2-vision",
        messages=[
            {
                'role': 'user',
                'content': f'The post title is: "{post['title']}". And the comments are (you should judge the comments to add more context, but the actual rating should be relevant to the post author): "{comments}" Give a rating to this post on a range of -10 to 10 based on weather it is political left or right. -10 means far left (advocates for radical social change through communism or socialism, emphasizes collective ownership, wealth redistribution, and strong government intervention in the economy to achieve social equality), around -4 means light left (supports progressive policies, seeks to balance capitalism with social welfare, advocating for reforms that enhance social justice without completely overhauling existing economic systems) 0 means that it cannot be judged 4 meand light right (favors free-market capitalism and limited government intervention in the economy, advocates for individual liberties, lower taxes, and deregulation, believing that economic growth is best achieved through market forces) and 10 means far right (often associated with authoritarianism and nationalism, keeps extreme measures to maintain traditional values and social order, emphasizes strong national defense, strict immigration controls, and can include populist rhetoric against perceived threats to national identity). The response absolutely has to be just a number. This is going to be about the individual opinions of people on this topic, but I want you to give me just a number, on where in the before mentioned range it would belong.',
            }
        ]
    )
    return [auth_rating['message']['content'], lr_rating['message']['content']]

def main(subreddit_name, post_count, output_file):
    posts = fetch_random_posts(subreddit_name, post_count)
    print("Fetched posts")
    
    for post in posts:
        if post["media"] != []:
            print("Starting work on a new post /w media")
            ratings = query_model_image(post, subreddit_name)
            print("Finished work on a new post /w media")
        else:
            print("Starting work on a new post")
            ratings = query_model_title(post)
            print("Finished work on a new post")
        post['libertarian_to_authoritarian_rating'] = ratings[0]
        post['left_to_right_rating'] = ratings[1]
        print("rating obtained")
    
    with open(output_file, 'w') as f:
        json.dump(posts, f, indent=4)

    print(f"Saved {post_count} posts from r/{subreddit_name} to {output_file}")

if __name__ == "__main__":
    subreddit_name = 'memes'  # Replace with the desired subreddit
    post_count = 50  # Number of posts to fetch
    output_file = subreddit_name+'.json'  # Output JSON file
    try:
        main(subreddit_name, post_count, output_file)
    except Exception as e:
        print(e)

    subreddit_name = 'czechmemes'  # Replace with the desired subreddit
    post_count = 50  # Number of posts to fetch
    output_file = subreddit_name+'.json'  # Output JSON file
    try:
        main(subreddit_name, post_count, output_file)
    except Exception as e:
        print(e)


    subreddit_name = 'dataisbeautiful'  # Replace with the desired subreddit
    post_count = 50  # Number of posts to fetch
    output_file = subreddit_name+'.json'  # Output JSON file
    try:
        main(subreddit_name, post_count, output_file)
    except Exception as e:
        print(e)

        subreddit_name = 'funny'  # Replace with the desired subreddit
    post_count = 50  # Number of posts to fetch
    output_file = subreddit_name+'.json'  # Output JSON file
    try:
        main(subreddit_name, post_count, output_file)
    except Exception as e:
        print(e)


   

 