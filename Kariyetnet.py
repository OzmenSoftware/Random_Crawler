import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


"""database_name = "JobList"
user_name = "postgres"
password = "123"
port = "5433"

# Bağlantı denemesi
connection = psycopg2.connect(
    dbname=database_name,
    user=user_name,
    password=password,
    port=port
)
print("Bağlandı")"""


chrome_driver_path = 'C:/Users/Çağdaş Halil Bacanak/OneDrive/Masaüstü/chromedriver.exe'

options = Options()
options.add_experimental_option("detach", True)                         
options.add_experimental_option("useAutomationExtension", False)      
options.add_argument("--start-maximized") 

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.get('https://www.kariyer.net/')

wait = WebDriverWait(driver, 20)


def get_shadow_root(element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

shadow_host = driver.find_element(By.TAG_NAME, 'efilli-layout-starbucks')
bekleme = wait.until(
    EC.presence_of_all_elements_located((By.TAG_NAME, 'efilli-layout-starbucks'))
)
button = get_shadow_root(shadow_host).find_element(by = By.CSS_SELECTOR, value = 'div.banner > div.banner__accept-button')
button.click()


try:
    #cursor = connection.cursor()

    # İş İlanları Bölümüne git
    is_sayfasi = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="İş Ara"]')))
    is_sayfasi.click()

    sayfa_numaralandirma = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pagination.py-3.b-pagination.justify-content-center')))
    sayfa_numaralari = sayfa_numaralandirma.find_elements(By.CLASS_NAME, 'page-link')
    sayfa_numara_metni = [sayfa_numara.text for sayfa_numara in sayfa_numaralari]

    # Her bir sayfa için iş ilanlarını
    for sayfa in range(int(sayfa_numara_metni[-2])):
        driver.get('https://www.kariyer.net/is-ilanlari?cp='+str(sayfa+1))

        list_items_wrapper = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'list-items-wrapper')))
        is_kardlari = list_items_wrapper.find_elements(By.CLASS_NAME, 'k-ad-card-title.multiline')

        for kart in is_kardlari:
            kart.click()
            time.sleep(2)

            new_window = [window for window in driver.window_handles if window != driver.current_window_handle][0]
            driver.switch_to.window(new_window)

            pozisyon_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span[aria-label]')))
            pozisyon = pozisyon_element.get_attribute('aria-label').strip()

            firma_ismi = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'company-name.company-name-hover')))
            firma = firma_ismi.text.strip()

            is_detayi_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'job-sub-detail')))
            is_detayi = is_detayi_div.text.strip()

            aday_kriterleri_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'aligment-container')))
            aday_kriterleri = aday_kriterleri_div.text.strip()

            new_window_url = driver.current_url

            # PostgreSQL'e veri eklenen yer
            insert_query = """
            INSERT INTO "JobDescriptions" ("Position", "FirmName", "JobDetail", "CandidateCriter", "Url")
            VALUES (%s, %s, %s, %s, %s);
            """

            #cursor.execute(insert_query, (pozisyon, firma, is_detayi, aday_kriterleri, new_window_url))
            #connection.commit()

            print(f"{pozisyon} pozisyonu için veri PostgreSQL'e eklendi.")

            time.sleep(2)

            driver.close()
            driver.switch_to.window(driver.window_handles[0])


        time.sleep(2)

    sonraki_sayfa = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="__layout"]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[2]/div[2]/div[52]/div/ul/li[14]/button/span')))
    sonraki_sayfa.click()

except Exception as e:
    print(f"Hata oluştu: {e}")
