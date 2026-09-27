import requests
import xml.etree.ElementTree as ET
import re
from html import unescape

FEED_URL = "https://www.sarkariexam.com/feed/"

headers = {
    "User-Agent": "SarkariJobBot/1.0"
}


def clean_text(text):
    if not text:
        return ""

    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


print("======================================")
print("SARKARI EXAM RSS TEST")
print("======================================")

response = requests.get(
    FEED_URL,
    headers=headers,
    timeout=30
)

print("STATUS:", response.status_code)
print("CONTENT TYPE:", response.headers.get("content-type"))
print("FEED SIZE:", len(response.content))

response.raise_for_status()

root = ET.fromstring(response.content)

channel = root.find("channel")

if channel is None:
    raise Exception("RSS channel not found")

items = channel.findall("item")

print("TOTAL RSS ITEMS:", len(items))

print("\n========== JOB LIST ==========\n")

for i, item in enumerate(items[:10], start=1):

    title_element = item.find("title")
    link_element = item.find("link")

    title = clean_text(
        title_element.text
        if title_element is not None
        else ""
    )

    link = (
        link_element.text.strip()
        if link_element is not None and link_element.text
        else ""
    )

    print(f"{i}. {title}")
    print(f"   {link}")
    print()

print("======================================")
print("✅ RSS TEST COMPLETED")
print("======================================")
