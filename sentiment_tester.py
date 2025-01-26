from sentiment import SentimentAnalyzer
#initialize the SentimentAnalyzer
analyzer = SentimentAnalyzer()
keywords = [
    "AI",
    "Monetization of AI",
    "LLM",
    "Training of LLM",
    "GPU",
    "AI software functionality"
]
#sentiment for each keyword
for keyword in keywords:
    try:
        sentiment_score, magnitude = analyzer.analyze_sentiment(keyword)
        print(f"Keyword: {keyword}")
        print(f"Sentiment Score: {sentiment_score}")
        print(f"Magnitude: {magnitude}")
        print("-" * 40)
    except Exception as e:
        print(f"Error analyzing sentiment for keyword '{keyword}': {e}")
