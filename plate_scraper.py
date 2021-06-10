from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("http://192.168.1.64/doc/page/config.asp")
assert "Login".lower() in driver.title.lower()

username_elem = driver.find_element_by_css_selector("div.login-user input.login-input")
username_elem.clear()
username_elem.send_keys("admin")

password_elem = driver.find_element_by_css_selector("div.login-item input#password")
password_elem.clear()
password_elem.send_keys("Hikevision")

login_button = driver.find_element_by_css_selector("div.login-item button.login-btn")
login_button.click()

realtime_link = driver.find_element_by_link_text('Road Traffic')
realtime_link.click()
print(realtime_link)


#driver.close()