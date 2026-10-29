from summa.summarizer import summarize


def summarize_article(text: str) -> str:
    """Extract the most important sentences from a news article."""

    if not text or not text.strip():
        return "Summary unavailable: article text is empty."

    text = " ".join(text.split())

    # Short articles may not contain enough sentences for TextRank.
    if len(text.split()) < 50:
        return text

    summary = summarize(
        text,
        ratio=0.25,
        words=150,
        split=False
    )

    if not summary or not summary.strip():
        return "Summary unavailable: insufficient article content."

    return summary.strip()
