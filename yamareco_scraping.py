
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import pickle
import time

# EdgeDriverのサービスを設定
service = EdgeService(executable_path=EdgeChromiumDriverManager().install())

# セキュリティ警告を無視するオプションを設定
options = Options()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

# Edgeを起動
driver = webdriver.Edge(service=service, options=options)

# クッキーを読み込み
driver.get("https://www.yamareco.com/")
with open("cookies.pkl", "rb") as file:
    cookies = pickle.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)

# ページを再読み込みしてセッションを復元
driver.refresh()
time.sleep(3)

def close_modals():
    try:
        while True:
            # 全画面広告の閉じるボタンをクリック
            fullscreen_ad_close_buttons = driver.find_elements(By.CSS_SELECTOR, "span.ns-4fxeg-e-16")
            for button in fullscreen_ad_close_buttons:
                if button.text == "閉じる":
                    try:
                        button.click()
                        time.sleep(2)  # モーダルが閉じるのを待機
                    except ElementClickInterceptedException:
                        pass

            # モーダルの「×」ボタンをクリック
            modal_close_buttons = driver.find_elements(By.CSS_SELECTOR, "button.close[data-dismiss='modal'] span")
            for button in modal_close_buttons:
                if button.text == "×":
                    try:
                        button.click()
                        time.sleep(2)  # モーダルが閉じるのを待機
                    except ElementClickInterceptedException:
                        pass
            
            # SVG閉じるアイコンをクリック
            svg_close_icons = driver.find_elements(By.CSS_SELECTOR, "svg[viewBox='0 0 48 48']")
            for icon in svg_close_icons:
                try:
                    icon.click()
                    time.sleep(2)  # モーダルが閉じるのを待機
                except ElementClickInterceptedException:
                    pass

            # 全画面広告やモーダルが存在しなくなった場合ループを終了
            if not fullscreen_ad_close_buttons and not modal_close_buttons and not svg_close_icons:
                break

    except WebDriverException:
        pass

def wait_until_no_modals():
    while True:
        try:
            WebDriverWait(driver, 5).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal.fade.in"))
            )
            break
        except TimeoutException:
            close_modals()

try:
    # 1. https://www.yamareco.com/ にアクセス
    driver.get("https://www.yamareco.com/")
    time.sleep(3)  # ページが完全にロードされるまで待機

    # 2. 新着の山行記録のリンクを見つけてクリック
    new_records_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "新着の山行記録"))
    )
    new_records_link.click()
    time.sleep(3)  # ページが完全にロードされるまで待機

    # モーダルが表示されている場合、閉じる
    wait_until_no_modals()

    # 3. 最初の山行記録のリンクを見つけてクリック
    first_record_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='https://www.yamareco.com/modules/yamareco/detail-']"))
    )
    first_record_link.click()
    time.sleep(3)  # ページが完全にロードされるまで待機

    # 再度モーダルが表示されている場合、閉じる
    wait_until_no_modals()

    # 4. 「拍手をおくる」ボタンをクリック
    clap_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-general.btn-general-sm.btn-general-black"))
    )
    clap_button.click()
    time.sleep(3)  # ボタンがクリックされた後の待機時間

except Exception as e:
    print("An error occurred:", e)
    # エラー時にページソースを保存してデバッグに役立てる
    with open("error_page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
