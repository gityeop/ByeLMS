import os
import pickle
import tkinter as tk
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
import sys
import random
from cryptography.fernet import Fernet


def get_chrome_driver():
    if getattr(sys, 'frozen', False):
        chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        chromedriver_path = os.path.join(current_dir, "chromedriver")

    driver = webdriver.Chrome(executable_path=chromedriver_path)
    return driver


username = ""
password = ""


def main():
    driver = get_chrome_driver()
    # 로그인 페이지 URL로 변경하세요
    login_url = "https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl"
    # 강의 페이지 URL로 변경하세요

    time.sleep(3)  # 로그인 후 페이지가 로드되기를 기다립니다.

    login(driver, login_url, username, password)

    time.sleep(3)  # 로그인 후 페이지가 로드되기를 기다립니다.
    icon_selector(driver)
    extract_number_of_lectures = extract_number()
    for i in range(extract_number_of_lectures):
        online_lecture_selector(driver)

        # 강의 정보 긁어오기
        lecture_duration = get_lecture_duration(driver)
        # print(lecture_duration)
        current_lecture_duration = get_current_lecture_duration(driver)
        # print(current_lecture_duration)
        pure_time_list = extract_pure_time(lecture_duration)
        # 강의 찾아서 들어가는 함수 만들기

        is_lecture_completed(driver, lecture_duration,
                             current_lecture_duration, pure_time_list)
        time.sleep(2)
        icon_selector(driver)

    # print(pure_time_list)
    print("모든 강의가 끝났습니다.")
    driver.quit()


def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Load the key from the file


def load_key():
    try:
        with open("key.key", "rb") as key_file:
            key = key_file.read()
        return key
    except FileNotFoundError:
        generate_key()
        return load_key()

# Encrypt the data


def encrypt_data(data):
    key = load_key()
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data

# Decrypt the data


def decrypt_data(encrypted_data):
    key = load_key()
    f = Fernet(key)
    decrypted_data = f.decrypt(encrypted_data).decode()
    return decrypted_data


def submit():
    global username, password
    username = entry_username.get()
    password = entry_password.get()

    encrypted_username = encrypt_data(username)
    encrypted_password = encrypt_data(password)

    with open("credentials_encrypted.pickle", "wb") as file:
        pickle.dump((encrypted_username, encrypted_password), file)

    window.destroy()


def load_credentials():
    if os.path.exists("credentials_encrypted.pickle"):
        with open("credentials_encrypted.pickle", "rb") as file:
            encrypted_username, encrypted_password = pickle.load(file)
        username = decrypt_data(encrypted_username)
        password = decrypt_data(encrypted_password)
        return username, password
    return "", ""


window = tk.Tk()
window.title("Login")

label_username = tk.Label(text="Username:")
entry_username = tk.Entry()
label_password = tk.Label(text="Password:")
entry_password = tk.Entry(show="*")

submit_button = tk.Button(text="Submit", command=submit)

label_username.pack()
entry_username.pack()
label_password.pack()
entry_password.pack()
submit_button.pack()

# Load saved credentials if they exist
saved_username, saved_password = load_credentials()
entry_username.insert(0, saved_username)
entry_password.insert(0, saved_password)

entry_username.focus_set()
window.mainloop()


def login(driver, login_url, username, password):
    driver.get(login_url)
    wait = WebDriverWait(driver, 10)  # 최대 10초 동안 대기합니다.
    login_button_locator = (By.ID, "login_btn")  # 로그인 버튼 요소의 실제 ID로 변경하세요

    wait.until(EC.presence_of_element_located(login_button_locator))

    username_input = driver.find_element(
        by=By.NAME, value="usr_id")  # 실제 사용자 이름 입력창의 요소 이름으로 변경하세요
    password_input = driver.find_element(
        by=By.NAME, value="usr_pwd")  # 실제 비밀번호 입력창의 요소 이름으로 변경하세요
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)  # 로그인 폼을 제출합니다.


def icon_selector(driver):
    wait = WebDriverWait(driver, 5)  # 최대 5초 동안 대기합니다.
    todo_icon = "#header > div.utillmenu > div > fieldset > div > div:nth-child(2)"

    icon_elements = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, todo_icon)))
    print(icon_elements)

    if icon_elements:
        icon_element = icon_elements[0]
        icon_element.click()
    else:
        print("원하는 요소가 없습니다. 계속 진행합니다.")


def online_lecture_selector(driver):
    wait = WebDriverWait(driver, 5)  # 최대 10초 동안 대기합니다.
    # 실제 아이콘 요소의 CSS 선택자로 변경하세요
    online_lecture = "#todo_pop > div > div.todo_search_wrap > div.todo_category_wrap > div:nth-child(1)"
    time.sleep(2)
    online_lecture_icon = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, online_lecture)))
    online_lecture_icon.click()
    online_lecture_item = "#todo_list > div.todo_wrap.on"  # 실제 아이콘 요소의 CSS 선택자로 변경하세요
    online_lectures_item_ver2 = "#todo_list > div:nth-child(2)"
    # wait.until(EC.presence_of_element_located(By.CSS_SELECTOR, online_lecture_item))
    # online_lecture_icon.click()
    time.sleep(2)
    online_lecture_item_wait = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, online_lecture_item)))
    online_lectures_item_ver2_wait = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, online_lectures_item_ver2)))
    if online_lecture_item_wait is None:
        if online_lectures_item_ver2 is None:
            driver.quit()
        else:
            online_lectures_item_ver2_wait.click()
    else:
        online_lecture_item_wait.click()


def extract_number():
    html = '<div class="cate_cnt" id="lecture_weeks_cnt">2</div>'
    soup = BeautifulSoup(html, 'html.parser')

    lecture_weeks_cnt = soup.select_one('#lecture_weeks_cnt')
    number = int(lecture_weeks_cnt.text)
    print(number)
    return number


def count_lectures(driver):
    wait = WebDriverWait(driver, 10)  # 최대 10초 동안 대기합니다.
    lecture_list_selector = ".site-mouseover-color"  # 강의 목록을 나타내는 CSS 선택자로 변경하세요
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, lecture_list_selector)))
    lecture_list = driver.find_elements(By.CSS_SELECTOR, lecture_list_selector)
    lecture_count = len(lecture_list)

    if lecture_count == 0:
        print("강의가 없습니다. 프로그램을 종료합니다.")
        driver.quit()
        sys.exit()

    return lecture_count


def get_lecture_duration(driver):
    wait = WebDriverWait(driver, 10)  # 최대 10초 동안 대기합니다.

    duration_selector = "div[style='float: left;margin-left: 7px;margin-top:3px;']"
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, duration_selector)))
    duration_elements = driver.find_elements(
        By.CSS_SELECTOR, duration_selector)
    last_durations = []
    for element in duration_elements:
        full_text = element.text
        last_duration = full_text.split(" / ")[-1]
        last_durations.append(last_duration)

    return last_durations


def get_current_lecture_duration(driver):
    wait = WebDriverWait(driver, 10)

    css_selector = 'div[style="float: left;margin-left: 7px;margin-top:3px;"]'
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, css_selector)))
    duration_element = driver.find_elements(By.CSS_SELECTOR, css_selector)
    current_durations = []
    for element in duration_element:
        full_text = element.text
        current_duration = full_text.split(" / ")[0]

        current_durations.append(current_duration)

    return current_durations
    # 텍스트를 " / "로 나누고 첫 번째 부분을 가져옵니다.


def is_lecture_completed(driver, last_durations, current_durations, pure_time_list):

    wait = WebDriverWait(driver, 10)
    pure_current_time = extract_pure_time(current_durations)
    for i in range(len(last_durations)):
        random_time = random.randint(120, 240)
        if pure_time_list[i] < pure_current_time[i]:
            pass
        else:
            left_time_list = pure_time_list[i] - \
                pure_current_time[i] + random_time
            # print(f"랜덤 시간 : {random_time}")
            print(f"재생 시간 : {left_time_list}")
            join_lecture(driver, left_time_list, i)
    driver.back()


def extract_pure_time(duration_str):
    lecture_time = []
    for element in duration_str:
        pure_time = convert_duration_to_seconds(element)
        lecture_time. append(pure_time)

    return lecture_time


def convert_duration_to_seconds(duration_str):
    time_parts = duration_str.split(":")
    if len(time_parts) == 3:
        hours, minutes, seconds = int(time_parts[0]), int(
            time_parts[1]), int(time_parts[2])
    elif len(time_parts) == 2:
        hours = 0
        minutes, seconds = int(time_parts[0]), int(time_parts[1])
    else:
        raise ValueError("Invalid time format")

    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


def join_lecture(driver, time_list_of_lectures, i):
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    lecture_site = '.site-mouseover-color'
    print(f"강의  시간: {time_list_of_lectures}초")
    wait_lecture_icon = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, lecture_site)))
    if i < len(wait_lecture_icon):
        wait_lecture_icon[i].click()
        time.sleep(5)
        actions.send_keys(Keys.SPACE).perform()
        for _ in range(5):
            actions.send_keys(Keys.ARROW_DOWN)
        actions.perform()
        time.sleep(time_list_of_lectures)

    else:
        print(f"Error: Unable to find lecture icon for index {i}")
    driver.back()
    time.sleep(2)  # 페이지 로딩을 기다리기 위해 추가
    # 강의 목록을 다시 가져옵니다.
    lecture_list_selector = ".site-mouseover-color"  # 강의 목록을 나타내는 CSS 선택자로 변경하세요
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, lecture_list_selector)))


if __name__ == "__main__":
    main()
