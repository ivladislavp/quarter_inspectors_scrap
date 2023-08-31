from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import csv
import requests
import certifi
import time
import re
import json

options = Options()
options.add_argument('--incognito')
driver = webdriver.Chrome(options=options)
all_data = []

# Указывает на раздел "где мой квартальный" на сайте Екатеринбург.рф
eka_link = 'https://xn--80acgfbsl1azdqr.xn--p1ai/справка/квартальные#tab3'

feature_collection = {
    "type": "FeatureCollection",
    "name": "objects-okn-zones",
    "features": []
}


def update_quarter_inspectors_data(quarters_link):
    driver.get(quarters_link)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'qly-districts-select')))
    district_select = driver.find_element(By.CSS_SELECTOR, '.qly-districts-select select')
    district_select_object = Select(district_select)

    district_names = [option.text for option in district_select_object.options[0:]]

    for i, district_name in enumerate(district_names):
        try:
            district_select_object.select_by_visible_text(district_name)
            time.sleep(3)
            page_content = driver.find_element(By.CLASS_NAME, 'qly-search-table')
            inspector_elements = page_content.find_elements(By.CLASS_NAME, 'qly-search-cell.js-district-qly a')

            for inspector_element in inspector_elements:
                inspector_href = inspector_element.get_attribute('href')
                pattern = r"userId=([a-f0-9-]+)"
                match = re.search(pattern, inspector_href)
                if match:
                    user_id = match.group(1)
                    inspector_data = get_inspector_data(user_id)

                    properties = {
                        "url": inspector_href,
                        "districtTitle": inspector_data['districtTitle'],
                        "quarterTitle": inspector_data['quarterTitle'],
                        "quarterDescription": inspector_data['quarterDescription'],
                    }

                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": process_coordinates(inspector_data['quarterCoordinates'])
                        },
                        "properties": properties,

                    }

                    feature_collection['features'].append(feature)

            print(f"Processed district: {district_name}")

        except Exception as err:
            print(f"Error processing district '{district_name}': {str(err)}")
            continue

    save_data_to_json(feature_collection)


def process_coordinates(coordinates):
    coordinates = coordinates.replace('POLYGON((', '').replace('))', '').split(',')

    polygon = []
    exterior_ring = []

    for x in coordinates:
        lon, lat = [float(coord) for coord in x.split(' ')]
        exterior_ring.append([lat, lon])  # Меняем местами широту и долготу

    polygon.append(exterior_ring)
    return polygon



def get_inspector_data(user_id):
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
        'user_id': f'{user_id}',
        'page': '1'
    }

    response = requests.post(url, headers=headers, data=data, verify=False)
    json_response = response.text
    data_dict = json.loads(json_response)
    qly_data = data_dict['data']['qly']
    return qly_data


def save_data_to_json(data):
    print('started saving')
    output_file_path = "output_quarters2222.json"
    with open(output_file_path, "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

    print(f"Данные сохранены в {output_file_path}")


if __name__ == "__main__":
    try:
        update_quarter_inspectors_data(eka_link)
    except Exception as e:
        print(e)
    finally:
        driver.quit()
