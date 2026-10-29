from flask import Flask, jsonify, request

from scraper import search_article
from summarizer import summarize_article

app = Flask(__name__)

REGISTRATION = "FA23-BDS-063"
NEWS_SOURCE = "TechCrunch"


@app.route("/", methods=["GET"])
def home():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>News Summarizer API</title>
    </head>
    <body>
        <h1>News Summarizer API</h1>
        <p>Registration Number: {REGISTRATION}</p>
        <p>News Source: {NEWS_SOURCE}</p>
        <p>Use /get?keyword=Pakistan to fetch and summarize an article.</p>
    </body>
    </html>
    """


@app.route("/get", methods=["GET"])
def get_news():
    keyword = request.args.get("keyword", "").strip()

    if not keyword:
        return jsonify({
            "error": "Please provide a keyword, e.g. /get?keyword=Pakistan"
        }), 400

    try:
        article = search_article(keyword)
        summary = summarize_article(article["text"])

        return jsonify({
            "registration": REGISTRATION,
            "newssource": NEWS_SOURCE,
            "keyword": keyword,
            "url": article["url"],
            "summary": summary
        })

    except Exception as error:
        app.logger.exception("News retrieval failed")
        return jsonify({
            "registration": REGISTRATION,
            "newssource": NEWS_SOURCE,
            "keyword": keyword,
            "error": str(error)
        }), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
