import os
import tweepy
import json
import time
import yagmail
import schedule
from datetime import datetime

def get_contents(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def get_emails(path):
    with open(path, 'r') as f:
        return f.read().splitlines()

def get_tweets(user):
    client = tweepy.Client(os.getenv('x_bearer_token'))
    try:
        user = client.get_user(username=user)
        user_data = user.data

        tweets = client.get_users_tweets(id=user_data.id, max_results=10)
        tweet_list = [tweet.text for tweet in tweets.data]
        
        result = {
            'user_data': str(user_data),
            'tweets': tweet_list,
            'timestamp': datetime.now().isoformat()
        }
        
        filename = './twitter_data/' + f'{datetime.now().strftime("%Y_%m%d_%H_%M_%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
            
        return result
    except tweepy.TweepyException as e:
        error_result = {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        filename = './twitter_data/' + f'{datetime.now().strftime("%Y_%m%d_%H_%M_%S")}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        return error_result

def format_tweet_content_html(data):
    if 'error' in data:
        return f"""
        <h3 style="color: red;">发生错误</h3>
        <p>{data['error']}</p>
        <p>时间：{data['timestamp']}</p>
        """
    
    user_info = data['user_data']
    tweets = data['tweets']
    timestamp = data['timestamp']
    
    # 构造 HTML 内容
    html = """
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #333;">用户信息</h2>
        <p>{user_info}</p>
        <hr style="border: 1px solid #ccc;">
        <h2 style="color: #333;">最新动态</h2>
        <ul style="list-style-type: none; padding: 0;">
    """.format(user_info=user_info)
    
    for i, tweet in enumerate(tweets, 1):
        html += f"""
        <li style="margin-bottom: 10px; padding: 10px; background: #f9f9f9; border-radius: 5px;">
            <strong>{i}.</strong> {tweet}
        </li>
        """
    
    html += """
        </ul>
        <hr style="border: 1px solid #ccc;">
        <p style="color: #666;">更新时间：{timestamp}</p>
    </body>
    </html>
    """.format(timestamp=timestamp)
    
    return html

def send_email(src, dst, subject, contents):
    pwd = os.environ.get('wangyi_emai_auth')
    yag = yagmail.SMTP(user=src, password=pwd, host='smtp.163.com', port='465')
    # 指定内容为 HTML
    yag.send(to=dst, subject=subject, contents=contents)
    yag.close()

def send_emails(src, tos, subject, contents):
    for to in tos:
        send_email(src, to, subject, contents)  

def daily_task():
    try:
        src = '19121220286@163.com'
        tos = get_emails('emails.txt') 
        subject = '今日AI+大佬实时信息流'
        raw_contents = get_tweets('elonmusk')
        contents = format_tweet_content_html(raw_contents)  # 使用 HTML 格式化
        print(contents)
        send_emails(src, tos, subject, contents)
    except Exception as e:
        print(f"{e} occured in daily_task")

if __name__ == "__main__":
    try:
        schedule.every().day.at('11:10').do(daily_task)
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        print(f"{e} occured~")