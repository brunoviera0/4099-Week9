import requests
from google.cloud import storage
from newsapi import NewsApiClient
import json
from datetime import datetime

#your Google Cloud project ID and bucket name would go here
PROJECT_ID = 'linear-listener-436516-c9'
BUCKET_NAME = 'news_4099'

#initialize storage and news API client
storage_client = storage.Client(project=PROJECT_ID)
newsapi = NewsApiClient(api_key='20ba84b32c674632bab001f2eb292c73')

def fetch_news(topic): #fetch an article about a given topic
    articles = newsapi.get_everything(q=topic, language='en', sort_by='publishedAt', page_size=1)
    if not articles['articles']:
        print(f"No news found for the topic: {topic}")
        return None
    return articles['articles'][0]  #return the first article

def upload_to_bucket(bucket_name, content, destination_blob_name): #upload fetched article to bucket
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(content, content_type='application/json')
    print(f"Uploaded file to {destination_blob_name} in {bucket_name} bucket.")

if __name__ == '__main__':
    topic = 'WBS'  #example topic, uses stock ticker for company
    article = fetch_news(topic)
    
    if article:
        #prepare the article content and file name
        content = json.dumps(article)
        date = datetime.now().strftime('%Y-%m-%d')
        file_name = f"news_{topic}_{date}.json"
        
        #upload the article to the bucket
        upload_to_bucket(BUCKET_NAME, content, file_name)
