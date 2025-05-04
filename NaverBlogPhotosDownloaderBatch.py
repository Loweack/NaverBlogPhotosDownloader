import os
import re
import requests
import time
import argparse
import logging

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import unquote

# -------------------- Configuration --------------------

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; "
    "Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
}

logging.basicConfig(
    filename='download.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# -------------------- WebDriver Init --------------------

def Iniwebdriver():
    options = webdriver.ChromeOptions()  # type: ignore
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)  # type: ignore

# -------------------- Count Images --------------------

def Countsofphotos(driver, url):
    for attempt in range(3):
        try:
            driver.get(url)
            driver.switch_to.frame("mainFrame")
            WebDriverWait(driver, timeout=5).until(
                EC.presence_of_element_located((By.ID, "whole-body"))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            imgs = soup.find_all("a", class_="se-module-image-link __se_image_link __se_link")
            imgcounts = len(imgs)
            print(f"There are {imgcounts} photos found")
            logging.info(f"{url}: Found {imgcounts} photos.")
            return imgcounts
        except Exception as e:
            logging.warning(f"{url}: Attempt {attempt + 1} - Error counting photos: {e}")
            time.sleep(1)
    logging.error(f"{url}: Failed to count photos after 3 attempts.")
    return 0

# -------------------- Download Images --------------------

def Downloadphotos(driver, imgcounts, url):
    dir_path = url.split("/")[-1]
    saved_dir = f"images/{dir_path}"

    if not os.path.exists(saved_dir):
        os.makedirs(saved_dir)

    success_count = 0
    failure_count = 0

    for img in range(imgcounts):
        photo_url = f"{url}?photoView={img}"
        img_url = None

        # Retry: extract image URL
        for attempt in range(3):
            try:
                driver.get(photo_url)
                driver.switch_to.frame("mainFrame")
                time.sleep(3)
                soup = BeautifulSoup(driver.page_source, "html.parser")
                img_tag = soup.find("img", class_="cpv__img cpv__fade")
                if img_tag:
                    img_url = unquote(img_tag.get("data-src"))
                    break
                else:
                    logging.warning(f"{photo_url}: Attempt {attempt + 1} - No image found.")
            except Exception as e:
                logging.warning(f"{photo_url}: Attempt {attempt + 1} - Error extracting image: {e}")
            time.sleep(1)

        if not img_url:
            logging.error(f"{photo_url}: Failed to extract image after 3 attempts.")
            failure_count += 1
            continue

        file_name = unquote(img_url.split("?")[0].split("/")[-1].split(".")[0])
        file_extension = img_url.split("?")[0].split(".")[-1]

        # Handle existing file names by incrementing
        base_output_path = os.path.join(saved_dir, f"{file_name}.{file_extension}")
        output_path = base_output_path
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(saved_dir, f"{file_name}_{counter}.{file_extension}")
            counter += 1

        # Retry: download image
        success = False
        for attempt in range(3):
            try:
                response = requests.get(img_url, headers=HEADERS, stream=True)
                if response.status_code == 200:
                    with open(output_path, "wb") as file:
                        file.write(response.content)
                    print(f"{img + 1}/{imgcounts} Downloaded: {os.path.basename(output_path)}")
                    logging.info(f"{photo_url}: Downloaded successfully.")
                    success = True
                    success_count += 1
                    break
                else:
                    logging.warning(f"{img_url}: Attempt {attempt + 1} - HTTP {response.status_code}")
            except Exception as e:
                logging.warning(f"{img_url}: Attempt {attempt + 1} - Download exception: {e}")
            time.sleep(1)

        if not success:
            logging.error(f"{img_url}: Failed to download after 3 attempts.")
            failure_count += 1

    print("Download finished")
    logging.info(f"{url}: Download complete — Success: {success_count}, Failed: {failure_count}")

# -------------------- Main Script --------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from URLs listed in a text file.")
    parser.add_argument("filename", type=str, help="The text file containing the URLs.")
    args = parser.parse_args()

    with open(args.filename, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]

    for input_url in urls:
        pattern = r"https:\/\/blog.naver.com\/edament\/[0-9]{12}"
        if re.fullmatch(pattern, input_url):
            URL = input_url
        else:
            try:
                URL = r"https://blog.naver.com/edament/" + input_url.split("No=")[1][:12]
            except Exception as e:
                print(f"Invalid URL format skipped: {input_url}, error: {e}")
                logging.warning(f"{input_url}: Skipped - invalid format. Error: {e}")
                continue

        print(f"\nProcessing URL: {URL}")
        logging.info(f"Started processing: {URL}")
        driver = Iniwebdriver()

        try:
            imgcounts = Countsofphotos(driver, URL)
            if imgcounts > 0:
                Downloadphotos(driver, imgcounts, URL)
            else:
                print(f"No images found for {URL}")
                logging.warning(f"{URL}: No images found.")
        except Exception as e:
            print(f"Error with URL {URL}: {e}")
            logging.error(f"{URL}: Unexpected error - {e}")
        finally:
            driver.quit()
            logging.info(f"{URL}: WebDriver session closed.")
