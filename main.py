from scraper.bulk_scraper import scrape_multiple_websites, save_results
import pandas as pd

while True:

    print("\n==============================")
    print(" Lead Extractor ")
    print("==============================")
    print("1. Scrape Websites")
    print("2. View Saved Leads")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":

        websites = [
            "https://www.w3.org/contact",
            "https://www.python.org/community/",
            "https://www.djangoproject.com/foundation/"
        ]

        results = scrape_multiple_websites(websites)

        save_results(results)

        print("\n✅ Scraping Completed Successfully!")

    elif choice == "2":

        try:
            df = pd.read_csv("data/leads.csv")
            print(df)
        except:
            print("No leads found!")

    elif choice == "3":

        print("Thank you!")
        break

    else:
        print("Invalid Choice")