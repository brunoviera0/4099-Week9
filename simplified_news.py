import requests
from google.cloud import datastore, storage
from newsapi import NewsApiClient
from datetime import datetime
import json
import matplotlib.pyplot as plt
from sentiment import SentimentAnalyzer

# Initialize sentiment analyzer, project, and bucket configurations
analyzer = SentimentAnalyzer()
PROJECT_ID = 'linear-listener-436516-c9'
BUCKET_NAME = 'news'
datastore_client = datastore.Client(project=PROJECT_ID)
storage_client = storage.Client(project=PROJECT_ID)
newsapi = NewsApiClient(api_key='20ba84b32c674632bab001f2eb292c73')

# Fetch news articles
def fetch_news(topic="WBS"):
    return newsapi.get_everything(q=topic, language='en', sort_by='publishedAt', page_size=5).get("articles", [])

# Upload content to Cloud Storage
def upload_to_bucket(content, blob_name, is_json=True):
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    if is_json:
        blob.upload_from_string(content, content_type='application/json')
    else:
        blob.upload_from_filename(content)
    print(f"Uploaded {blob_name} to {BUCKET_NAME} bucket.")

# Process each article: analyze sentiment and store results
def store_news_data(article, topic, sequential_num):
    sentiment_score, magnitude = analyzer.analyze_sentiment(article.get("content", "") or article.get("description", ""))
    date_str = datetime.now().strftime('%Y-%m-%d')
    file_name = f"news_{topic}_{date_str}_{sequential_num}.json"
    scored_file_name = f"scored_{file_name}"

    # Upload original and scored content to bucket
    upload_to_bucket(json.dumps(article), file_name)
    upload_to_bucket(json.dumps({"sentiment_score": sentiment_score}), scored_file_name)

    # Create and store entity in Datastore
    entity = datastore.Entity(datastore_client.key("newsData"))
    entity.update({
        "topic": topic,
        "title": article["title"],
        "description": article.get("description", ""),
        "sentiment_score": sentiment_score,
        "magnitude": magnitude,
        "url": article["url"],
        "published_at": article["publishedAt"],
        "file_name": file_name,
        "timestamp": datetime.utcnow()
    })
    datastore_client.put(entity)
    print(f"Stored article and sentiment for: {article['title']}")

# Retrieve data and sentiment scores for plotting
def retrieve_news_data():
    results = datastore_client.query(kind="newsData").fetch()
    dates, sentiment_scores = zip(*[(entity["published_at"], entity["sentiment_score"]) for entity in results])
    return dates, sentiment_scores

# Plot sentiment scores over time
def plot_sentiment(dates, sentiment_scores):
    if dates:
        plt.figure(figsize=(10, 6))
        plt.plot(dates, sentiment_scores, marker="o")
        plt.title("Sentiment Analysis for Webster Bank (WBS)")
        plt.xlabel("Date")
        plt.ylabel("Sentiment Score")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        image_filename = "sentiment.png"
        plt.savefig(image_filename)
        print(f"Plot saved as {image_filename}")
        upload_to_bucket(image_filename, image_filename, is_json=False)
    else:
        print("No data available to plot.")

# Main flow: fetch, process, store, and plot
if __name__ == "__main__":
    topic = "WBS"  # Webster Bank ticker for News API
    for i, article in enumerate(fetch_news(topic), start=1):
        store_news_data(article, topic, i)
    dates, sentiment_scores = retrieve_news_data()
    plot_sentiment(dates, sentiment_scores)
