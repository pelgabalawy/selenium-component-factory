from selenium.common import StaleElementReferenceException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from typing import Dict


class CompFactoryException(Exception):
    """Base class for exceptions in this module."""
    pass


class ComponentSelectorNotSpecified(CompFactoryException):
    """Raised when the component selector is not provided"""


class ElementNotFoundException(CompFactoryException):
    """Raised when the element is not found in the page. (Using ` EC.presence_of_element_located` function from
    within __getattr__ method)."""


class ElementNotVisibleException(CompFactoryException):
    """Raised when the element is not visible in the page. (Using `EC.visibility_of_element_located` function from
    within __getattr__ method)."""


class ComponentFactory(object):
    timeout: int = 10                   # the global timeout specified to wait for elements to show up
    highlight: bool = False             # hightlight elements when they are found
    highlight_color: str = '#33ffff'    # the color used to highlight elements

    mobile_test: bool = False           # Mobile support

    locators: Dict[str, str] = {}       # elements within the component

    # mapping of the available selectors in selenium for web elements
    TYPE_OF_LOCATORS = {
        'css': By.CSS_SELECTOR,
        'id': By.ID,
        'name': By.NAME,
        'xpath': By.XPATH,
        'link_text': By.LINK_TEXT,
        'partial_link_text': By.PARTIAL_LINK_TEXT,
        'tag': By.TAG_NAME,
        'class_name': By.CLASS_NAME
    }

    def __init__(self):
        pass

    def __get__(self, instance, owner):
        if not instance:
            return None
        else:
            self.driver = instance.driver

    def __getattr__(self, loc):
        # if it's mobile component we use this code
        if self.mobile_test:
            if loc in self.locators.keys():
                element = self.find_element_by_accessibility_id(self.locators[loc][1])
                return element
        else:
            # find all the elements within the component
            if loc in self.locators.keys():
                locator = (self.TYPE_OF_LOCATORS[self.locators[loc][0].lower()], self.locators[loc][1])
                try:
                    element = WebDriverWait(self.driver, self.timeout).until(
                        EC.presence_of_element_located(locator)
                    )
                except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
                    raise ElementNotFoundException(
                        "An exception of type " + type(e).__name__ +
                        " occurred. With Element -: " + loc +
                        " - locator: (" + locator[0] + ", " + locator[1] + ")"
                    )

                try:
                    element = WebDriverWait(self.driver, self.timeout).until(
                        EC.visibility_of_element_located(locator)
                    )
                except (StaleElementReferenceException, NoSuchElementException, TimeoutException) as e:
                    raise ElementNotVisibleException(
                        "An exception of type " + type(e).__name__ +
                        " occurred. With Element -: " + loc +
                        " - locator: (" + locator[0] + ", " + locator[1] + ")"
                    )

                element = self.get_web_element(*locator)
                element._locator = locator
                return element
        return super().__getattr__(loc)

    def get_web_element(self, *loc):
        element = self.driver.find_element(*loc)
        self.highlight_web_element(element)
        return element

    def highlight_web_element(self, element):
        """
        To highlight webElement
        :param: WebElement
        :return: None
        """
        if self.highlight:
            self.driver.execute_script(f"arguments[0].style.border='2px ridge {self.hightlight_color}'", element)
