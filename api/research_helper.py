import os
import requests
import re
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
from ai_helper import generate_ai_response
import feedparser
import random
import urllib.parse

SERP_API_KEY = os.environ.get("SERP_API_KEY", "")

def web_search(query, engine="google"):
    """🌐 Execute high-fidelity web search via SerpApi"""
    params = {
        "engine": engine,
        "q": query,
        "api_key": SERP_API_KEY
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        return results
    except Exception as e:
        print(f"❌ [RESEARCH] Search failed: {e}")
        return {}

def get_rss_news(query):
    """📡 Fetch supplemental news headlines via Google News RSS (Keyless)"""
    try:
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        results = []
        if feed.entries:
            for entry in feed.entries[:5]:
                results.append(f"Title: {entry.title}\nSource: {entry.get('source', {}).get('title', 'Unknown')}\n")
        return "\n".join(results)
    except Exception as e:
        print(f"⚠️ [RESEARCH] RSS news failed: {e}")
        return ""

def get_news_summary(topic_or_link):
    """📰 Analyze news topic or URL to extract core narrative context"""
    content = ""
    
    # 1. Handle URL Scraping
    if topic_or_link.startswith("http"):
        print(f"🔗 [RESEARCH] Scraping source link: {topic_or_link}")
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(topic_or_link, headers=headers, timeout=15)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # Remove script/style
                for s in soup(["script", "style"]): s.decompose()
                content = soup.get_text(separator=' ', strip=True)[:3000] # Limit context
        except Exception as e:
            print(f"⚠️ [RESEARCH] Scraping failed: {e}")
            content = f"Source URL: {topic_or_link}"
    else:
        # 2. Handle Dual-Vector Search (SerpApi + News RSS)
        print(f"📡 [RESEARCH] Fetching real-time news for: {topic_or_link}")
        
        # A. SerpApi News
        serp_results = web_search(topic_or_link, engine="google_news")
        news_results = serp_results.get("news_results", [])
        for item in news_results[:5]:
            content += f"SERP_NEWS: {item.get('title')} - {item.get('snippet')}\n"
            
        # B. Keyless RSS News (Variety/Redundancy)
        rss_content = get_rss_news(topic_or_link)
        if rss_content:
            content += f"\nRSS_NEWS_FEED:\n{rss_content}"

    if not content:
        return topic_or_link

    # 3. Synthesize via AI
    prompt = f"Given the following raw info or news snippets, extract the most viral, high-impact narrative summary for a 1-minute YouTube Short. Focus on the hook and core facts. Return ONLY the summarized narrative.\n\nRAW INFO:\n{content}"
    summary = generate_ai_response(prompt)
    return summary.text if hasattr(summary, 'text') else str(summary)

def get_niche_trends(niche):
    """🎯 Discover trending topics within a specific niche"""
    print(f"🔥 [RESEARCH] Discovering trends for niche: {niche}")
    query = f"trending news and hot topics in {niche} {datetime.now().strftime('%B %Y')}"
    results = web_search(query)
    
    organic = results.get("organic_results", [])
    snippets = "\n".join([f"- {r.get('title')}: {r.get('snippet')}" for r in organic[:10]])
    
    prompt = f"Based on these search results for the {niche} niche, identify the single most viral and 'trendy' specific topic right now that would make a great YouTube Short. Return ONLY the topic title.\n\nRESULTS:\n{snippets}"
    trending_topic = generate_ai_response(prompt)
    return trending_topic.text if hasattr(trending_topic, 'text') else str(trending_topic)

from datetime import datetime
