from sre_constants import NOT_LITERAL
from urllib.parse import uses_params
import requests
import pandas as pd
import praw
import re

#inputs
client_id="m4gzaejsHU72KjNxYXkuOg"
client_secret="lQuXJL0fhaXeqFe3_GsNMIDourstNQ"
user_agent="MyBot/0.0.1"
password="124y1110nd"
username="spizzray"
search = "msr guardian"
search_limit = 31 #chose 31 cuz we observe that after 31, posts on msr guardian are no longer relevant
sort = "relevance"


'''_________FUNCTIONS__________'''

def upvote_ratio(ups, downs):
    total = ups + downs
    if total >0:
        ratio = float(ups/total)
        return ratio
    else:
        return 0

def search_string(search):
    result = search.replace(' ', '%20') 
    return result

def clean_text(text):                               # user defined function for cleaning text
    text = text.lower()                             # all lower case
    text = re.sub(r'\[.*?\]', ' ', text)            # remove text within [ ] (' ' instead of '')
    text = re.sub(r'\<.*?\>', ' ', text)            # remove text within < > (' ' instead of '')
    text = re.sub(r'http\S+', ' ', text)            # remove website ref http
    text = re.sub(r'www\S+', ' ', text)             # remove website ref www

    text = text.replace('€', 'euros')               # replace special character with words
    text = text.replace('£', 'gbp')                 # replace special character with words
    text = text.replace('$', 'dollar')              # replace special character with words
    text = text.replace('%', 'percent')             # replace special character with words
    text = text.replace('\n', ' ')                  # remove \n in text that has it

    text = text.replace('\'', '’')                  # standardise apostrophe
    text = text.replace('‚Äô;', '’')                # standardise apostrophe
    text = text.replace('‚Äù', '’')                 # standardise apostrophe
    text = text.replace('Äú', '’')                  # standardise apostrophe
    text = text.replace('‚Ä¶', '')                  # standardise apostrophe

    text = text.replace('’d', ' would')             # remove ’ (for would, should? could? had + PP?)
    text = text.replace('’s', ' is')                # remove ’ (for is, John's + N?)
    text = text.replace('’re', ' are')              # remove ’ (for are)
    text = text.replace('’ll', ' will')             # remove ’ (for will)
    text = text.replace('’ve', ' have')             # remove ’ (for have)
    text = text.replace('’m', ' am')                # remove ’ (for am)
    text = text.replace('can’t', 'can not')         # remove ’ (for can't)
    text = text.replace('won’t', 'will not')        # remove ’ (for won't)
    text = text.replace('n’t', ' not')              # remove ’ (for don't, doesn't)

    text = text.replace('’', ' ')                   # remove apostrophe (in general)
    text = text.replace('&quot;', ' ')              # remove quotation sign (in general)

    text = text.replace('cant', 'can not')          # typo 'can't' (note that cant is a proper word)
    text = text.replace('dont', 'do not')           # typo 'don't'

    text = re.sub(r'[^a-zA-Z0-9]', r' ', text)      # only alphanumeric left
    text = text.replace("   ", ' ')                 # remove triple empty space
    text = text.replace("  ", ' ')                  # remove double empty space
    return text



'''_________RAW REDDIT API CODE__________'''

auth = requests.auth.HTTPBasicAuth(client_id, client_secret)

data = {'grant_type': 'password',
        'username': username,
        'password': password}

# setup our header info, which gives reddit a brief description of our app
headers = {'User-Agent': user_agent}

# send our request for an OAuth token
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers) 

# convert response to JSON and pull access_token value
TOKEN = res.json()['access_token']

# add authorization to our headers dictionary
headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

# while the token is valid (~2 hours) we just add headers=headers to our requests

res = requests.get('https://oauth.reddit.com/search/?q='+ search_string(search) +'&sort=' + sort, headers=headers,  params = {'limit': str(search_limit)}) ##search function --> automate!!

#print(res.json()) #--> uncomment if you wanna see what is in the link
#print(post["data"].keys()) #--> uncomment to see the keys you can use for post['data']
#post['kind']+'_'+ post['data']['id'] #--> get the unique id for the post

'''_________USING PRAW LIBRARY FOR COMMENTS__________'''

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
    password=password,
    username=username,
)
# submission = reddit.submission(url="https://www.reddit.com/search/?q=" + search_string(search) + "&sort=hot")

# #comments = submission.comments.list() #.list includes all the replies too
# comments = submission.comments

'''_________PANDAS__________'''
df = pd.DataFrame()


for post in res.json()['data']['children']:
    print(post['data']['id'])


for post in res.json()['data']['children']:
    df = df.append({
        'subreddit': clean_text(post['data']['subreddit']),
        'title': clean_text(post['data']['title']),
        'selftext': clean_text(post['data']['selftext']),
        'ups': post['data']['ups'],
        'downs': post['data']['downs'],
        'upvote_ratio': post['data']['upvote_ratio'],
        'overall_text': clean_text(post['data']['title']) + clean_text(post['data']['selftext']),
    }, ignore_index=True)

    submission = reddit.submission(url="https://www.reddit.com/" + post['data']['id'])
    comments = submission.comments.replace_more(limit=0)

    submission.comments.replace_more(limit = 0)

    for comment in submission.comments.list(): #NOT INCLUDING COMMENT REPLIES
        df = df.append({ 
            'comment': clean_text(comment.body),
            'comment ups': comment.ups,
            'comment downs': comment.downs,
            'overall_text': clean_text(comment.body),
            #'comment upvote_ratio': comment.upvote_ratio(comment.ups, comment.downs),
            }, ignore_index=True)


'''the ocode below no longer in use'''
# for row in df['title']:
#     for i, comment in enumerate(comments): #enumerate labels comments with own index
#         df['comment {}'.format(i+1)] = comment.body
#         df['comment {} ups'.format(i+1)] = comment.ups
#         df['comment {} downs'.format(i+1)] = comment.downs
#         df['comment {} upvote_ratio'.format(i+1)] = upvote_ratio(comment.ups, comment.downs)

# for comment in comments:
#     df = df.append({
#         'comment': comment.body,
#         'comment ups': comment.ups,
#         'comment downs': comment.downs,
#         'comment upvote_ratio': upvote_ratio(comment.ups, comment.downs),
#         }, ignore_index=True)

print(df)

df.to_csv(r'/Users/raymondharrison/Desktop/DAI/AI Applicatoins/{}.csv'.format(search))