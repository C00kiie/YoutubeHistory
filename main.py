#!/usr/bin/python


import argparse
import re
import json2html
import json
import youtube_dl as handler_aux
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = '#REPLACE_ME'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


includes = """
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
"""
opts = {
    # used to output less verbose information
    'no_warnings':True,
    'quiet':True,
    # audios filter
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

def number_readable(number):
    number = str(number)
    orig = number
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', number)
    if orig == new:
        return new
    else:
        return number_readable(new)

def	get_stats(link):
  statistics = {}
  with handler_aux.YoutubeDL(opts) as ydl:
                # video information for the given video
                info = ydl.extract_info(link, download=False)
                statistics['title'] = info.get('title', None)
                statistics['video_duration'] = info.get("duration", None)
                statistics['like_count']     =   number_readable (info.get("like_count", None))
                statistics['dislike_count']  =   number_readable (info.get("dislike_count", None))
                statistics['view_count']     =   number_readable ( info.get("view_count", None))
                m, s = divmod(statistics['video_duration'], 60)
                h, m = divmod(m, 60)
                if h > 0:
                    statistics['video_duration'] = '{}:{}:{}'.format(h, m, s)
                else:
                    statistics['video_duration'] = '{}:{}'.format(m, s)
                    # checking if video size exceeds the normal limit [50 MB]
  return statistics

def youtube_search(search_term,max_results):

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=search_term,
    part='id,snippet',
    maxResults=max_results
  ).execute()

  video_arr = []
  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get('items', []):
    if search_result['id']['kind'] == 'youtube#video':
      videoId = search_result['id']['videoId']
      snippet = search_result['snippet']
      link = 'http://www.youtube.com/watch?v='+videoId
      snippet['link'] = link
      url = snippet['thumbnails']['high']['url']
      snippet.pop('thumbnails')
      snippet['thumbnail'] = '<img src="{0}">'.format(url)
      snippet.pop('liveBroadcastContent')
      statistics = get_stats(link)
      for i in statistics.keys():
        snippet[i] = statistics[i]
      pub = snippet['publishedAt']
      snippet.pop('publishedAt')
      snippet['publishedAt'] = pub
      snippet.pop('channelId')
      video_arr.append(snippet)
  return video_arr
def json2html_output(search_term,maxResults=10):
  items = youtube_search(search_term,maxResults)
  
  for i in items:
    i['link'] = '<a href="{0}">link</a>'.format(i['link'])
  f = open(search_term,'w')
  html = includes + json2html.json2html.convert(escape = False,json = json.dumps(items), table_attributes="id=\"info-table\" class=\"table table-bordered table-hover\"")
  f.write(html)
  f.close()
def get_keywords(file='input.txt'):
  try:
    f = open('input.txt','r')
    content = f.readlines()
    f.close()
    c = 0
    for i in content:
      content[c] = content[c].replace('\n','')
      c+=1    
    return content
  except Exception as e:
    print('input.txt not found!')
    exit(-1)

if __name__ == '__main__':
  keywords = get_keywords()
  for keyword in keywords:
  	json2html_output(keyword);
