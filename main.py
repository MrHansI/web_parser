import requests
import csv
from bs4 import BeautifulSoup
from progress.bar import Bar

BASE_URL = "https://www.ruspitomniki.ru"

CSV_FILE = 'flowers.csv'
with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['title_ru', 'title_en', 'images', 'description', 'characteristics'])

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return None

def save_to_csv(data):
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def scrape():
    url_categories = f"{BASE_URL}/catalog/"
    html_categories = fetch_html(url_categories)

    if not html_categories:
        print("Не удалось загрузить категории.")
        return

    categories = html_categories.find_all("a", {"class": "d-block mb-1 fs-4 fw-700 text-primary"})
    barCategories = Bar('Categories', max=len(categories))

    for category in categories:
        category_url = BASE_URL + category.get("href")
        html_subcategories = fetch_html(category_url)

        if not html_subcategories:
            barCategories.next()
            continue

        subcategories = html_subcategories.find_all("a", {"class": "d-block mb-1 fs-4 fw-700 text-primary"})
        barSubcategories = Bar('Subcategories', max=len(subcategories))

        for subcategory in subcategories:
            subcategory_url = BASE_URL + subcategory.get("href")
            html_flowers = fetch_html(subcategory_url)

            if not html_flowers:
                barSubcategories.next()
                continue

            flowers = html_flowers.find_all("a", {"class": "d-block mb-1 fs-4 fw-700 text-primary"})

            for flower in flowers:
                flower_url = BASE_URL + flower.get("href")
                html_flower = fetch_html(flower_url)

                if not html_flower:
                    continue

                try:
                    flower_title_ru = html_flower.find("h1").text.strip() if html_flower.find("h1") else "N/A"
                    flower_title_en = html_flower.find("div", {"class": "mb-4 fs-3 fw-500"})
                    flower_title_en = flower_title_en.text.strip() if flower_title_en else "N/A"
                    flower_imgs = [img.get("src") for img in html_flower.find_all("img", {"class": "w-100"})]
                    flower_description = html_flower.find("div", {"class": "col text-justify"})
                    flower_description = flower_description.text.strip() if flower_description else "N/A"
                    flower_characteristics = html_flower.find("tbody")
                    flower_characteristics = flower_characteristics.text.strip() if flower_characteristics else "N/A"

                    save_to_csv([
                        flower_title_ru,
                        flower_title_en,
                        "; ".join(flower_imgs),
                        flower_description,
                        flower_characteristics,
                    ])
                except Exception as e:
                    print(f"Ошибка при обработке {flower_url}: {e}")

            barSubcategories.next()

        barCategories.next()

scrape()
print("\nСкрапинг завершен, данные сохранены в", CSV_FILE)
