from googleapiclient.discovery import build
from MusicRecommenderSystem import config
import re

class YouTubeClient:
    def __init__(self):
        self.youtube = build('youtube', 'v3',
                    developerKey=Config.YOUTUBE_API_KEY)

    def search_music_video(self, track_name, artist_name):
       """Search for a music video on YouTube"""
       query = f"{track_name} {artist_name} official"

       request = self.youtube.search().list(
           part='snippet',
           q=query,
           type='video',
           videoCategoryId='10', #Music Category of choice
           maxResults=5
       )
     
       response = request.execute()

       
       
       if response['items']:
           return [ {
               'video_id': item['id']['videoId'],
               'title': item['snippet']['title'],
               'channel': item['snippet']['channelTitle'],
               'thumbnail': item['snippet']['thumbnails']['high']['url']
               } for item in response['items']]
       return []

    def get_video_details(self, video_id):
        """Get detailed information about a video"""
        request = self.youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        )

        response = request.execute()


        if response['items']:
            video = response['items'][0]
            return {
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'views':int(video['statistics'].get('viewCount',0)),
                'likes':int(video['statistics'].get('likeCount',0)),
                'duration':video['contentDetails']['duration']
            }

        return None



                                               