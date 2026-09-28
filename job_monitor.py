import requests
import xml.etree.ElementTree as ET
import json
import hashlib
import re
from html import unescape

FEED_URL = "https://www.sarkariexam.com/feed/"
SEEN_FILE = "seen_jobs.json"
MESSAGE_FILE = "latest_jobs.txt"

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


def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as file:
        json.dump(
            sorted(seen),
            file,
            ensure_ascii=False,
            indent=2
        )


def make_id(title, link):
    value = (link or title).strip()

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


print("======================================")
print("SARKARI EXAM JOB MONITOR")
print("======================================")

response = requests.get(
    FEED_URL,
    headers=headers,
    timeout=30
)

print("STATUS:", response.status_code)

response.raise_for_status()

root = ET.fromstring(response.content)

channel = root.find("channel")

if channel is None:
    raise Exception("RSS channel not found")

items = channel.findall("item")

print("TOTAL RSS ITEMS:", len(items))

seen = load_seen()

print("ALREADY SEEN:", len(seen))

new_jobs = []

for item in items:

    title_element = item.find("title")
    link_element = item.find("link")
    date_element = item.find("pubDate")

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

    date = (
        date_element.text.strip()
        if date_element is not None and date_element.text
        else ""
    )

    if not title:
        continue

    job_id = make_id(title, link)

    if job_id in seen:
        continue

    new_jobs.append({
        "id": job_id,
        "title": title,
        "link": link,
        "date": date
    })

    seen.add(job_id)


print("NEW JOBS:", len(new_jobs))


# --------------------------------------
# CREATE HINDI MESSAGES
# --------------------------------------

messages = []

for job in new_jobs:

    message = f"""📢 नई सरकारी नौकरी अपडेट

🔹 पोस्ट: {job['title']}

📅 तारीख: {job['date']}

🔗 पूरी जानकारी:
{job['link']}

📌 Sarkari Job Update
"""

    messages.append(message)


if messages:

    with open(
        MESSAGE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n\n━━━━━━━━━━━━━━━━━━━━\n\n".join(messages)
        )

    print("\n========== HINDI MESSAGE ==========\n")

    print(
        "\n\n━━━━━━━━━━━━━━━━━━━━\n\n".join(messages)
    )

    print("\n======================================")
    print("✅ Hindi messages created")
    print("======================================")

else:

    # Empty file बनाना ताकि workflow में file हमेशा मौजूद रहे
    with open(
        MESSAGE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write("")

    print("ℹ️ कोई नई job नहीं मिली।")


save_seen(seen)

print("SEEN JOBS SAVED:", len(seen))
print("✅ MONITOR COMPLETED")
