import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from seleniumcompfactory.ComponentFactory import ComponentFactory


@pytest.fixture
def az():
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.get("https://s1.demo.opensourcecms.com/wordpress/wp-login.php")
    try:
        yield driver
    finally:
        driver.close()


class LoginComp(ComponentFactory):
    def __init__(self, driver):
        self.driver = driver

    locators = {
        "edtUserName": ('ID', 'user_login'),
        "edtPassword": ('NAME', 'pwd'),
        "btnSignIn": ('XPATH', '//input[@value="Log In"]'),
        "unknownElement": ("CSS", ".notThere")
    }

    def login(self):
        # set_text(), click_button() methods are extended methods in PageFactory
        self.edtUserName.send_keys("opensourcecms")  # edtUserName become class variable using PageFactory
        self.edtPassword.send_keys("opensourcecms")
        self.btnSignIn.click()


def test_login(az):
    pglogin = LoginComp(az)
    pglogin.login()


def test_not_found_element(az):
    with pytest.raises(Exception) as ex:
        pglogin = LoginComp(az)
        pglogin.timeout = 2
        pglogin.unknownElement
    assert 'unknownElement - locator: (css selector, .notThere)' in str(ex.value)
