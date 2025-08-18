import requests
import csv
import json

API_KEY = "be18ad2d5dmsh810c34b85ef8084p1fa253jsnc78289ebfd0e"  
BASE_URL = "https://real-time-amazon-data.p.rapidapi.com"
HEADERS = {
    "x-rapidapi-host": "real-time-amazon-data.p.rapidapi.com",
    "x-rapidapi-key": API_KEY
}


def search_products(query="Phone", country="US", page=1):
    url = f"{BASE_URL}/search"
    params = {
        "query": query,
        "country": country,
        "page": page
    }
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    total_products = data.get("total_products") or data.get("data", {}).get("total_products", 0)
    products = data.get("products") or data.get("data", {}).get("products", [])
    return total_products, products


def get_product_details(asin, country="US"):
    url = f"{BASE_URL}/product-details"
    params = {
        "asin": asin,
        "country": country
    }
    response = requests.get(url, headers=HEADERS, params=params)

    try:
        data = response.json()
    except ValueError:
        print("Couldn't parse JSON: ")
        print(response.text)
        return {}

    return data.get("data", {})


def get_product_reviews(asin, country="US", page=1):
    url = f"{BASE_URL}/product-reviews"
    params = {
        "asin": asin,
        "country": country,
        "page": page,
        "sort_by": "TOP_REVIEWS",
        "star_rating": "ALL",
        "verified_purchases_only": "false",
        "images_or_videos_only": "false",
        "current_format_only": "false"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    try:
        data = response.json()
    except ValueError:
        print("⚠️ Couldn't parse JSON:")
        print(response.text)
        return []

    print("\n Full product-reviews response:")
    print(json.dumps(data, indent=2))

    if "reviews" in data:
        return data["reviews"]
    elif "data" in data and isinstance(data["data"], list):
        return data["data"]
    elif "data" in data and "reviews" in data["data"]:
        return data["data"]["reviews"]
    else:
        return []


def get_best_sellers(category="software", country="US", page=1):
    url = f"{BASE_URL}/best-sellers"
    params = {
        "category": category,
        "type": "BEST_SELLERS",
        "country": country,
        "page": page
    }
    response = requests.get(url, headers=HEADERS, params=params)

    try:
        response.raise_for_status()  
        data = response.json()
    except Exception as e:
        print("Failed to get or parse JSON:", e)
        print("Raw response:", response.text)
        return []

    print("Full best sellers response:")
    print(json.dumps(data, indent=2))

    bestsellers = data.get("data", {}).get("bestsellers", [])
    if not bestsellers:
        print("No best sellers found in the response.")
        return []

    return bestsellers  
            
def save_to_csv(products, filename="products.csv"):
    if not products:
        print("No products to save.")
        return

    fieldnames = ["product_title", "asin", "product_price", "product_url"]

    try:
        with open(filename, mode="w", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for p in products:
                writer.writerow({
                    "product_title": p.get("product_title", "No Title"),
                    "asin": p.get("asin", "N/A"),
                    "product_price": p.get("product_price", "N/A"),
                    "product_url": p.get("product_url", "N/A")
                })
        print(f" Saved {len(products)} products to {filename}")
    except Exception as e:
        print(f" Error saving CSV: {e}")
    
def main():
    while True:
        print("\n Amazon Product Explorer")
        print("1.  Search Products")
        print("2.  Product Details")
        print("3.  Product Reviews")
        print("4.  Best Sellers")
        print("5.  Exit")

        choice = input("Choose an option (1-5): ")

        if choice == "1":
            query = input("Enter product search query (default 'Phone'): ") or "Phone"
            country = input("Enter country code (default 'US'): ") or "US"
            page_input = input("Enter page number (default 1): ")
            page = int(page_input) if page_input.isdigit() else 1

            total, products = search_products(query=query, country=country, page=page)
            print(f"\n Total Products Found: {total}")

            if not products:
                print(" No products found.")
            else:
                for i, p in enumerate(products[:5], 1):
                    print(f"\n[{i}] {p.get('product_title', 'No Title')}")
                    print(f"ASIN: {p.get('asin')}")
                    print(f"Price: {p.get('product_price', 'N/A')}")
                    print(f"URL: {p.get('product_url', 'N/A')}")
                save_csv = input("\n Do you want to save all results to CSV? (y/n): ").strip().lower()
                if save_csv == 'y':
                    save_to_csv(products)    

        elif choice == "2":
            asin = input("Enter product ASIN: ")
            country = input("Enter country code (default 'US'): ") or "US"
            details = get_product_details(asin, country)
            if not details:
                print("No product details found.")
                continue

            print("\n Product Details:")
            print(f"Title: {details.get('product_title')}")
            print(f"Brand: {details.get('product_byline')}")
            print(f"Rating: {details.get('product_star_rating')}")

            features = details.get('about_product')
            if features:
                print("Features:")
                for feature in features:
                    print(f"- {feature}")
            else:
                print("Features: None")

            print(f"Description: {details.get('product_description')}")

        elif choice == "3":
           MAX_REVIEW_LENGTH = 300
           asin = input("Enter product ASIN: ")
           country = input("Enter country code (default 'US'): ") or "US"
           page_input = input("Enter page number (default 1): ")
           page = int(page_input) if page_input.isdigit() else 1

           reviews = get_product_reviews(asin, country, page)

           if not reviews:
               print(" No reviews found.")
           else:
               print("\n Product Reviews:")
               for i, r in enumerate(reviews[:3], 1):
                   print(f"\nReview {i}:")
                   print(f"Author: {r.get('review_author', 'N/A')}")
                   print(f"Rating: {r.get('review_star_rating', 'N/A')}")
                   print(f"Title: {r.get('review_title', 'No Title')}")
                   print(f"Content: {r.get('review_comment', 'No Content')}")
                   content = r.get('review_comment') or "NO Content"
                   if len(content) > MAX_REVIEW_LENGTH:
                       content = content[:MAX_REVIEW_LENGTH].rstrip() + "..."
                   print(f'Content: {content}')    
        

        elif choice == "4":
            category = input("Enter category ID (default 'software'): ") or "software"
            country = input("Enter country code (default 'US'): ") or "US"
            page_input = input("Enter page number (default 1): ")
            page = int(page_input) if page_input.isdigit() else 1

            bestsellers = get_best_sellers(category, country, page)
            if not bestsellers:
                print(" No best sellers found.")
            else:
                print("\n Best Sellers:")
                for i, p in enumerate(bestsellers[:5], 1):
                    print(f"\n[{i}] {p.get('title', 'No Title')}")
                    print(f"ASIN: {p.get('asin', 'N/A')}")
                    print(f"Price: {p.get('price', {}).get('raw', 'N/A')}")
                    print(f"URL: {p.get('url', 'N/A')}")

        elif choice == "5":
            print(" Exiting... See you next time!")
            break
        else:
            print(" Invalid choice. Please select a number between 1 and 5.")

if __name__ == "__main__":
    main()
