"""
Task 2 — Crawl bài báo về nghệ sĩ liên quan tới ma tuý.

Hướng dẫn:
    1. Crawl tối thiểu 5 bài báo từ các trang tin tức Việt Nam.
    2. Sử dụng requests + BeautifulSoup (nhanh, không cần browser).
    3. Lưu output vào data/landing/news/
    4. Mỗi bài lưu 1 file JSON với metadata (url, title, date_crawled, content).

Cài đặt:
    pip install requests beautifulsoup4 html2text
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import html2text

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

# Headers giả lập trình duyệt Chrome thật
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/",
}

# CSS selectors để lấy nội dung chính của từng báo
CONTENT_SELECTORS = {
    "tuoitre.vn":    ["div.content-news-details", "div#main-detail-body", "div.main-content-body"],
    "thanhnien.vn":  ["div.detail-content", "div.content-detail", "div#abody"],
    "vnexpress.net": ["article.fck_detail", "div.Normal"],
    "vtv.vn":        ["div.noidung", "div.article-content"],
    "dantri.com.vn": ["div.singular-content", "div.dt-news__content"],
}

TITLE_SELECTORS = {
    "tuoitre.vn":    ["h1.article-title", "h1"],
    "thanhnien.vn":  ["h1.detail-title", "h1"],
    "vnexpress.net": ["h1.title-detail", "h1"],
    "vtv.vn":        ["h1.article-title", "h1"],
    "dantri.com.vn": ["h1.title-page", "h1"],
}


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)


# Danh sách URL bài báo cần crawl
ARTICLE_URLS = [
    # VnExpress - không bị chặn, có đầy đủ nội dung về vụ Chi Dân & An Tây
    "https://vnexpress.net/khoi-to-ca-si-chi-dan-an-tay-vi-tang-tru-ma-tuy-4827561.html",
    "https://vnexpress.net/huu-tin-linh-7-nam-6-thang-tu-4601099.html",
    "https://vnexpress.net/chau-viet-cuong-linh-13-nam-tu-4365729.html",
    "https://vnexpress.net/nghi-pham-ma-tuy-showbiz-bi-xu-ly-the-nao-4234040.html",
    "https://vnexpress.net/tong-hop-nhung-nghe-si-viet-dinh-lieu-ma-tuy-4012040.html",
]


def get_domain(url: str) -> str:
    """Lấy tên miền từ URL."""
    from urllib.parse import urlparse
    return urlparse(url).netloc.replace("www.", "")


def html_to_markdown(html: str) -> str:
    """Chuyển HTML sang Markdown sạch."""
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.ignore_emphasis = False
    h.body_width = 0  # Không wrap dòng
    return h.handle(html).strip()


def crawl_article_requests(url: str) -> dict:
    """
    Crawl bài báo bằng requests + BeautifulSoup.
    Dùng CSS selector đặc thù của từng báo để lấy nội dung chính.
    """
    domain = get_domain(url)
    content_selectors = CONTENT_SELECTORS.get(domain, ["article", "div.content", "main"])
    title_selectors = TITLE_SELECTORS.get(domain, ["h1"])

    session = requests.Session()
    session.headers.update(HEADERS)

    resp = session.get(url, timeout=20, allow_redirects=True)
    resp.encoding = resp.apparent_encoding or "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    # Lấy tiêu đề
    title = "Unknown"
    for sel in title_selectors:
        tag = soup.select_one(sel)
        if tag and tag.get_text(strip=True):
            title = tag.get_text(strip=True)
            break
    if title == "Unknown":
        og_title = soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "Unknown")

    # Lấy nội dung bài báo
    content_html = ""
    for sel in content_selectors:
        tag = soup.select_one(sel)
        if tag and len(tag.get_text(strip=True)) > 200:
            content_html = str(tag)
            break

    if not content_html:
        # Fallback: lấy thẻ <article> hoặc <main>
        for fallback in ["article", "main", "div#content", "div.container"]:
            tag = soup.select_one(fallback)
            if tag and len(tag.get_text(strip=True)) > 200:
                content_html = str(tag)
                break

    content_md = html_to_markdown(content_html) if content_html else ""
    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": content_md,
        "_method": "requests",
    }


async def crawl_article_browser(url: str) -> dict:
    """Fallback: crawl bằng browser (crawl4ai) nếu requests thất bại."""
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    browser_cfg = BrowserConfig(
        browser_type="chromium",
        headless=True,
        user_agent=HEADERS["User-Agent"],
    )
    run_cfg = CrawlerRunConfig(
        wait_until="domcontentloaded",
        page_timeout=60000,
        delay_before_return_html=3.0,
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(url=url, config=run_cfg)
        md = result.markdown
        if isinstance(md, str):
            content = md
        else:
            content = (
                getattr(md, "raw_markdown", None)
                or getattr(md, "fit_markdown", None)
                or str(md)
            )

        title = result.metadata.get("title", "Unknown") if result.metadata else "Unknown"
        return {
            "url": url,
            "title": title,
            "date_crawled": datetime.now().isoformat(),
            "content_markdown": content or "",
            "_method": "browser",
        }


async def crawl_article(url: str) -> dict:
    """
    Crawl bài báo: thử requests trước, fallback sang browser nếu thất bại.
    """
    try:
        article = crawl_article_requests(url)
        if len(article["content_markdown"]) > 300:
            print(f"    [requests OK] {len(article['content_markdown'])} chars")
            return article
        else:
            print(f"    [requests: noi dung qua ngan ({len(article['content_markdown'])} chars), thu browser...]")
    except Exception as e:
        print(f"    [requests that bai: {e}, thu browser...]")

    # Fallback sang browser
    article = await crawl_article_browser(url)
    print(f"    [browser] {len(article['content_markdown'])} chars")
    return article


async def crawl_all():
    """Crawl toàn bộ bài báo trong ARTICLE_URLS."""
    setup_directory()

    for i, url in enumerate(ARTICLE_URLS, 1):
        print(f"[{i}/{len(ARTICLE_URLS)}] Crawling: {url}")
        try:
            article = await crawl_article(url)
            char_count = len(article["content_markdown"])
            status = "OK" if char_count > 300 else "NGAN"
            print(f"  [{status}] Title: {article['title'][:60]}")
            print(f"  [{status}] Content: {char_count} chars | method: {article.get('_method', '?')}")
        except Exception as e:
            print(f"  [LOI] {e}")
            article = {
                "url": url,
                "title": "Error",
                "date_crawled": datetime.now().isoformat(),
                "content_markdown": f"Loi crawl: {e}",
            }

        # Bỏ key nội bộ trước khi lưu
        article.pop("_method", None)

        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [v] Saved: {filepath}")
        time.sleep(1)  # Nghỉ 1 giây giữa các bài để tránh bị chặn


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if not ARTICLE_URLS:
        print("Hay dien ARTICLE_URLS truoc khi chay!")
    else:
        asyncio.run(crawl_all())
