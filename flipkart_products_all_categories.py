import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36"
}

# Dictionary of category-specific classes for container, title, price, rating
category_classes = {
    "mobile": {
        "container": "_",
        "title": "",
        "price": "",
        "rating": "",
    },
    "shoes": {
        "container": "",
        "title": "",
        "price": "",
        "rating": "",
    },
    "laptop": {
        "container": "",
        "title": "",
        "price": "",
        "rating": "",

    }

    # Add more categories & their classes here
}

def scrape_category(category, classes, max_pages=50):
    all_products = []

    for page in range(1, max_pages + 1):
        url = f"https:///search?q={category}&page={page}"
        print(f"Scraping '{category}' - page {page}")
        
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to fetch page {page} of {category}. Status code: {response.status_code}")
            break
        
        soup = BeautifulSoup(response.content, "html.parser")
        containers = soup.find_all("div", class_=classes["container"])
        
        if not containers:
            print(f"No products found on page {page} for {category}. Possibly last page.")
            break
        
        for block in containers:
            title_tag = block.find("div", class_=classes["title"])
            price_tag = block.find("div", class_=classes["price"])
            rating_tag = block.find("div", class_=classes["rating"])
            
            if title_tag and price_tag:
                title = title_tag.text.strip()
                price = price_tag.text.strip()
                rating = rating_tag.text.strip() if rating_tag else None
                
                product = {
                    "category": category,
                    "title": title,
                    "price": price,
                    "rating": rating
                }
                all_products.append(product)
                print(f"  + {title} | {price} | Rating: {rating}")

        time.sleep(2)  # Be polite with 2-second delay

    return all_products

def main():
    all_data = []
    max_pages = 50
    
    for category, classes in category_classes.items():
        print(f"\nStarting scrape for category: {category}")
        category_data = scrape_category(category, classes, max_pages=max_pages)
        print(f"Collected {len(category_data)} products for category '{category}'")
        all_data.extend(category_data)
    
    df = pd.DataFrame(all_data)
    df.to_csv("flipkart_products_all_categories.csv", index=False)
    print("\nScraping finished. Data saved to flipkart_products_all_categories.csv")

if __name__ == "__main__":
    main()
