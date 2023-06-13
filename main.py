import requests
import time

from hyper.contrib import HTTP20Adapter
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()

service = Service(executable_path="D:\\Python\\chromedriver\\chromedriver.exe")  # Browser Chrome v114.0.5735.110
driver = webdriver.Chrome(service=service, options=options)

url = "https://www.avito.ru/"
print("Введите запрос на русском языке:")
search = input()
print("Введите город:")
location = input()

try:
    # Открытие страницы
    driver.get(url=url)
    time.sleep(3)

    # Изменение локации
    location_button = driver.find_element(By.CSS_SELECTOR, '[data-marker="search-form/change-location"]')
    location_button.click()
    location_input = driver.find_element(By.CSS_SELECTOR, '[data-marker="popup-location/region/input"]')
    time.sleep(1)

    location_input_value = location_input.get_attribute('value')

    # Удаление города в поле ввода (определяет сайт)
    i = 0
    while i < len(location_input_value):
        location_input.send_keys(Keys.BACK_SPACE)
        i = i + 1

    time.sleep(0.5)
    # Запись города
    location_input.send_keys(location)
    time.sleep(0.5)

    try:
        # Выбор города в выпадающем списке
        location_li = driver.find_element(By.CSS_SELECTOR, '[data-marker="suggest(0)"]')
        location_li.click()
        time.sleep(0.8)

        button_show_ads = driver.find_element(By.XPATH, '//*[@id="smallRadiusTab"]/div/div/div[2]/div[2]/div['
                                                        '2]/button/span')
        driver.execute_script("arguments[0].click();", button_show_ads)
    except NoSuchElementException:
        print("Введен некорректный населенный пункт")

    # Ввод критерия поиска
    search_input = driver.find_element(By.CSS_SELECTOR, '[data-marker="search-form/suggest"]')
    search_input.click()
    search_input.send_keys(search)

    submit_button = driver.find_element(By.CSS_SELECTOR, '[data-marker="search-form/submit-button"]')
    submit_button.click()

    # Сбор ссылок
    link_list = []
    while True:
        elements = (driver.find_elements(By.CLASS_NAME, 'iva-item-sliderLink-uLz1v'))

        for link in elements:
            link_list.append(link.get_attribute('href'))

        try:
            next_page = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Следующая страница"]')
            next_page.click()
        except NoSuchElementException:
            break

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, likeGecko) Chrome/114.0.0.0 '
                      'Safari/537.36 '
    }

    # Проход по ссылкам и сбор данных в объект
    all_ad = {}
    for link in link_list:
        session = requests.Session()
        session.mount('https://', HTTP20Adapter())
        req = session.get(link)
        src = req.text
        soup = BeautifulSoup(src, 'lxml')

        ad_number_array = soup.find(attrs={'data-marker': 'item-view/item-id'}).text.split()
        ad_number = ad_number_array[1]
        all_ad["ad_number"] = ad_number

        all_ad["name"] = soup.find(class_='title-info-title-text').text
        all_ad["price"] = soup.find(attrs={'itemprop': 'price'})['content']
        all_ad["address"] = soup.find(attrs={'itemprop': 'address'}).text
        all_ad["description"] = soup.find(attrs={'data-marker': 'item-view/item-description'}).text

        publication_date = soup.find(attrs={'data-marker': 'item-view/item-date'}).text
        publication_date = publication_date[3:len(publication_date)]
        all_ad["publication_date"] = publication_date

        views_count = soup.find(attrs={'data-marker': 'item-view/total-views'}).text
        views_count = views_count[1:len(views_count) - 1]
        all_ad["views_count"] = views_count

        all_ad["link_to_ad"] = link
        all_ad["ad status"] = 'активно'

except Exception as ex:
    print(ex)
finally:
    driver.close()
    driver.quit()
