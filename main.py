import streamlit as st
import feedparser
from newspaper import Article, Config
from PIL import Image
import requests
from io import BytesIO
import random
import nltk

# --- Ensure NLTK punkt tokenizer is available ---
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab')
    except:
        nltk.download('punkt')

# --- Streamlit UI Setup ---
st.set_page_config(page_title="🧠 Tech News Feed", layout="wide")
st.title("🧠 Tech News Digest")
st.caption("Live feed of top tech articles with varied layouts and summaries.")

# --- Tech Feeds and Keywords ---
TECH_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.wired.com/feed/rss",
    "https://www.theverge.com/rss/index.xml",
    "http://feeds.arstechnica.com/arstechnica/index",
    "https://www.cnet.com/rss/all/",
    "https://www.engadget.com/rss.xml",
    "https://gizmodo.com/rss",
    "https://www.digitaltrends.com/feed/",
    "https://www.zdnet.com/news/rss.xml",
    "https://www.slashgear.com/feed/",
]

TECH_KEYWORDS = [
    "technology", "AI", "artificial intelligence", "machine learning", "deep learning",
    "neural network", "NLP", "computer vision", "robotics", "blockchain", "cybersecurity",
    "cloud", "quantum", "software", "hardware", "semiconductor", "startup", "big data",
    "programming", "data science", "computing", "gadgets", "mobile", "5G", "wearable",
    "internet of things", "IoT", "AR", "VR", "tech", "developer", "app", "IT"
]

MAX_ARTICLES = 10

# Custom user-agent for newspaper3k
user_agent_config = Config()
user_agent_config.browser_user_agent = 'Mozilla/5.0'

# --- Caching and Fetching ---
@st.cache_data(ttl=600)
def fetch_tech_articles():
    articles = []
    seen_urls = set()

    for feed_url in TECH_FEEDS:
        parsed = feedparser.parse(feed_url)
        for entry in parsed.entries:
            if len(articles) >= MAX_ARTICLES:
                break
            url = entry.link
            if url in seen_urls:
                continue
            seen_urls.add(url)

            try:
                art = Article(url, config=user_agent_config)
                art.download()
                art.parse()
                art.nlp()
            except Exception as e:
                st.warning(f"⚠️ Skipped article: {url} ({e})")
                continue

            content = (art.title or "") + " " + art.summary
            if not any(kw.lower() in content.lower() for kw in TECH_KEYWORDS):
                continue

            articles.append({
                "title": art.title,
                "url": url,
                "summary": art.summary,
                "image": art.top_image,
                "source": parsed.feed.get("title", "Unknown"),
                "published": entry.get("published", "Unknown")
            })

        if len(articles) >= MAX_ARTICLES:
            break

    return articles[:MAX_ARTICLES]

# --- Article Display ---
def display_article(article, layout_style):
    try:
        img_data = requests.get(article["image"], timeout=3).content if article["image"] else None
        image = Image.open(BytesIO(img_data)).convert("RGB") if img_data else None
    except Exception:
        image = None

    if layout_style == "left-image":
        cols = st.columns([1, 3])
        with cols[0]:
            if image:
                st.image(image, use_container_width=True, clamp=True)
        with cols[1]:
            st.subheader(f"[{article['title']}]({article['url']})")
            st.caption(f"{article['source']} • {article['published']}")
            st.write(article["summary"])
        st.markdown("---")

    elif layout_style == "right-image":
        cols = st.columns([3, 1])
        with cols[0]:
            st.subheader(f"[{article['title']}]({article['url']})")
            st.caption(f"{article['source']} • {article['published']}")
            st.write(article["summary"])
        with cols[1]:
            if image:
                st.image(image, use_container_width=True, clamp=True)
        st.markdown("---")

    elif layout_style == "centered":
        st.subheader(f"[{article['title']}]({article['url']})")
        if image:
            st.image(image, use_container_width=True, clamp=True)
        st.caption(f"{article['source']} • {article['published']}")
        st.write(article["summary"])
        st.markdown("---")

    elif layout_style == "tile":
        st.markdown("### 📰 " + article["title"])
        if image:
            st.image(image, width=350, clamp=True)
        st.caption(f"{article['source']} • {article['published']}")
        st.write(article["summary"])
        st.markdown("---")

# --- Main Execution ---
with st.spinner("🔄 Fetching latest tech news..."):
    articles = fetch_tech_articles()

if not articles:
    st.warning("😕 No tech articles available right now. Try again later.")
else:
    layout_options = ["left-image", "right-image", "centered", "tile"]
    for article in articles:
        layout = random.choice(layout_options)
        display_article(article, layout)
