from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def get_districts_dict():
    districts_dict = {}

    # Конфигурация и инициализция селениума
    options = Options()
    options.add_argument('--incognito')
    driver = webdriver.Chrome(options=options)
    link = 'https://xn--80acgfbsl1azdqr.xn--p1ai/справка/квартальные#tab3'

    # Сбор списка названий и ссылок на районы
    driver.get(link)
    wait = WebDriverWait(driver, 30)
    selector = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'qly-districts-select')))
    districts_elements = selector.find_elements(By.TAG_NAME, 'option')

    # Наполняем словарь районами
    for district in districts_elements:
        district_name = district.text
        district_link = district.get_attribute('value')
        # districts_dict[district_name] = district_link

    # Поочередно обходим каждый район и собираем отдельный словарь инспекторов
    for district_name, district_link in districts_dict.items():
        district_select = driver.find_element(By.CSS_SELECTOR, '.qly-districts-select select')
        district_select.send_keys(district_link)
        page_content = driver.page_source
        inspector_elements = page_content.find_elements(By.CSS_SELECTOR, '.qly-search-cell.js-district-qly a')

def get_inspector_list():
    # Конфигурация и инициализция селениума
    options = Options()
    options.add_argument('--incognito')
    driver = webdriver.Chrome(options=options)
    link = 'https://xn--80acgfbsl1azdqr.xn--p1ai/справка/квартальные#tab3'

    # Сбор списка названий и ссылок на районы
    driver.get(link)
    wait = WebDriverWait(driver, 30)
    selector = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'qly-districts-select')))
    districts_elements = selector.find_elements(By.TAG_NAME, 'option')

    for district in districts_elements:
        district_name = district.text
        district_link = district.get_attribute('value')
        district_select = driver.find_element(By.CSS_SELECTOR, '.qly-districts-select select')
        district_select.send_keys(district_link)
        page_content = driver.find_element(By.CLASS_NAME, 'qly-search-table')
        inspector_elements = page_content.find_elements(By.CLASS_NAME, 'qly-search-cell.js-district-qly a')
        for inspector_element in inspector_elements:
            inspector_name = inspector_element.text
            inspector_href = inspector_element.get_attribute('href')
            print(inspector_name, inspector_href)




    # def get_inspectors_by_district():
    #     pass
    #
    # def get_inspector_card_info():
    #     get_inspectors_by_district()
    #     pass
    #
    # def update_all_quarter_inspectors():
    #     for inspector in inspectors_dict:
    #         inspectors_list += get_inspector_card_info()

#get_districts_dict()

get_inspector_list()