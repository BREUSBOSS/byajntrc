from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from fake_useragent import UserAgent

from .base_driver import BaseDriverHelper

DRIVER_NAME = 'ChromeWebDriver'

class WebDriverHelper(BaseDriverHelper):

    def __init__(self):
        super().__init__(name=DRIVER_NAME)

        # Генерация случайного User-Agent
        ua = UserAgent()
        user_agent = ua.random

        # Настройки Chrome
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--disable-gpu")
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument("start-maximized")
        self.options.add_argument("disable-infobars")
        self.options.add_argument(f"user-agent={user_agent}")
        self.options.add_argument("--disable-blink-features=AutomationControlled")  # Отключает navigator.webdriver

        # Установка ChromeDriver автоматически
        driver_path = ChromeDriverManager().install()
        self._driver = webdriver.Chrome(service=ChromeService(driver_path), options=self.options)

        # Маскируем WebDriver
        self._mask_webdriver()

    @property
    def driver(self):
        return self._driver
    
    def cleanup(self):
        """ Закрывает браузер и освобождает ресурсы. """
        self._driver.quit()

    """ PRIVATE """

    def _mask_webdriver(self):
        """ Маскирует WebDriver от детектирования. """
        self._driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'])
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3]
                });
            """
        })

    def check_valid_driver_connection(self):
        """ Проверяет, корректно ли загружен ChromeDriver. """
        try:
            with webdriver.Chrome(service=ChromeService(ChromeDriverManager().install())) as test_driver:
                return True
        except Exception as e:
            print(f'Could not load ChromeDriver: {e}')
            return False
