import requests
from bs4 import BeautifulSoup
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


# === Connect to MongoDB ===
def connect_to_db():
    client = MongoClient(MONGO_URI)
    db = client["quotes_db"]
    return db["quotes"], db["authors"]


def scrape_quotes():
    base_url = "http://quotes.toscrape.com"
    all_quotes = []
    all_authors = []

    page = 1
    while True:
        url = f"{base_url}/page/{page}/"
        r = requests.get(url)
        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "html.parser")
        quotes = soup.find_all("div", class_="quote")
        if not quotes:
            break

        for q in quotes:
            text_tag = q.find("span", class_="text")
            author_tag = q.find("small", class_="author")
            tag_links = q.find_all("a", class_="tag")
            author_link_tag = q.find("a")

            if not text_tag or not author_tag or not author_link_tag:
                continue

            text = text_tag.get_text(strip=True)
            author = author_tag.get_text(strip=True)
            tags = [t.get_text(strip=True) for t in tag_links]
            author_link = str(author_link_tag.get("href", ""))
            full_link = f"{base_url}{author_link}"

            all_quotes.append({
                "tags": tags,
                "author": author,
                "quote": text
            })

            if full_link not in [a["link"] for a in all_authors]:
                all_authors.append({"name": author, "link": full_link})

        print(f"Parsed page {page}")
        page += 1

    return all_quotes, all_authors


def scrape_authors(authors_list):
    authors_data = []
    for a in authors_list:
        r = requests.get(a["link"])
        soup = BeautifulSoup(r.text, "html.parser")
        fullname_tag = soup.find("h3", class_="author-title")
        born_date_tag = soup.find("span", class_="author-born-date")
        born_location_tag = soup.find("span", class_="author-born-location")
        description_tag = soup.find("div", class_="author-description")

        if not fullname_tag:
            continue

        fullname = fullname_tag.get_text(strip=True)
        born_date = born_date_tag.get_text(strip=True) if born_date_tag else ""
        born_location = born_location_tag.get_text(strip=True) if born_location_tag else ""
        description = description_tag.get_text(strip=True) if description_tag else ""

        authors_data.append({
            "fullname": fullname,
            "born_date": born_date,
            "born_location": born_location,
            "description": description
        })

    return authors_data


# === Save data to JSON files ===
def save_to_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f" Saved {filename}")


# === Import JSON data to MongoDB ===
def import_to_mongo(quotes_col, authors_col, quotes, authors):
    quotes_col.delete_many({})
    authors_col.delete_many({})
    quotes_col.insert_many(quotes)
    authors_col.insert_many(authors)
    print("Data successfully imported into MongoDB!")



def main():
    print("Starting scraping...")
    quotes_col, authors_col = connect_to_db()

    quotes, authors_links = scrape_quotes()
    authors = scrape_authors(authors_links)

    save_to_json("quotes.json", quotes)
    save_to_json("authors.json", authors)

    import_to_mongo(quotes_col, authors_col, quotes, authors)
    print("Done!")


if __name__ == "__main__":
    main()
