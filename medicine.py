import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Base URL for scraping
base_url = "https://www.1mg.com/categories/health-conditions/"
categories = ['diabetes-1', 'cardiac-care-35', 'stomach-care-30', 'liver-care-39', 'bone-joint-muscle-care-34', 'kidney-care-40', 'derma-care-1183', 'respiratory-care-14', 'eye-care-31']
medicine_data = []

for category in categories:
    page_num = 1
    total_medicines = 0
    print(f"Scraping category: {category}")

    while total_medicines < 40:
        url = f"{base_url}{category}?filter=true&page={page_num}"
        driver.get(url)
        time.sleep(10)  # Wait for the page to load

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for med in soup.find_all('div', class_='style__product-box___liepi'):
            try:
                name = med.find('div', class_='style__pro-title___2QwJy').text.strip()
                price = med.find('div', class_='style__price-tag___cOxYc').text.strip()
                discount = med.find('span', class_='style__off-badge___2JaF-').text.strip() if med.find('span', class_='style__off-badge___2JaF-') else 'No discount'
                rating = med.find('div', class_='CardRatingDetail__ratings___1q8zc').text.strip() if med.find('div', class_='CardRatingDetail__ratings___1q8zc') else 'No rating'
                
                medicine_data.append({
                    'Name': name,
                    'Price': price,
                    'Discount': discount,
                    'Rating': rating,
                    'Category': category
                })
                total_medicines += 1
            except:
                continue

        page_num += 1

# Close WebDriver
driver.quit()

# Convert to DataFrame
df = pd.DataFrame(medicine_data)

# Data Cleaning
# Remove currency symbols and convert 'Price' to float
df["Price"] = df["Price"].astype(str).str.replace("MRP", "").str.replace("₹", "").str.replace(",", "").astype(float)

# Clean 'Discount' column
df["Discount"] = df["Discount"].astype(str).str.replace("% off", "").replace("No discount", np.nan).astype(float)

# Clean 'Rating' column
df["Rating"] = df["Rating"].astype(str).str.extract(r"([\d\.]+)").astype(float)

# Summary Statistics
print("Summary Statistics:")
print(df.describe())

# Set style for plots
sns.set_theme(style="whitegrid")

# Create subplots for visualization
fig, axes = plt.subplots(3, 1, figsize=(12, 18))

# Category-wise Price Distribution using Box Plot
sns.boxplot(x="Category", y="Price", data=df, ax=axes[0], palette="Blues")
axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45, ha="right")
axes[0].set_title("Price Distribution by Category")

# Category-wise Discount Distribution using Box Plot
sns.boxplot(x="Category", y="Discount", data=df, ax=axes[1], palette="Greens")
axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha="right")
axes[1].set_title("Discount Distribution by Category")

# Category-wise Rating Distribution using Strip Plot
sns.stripplot(x="Category", y="Rating", data=df, ax=axes[2], palette="Reds", jitter=True)
axes[2].set_xticklabels(axes[2].get_xticklabels(), rotation=45, ha="right")
axes[2].set_title("Rating Distribution by Category")

# Adjust layout and save plots
plt.tight_layout()
plt.savefig("output.png")
plt.show()
