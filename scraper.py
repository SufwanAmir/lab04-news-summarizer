from urllib.parse import quote_plus, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


BASE_URL = "https://techcrunch.com"


def create_driver():
    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1365,1000")

    return webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),
        options=options
    )


def search_article(keyword: str) -> dict:
    driver = create_driver()

    try:
        search_url = f"{BASE_URL}/search/{quote_plus(keyword)}/"
        driver.get(search_url)

        WebDriverWait(driver, 20).until(
            lambda d: d.find_elements(By.TAG_NAME, "body")
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")
        article_url = None

        for link in soup.find_all("a", href=True):
            href = link["href"]
            title_text = link.get_text(" ", strip=True)

            if not href or not title_text:
                continue

            parsed = urlparse(href)
            path = parsed.path

            if (
                parsed.netloc == "techcrunch.com"
                and len(path.strip("/").split("/")) >= 2
                and path.strip("/").split("/")[0].isdigit()
                and path.strip("/").split("/")[1].isdigit()
            ):
                article_url = href
                break

        if not article_url:
            raise ValueError(
                f"No TechCrunch article found for keyword: {keyword}"
            )

        driver.get(article_url)

        WebDriverWait(driver, 20).until(
            lambda d: d.find_elements(By.TAG_NAME, "body")
        )

        soup = BeautifulSoup(driver.page_source, "html.parser")

        title_tag = soup.find("h1")
        title = title_tag.get_text(" ", strip=True) if title_tag else keyword

        content = (
            soup.select_one("div.entry-content")
            or soup.select_one("article")
            or soup.find("main")
        )

        if content:
            for element in content.select("script, style, nav, footer, aside"):
                element.decompose()

            paragraphs = [
                p.get_text(" ", strip=True)
                for p in content.find_all("p")
            ]
            text = "\n".join(p for p in paragraphs if p)
        else:
            text = ""

        if len(text.split()) < 30:
            raise ValueError(
                f"Insufficient article text extracted from {article_url}"
            )

        return {
            "title": title,
            "url": article_url,
            "text": text,
        }

    finally:
        driver.quit()
