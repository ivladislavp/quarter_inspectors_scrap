from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def get_quarter_inspectors():
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
    #driver.quit()

    # Наполняем словарь районами
    for district in districts_elements:
        district_name = district.text
        district_link = district.get_attribute('value')
        districts_dict[district_name] = district_link
    return districts_dict




returned_items = get_quarter_inspectors()
for k, v in returned_items.items():
    print(k,v)
