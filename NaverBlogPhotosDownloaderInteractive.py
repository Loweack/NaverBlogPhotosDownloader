import os
import re
import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import unquote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; "
    "Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
}


def Iniwebdriver():
    options = webdriver.ChromeOptions()  # type: ignore
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")  # disable UI
    options.add_argument(
        "--disable-gpu"
    )  # disable GPU, usually work with --no-headless
    driver = webdriver.Chrome(options=options)  # type: ignore
    return driver


# find out how many photos
def Countsofphotos(driver, url):
    try:
        driver.get(url)
        driver.switch_to.frame("mainFrame")
        WebDriverWait(driver, timeout=5).until(
            EC.presence_of_element_located((By.ID, "whole-body"))
        )
        # time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        imgs = soup.find_all(
            "a", class_="se-module-image-link __se_image_link __se_link"
        )
        imgcounts = len(imgs)
        print(f"There're {imgcounts} photos found")
        return imgcounts
    except Exception as e:
        print(f"Counting the photos got wrong! {e}")


def Downloadphotos(driver, imgcounts, url):

    dir_path = url.split("/")[-1]

    if not os.path.exists(f"images/{dir_path}"):
        os.makedirs(f"images/{dir_path}")

    for img in range(imgcounts):
        try:
            # the photoview url
            photo_url = f"{url}?photoView={img}"
            driver.get(photo_url)
            driver.switch_to.frame("mainFrame")
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            img_url = unquote(
                soup.find("img", class_="cpv__img cpv__fade").get("data-src")  # type: ignore
            )
            # print(f'Original image url: {img_url}')
        except Exception as e:
            print(f"the {photo_url} was wrong! {e}")

        file_name = unquote(img_url.split("?")[0].split("/")[-1].split(".")[0])
        print(f"file name: {file_name}")

        file_extension = img_url.split("?")[0].split(".")[-1]

        output_path = os.path.join(
            f"images/{dir_path}", f"{file_name}.{file_extension}"
        )

        download_photo = requests.get(img_url, headers=HEADERS, stream=True)

        if download_photo.status_code == 200:
            with open(output_path, "wb") as file:
                file.write(download_photo.content)
            print(f"{img + 1}/{imgcounts} downloading{'.' * 20}\n")
        else:
            print(
                f"download {file_name} failed!HTTP status code: {download_photo.status_code}"
            )

    print("Download finished")
    driver.quit()


if __name__ == "__main__":

    input_url = input("Enter the url you want to download pics: ")
    pattern = r"https:\/\/blog.naver.com\/edament\/[0-9]{12}"
    if re.fullmatch(pattern, input_url):
        print(f"The url you want to download is {input_url}")
    else:
        URL = r"https://blog.naver.com/edament/" + input_url.split("No=")[1][:12]
        print(f"The url you want to download is {input_url}")

    webdriver = Iniwebdriver()

    try:
        Downloadphotos(webdriver, Countsofphotos(webdriver, URL), URL)
    except Exception as e:
        print(f"Something went wrong! {e}")
    finally:
        webdriver.quit()
