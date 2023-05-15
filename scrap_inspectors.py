from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import requests
import certifi
import time

options = Options()
options.add_argument('--incognito')
driver = webdriver.Chrome(options=options)

all_data = []

# Хардкод на раздел "где мой квартальный" на сайте Екатеринбург.рф
eka_link = 'https://xn--80acgfbsl1azdqr.xn--p1ai/справка/квартальные#tab3'

from selenium.webdriver.support.ui import Select


def update_quarter_inspectors_data(quarters_link):
    driver.get(quarters_link)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'qly-districts-select')))
    district_select = driver.find_element(By.CSS_SELECTOR, '.qly-districts-select select')
    district_select_object = Select(district_select)

    district_names = [option.text for option in district_select_object.options[1:]]

    for i, district_name in enumerate(district_names):
        try:
            district_select_object.select_by_visible_text(district_name)
            time.sleep(2)  # Добавляем задержку, чтобы дать странице время загрузиться
            page_content = driver.find_element(By.CLASS_NAME, 'qly-search-table')
            inspector_elements = page_content.find_elements(By.CLASS_NAME, 'qly-search-cell.js-district-qly a')

            for inspector_element in inspector_elements:
                inspector_href = inspector_element.get_attribute('href')
                time.sleep(7)
                inspector_data = parse_inspector_card(inspector_href)
                inspector_data['district'] = district_name
                all_data.append(inspector_data)

            print(f"Processed district: {district_name}")

            # Check if there are more districts
            if i < len(district_names) - 1:
                driver.get(quarters_link)  # Navigate back to the original link
                wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'qly-districts-select')))
                district_select = driver.find_element(By.CSS_SELECTOR, '.qly-districts-select select')
                district_select_object = Select(district_select)
                district_select_object.select_by_visible_text(district_names[i + 1])
                time.sleep(2)  # Add a delay to allow the page to load

        except Exception as e:
            print(f"Error processing district '{district_name}': {str(e)}")
            continue

    save_data_to_csv(all_data, 'data.csv')


# TODO регулярка которая обрезает хвосты и оставляет только #userId инспектора для подставления в ссылку
# TODO возвращаемый map_code приходит в виде координат прямоугольника, нужно научиться его читать
def parse_inspector_card(url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.qly-card')))
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    inspector_data = {}

    # Извлечение имени
    name_element = soup.find('h3')
    if name_element:
        inspector_data['name'] = name_element.text.strip()

    # Извлечение телефона
    phone_element = soup.find('div', class_='qly-card-coord')
    if phone_element:
        inspector_data['phone'] = phone_element.text.strip()

    # Извлечение закрепленного имущественного комплекса
    complex_name_element = soup.find('div', string='Закреплённый имущественный комплекс:')
    if complex_name_element:
        inspector_data['complex_name'] = complex_name_element.find_next('div', class_='qly-card-coord').text.strip()

    # Извлечение карты
    map_element = soup.find('path', class_='leaflet-interactive')
    if map_element:
        inspector_data['map_code'] = map_element['d']

    # Извлечение границ участка
    boundaries_element = soup.find('div', class_='qly-card-info-photo', string='Границы имущественного комплекса:')
    if boundaries_element:
        boundaries_text = boundaries_element.find_next('div', class_='qly-card-info-info').p.get_text()
        # boundaries_list = boundaries_text.split(' ')
        inspector_data['boundaries'] = boundaries_text

    return inspector_data


def save_data_to_csv(data, filename):
    fieldnames = ['district', 'name', 'phone', 'complex_name', 'map_code', 'boundaries']

    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def get_inspector_data(url):
    url = 'https://xn--80acgfbsl1azdqr.xn--p1ai/data-send/quarterly/qlydata'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,pl;q=0.5,it;q=0.4',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': 'newportal=729ba6f85272f2e1b44504239d70a651; _ym_uid=1683803320120712192; _ym_d=1683803320; sputnik_session=1684077816368|1; _ym_isad=1',
        'DNT': '1',
        'Origin': 'https://xn--80acgfbsl1azdqr.xn--p1ai',
        'Referer': 'https://xn--80acgfbsl1azdqr.xn--p1ai/%D1%81%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0/%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    data = {
        'user_id': '3b5af31e-b6a9-4fcf-8268-8f92bb52ea42',
        'page': '1'
    }

    return requests.post(url, headers=headers, data=data, verify=False)

# try:
#     update_quarter_inspectors_data(eka_link)
# except Exception as e:
#     print(e)
#
# print(parse_inspector_card(
#     'https://xn--80acgfbsl1azdqr.xn--p1ai/%D1%81%D0%BF%D1%80%D0%B0%D0%B2%D0%BA%D0%B0/%D0%BA%D0%B2%D0%B0%D1%80%D1%82%D0%B0%D0%BB%D1%8C%D0%BD%D1%8B%D0%B5#userId=3b5af31e-b6a9-4fcf-8268-8f92bb52ea42'))
