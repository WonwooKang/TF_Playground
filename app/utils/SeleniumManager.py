# -*- coding: utf-8 -*-

import os
import platform
# 아래 코드들을 import 해 줍시다.
# WebDriverWait는 Selenium 2.4.0 이후 부터 사용 가능합니다.
# expected_conditions는 Selenium 2.26.0 이후 부터 사용 가능합니다.
import traceback
import zipfile
from typing import AnyStr

from selenium import webdriver
from selenium.webdriver.remote.command import Command

from app.utils import S3

# 드라이버 다운로드 경로 - 람다 기본사용 경로
tmpPath = '/tmp/'
if platform.system() == 'Windows':
    tmpPath = 'c:/tmp/'


def driver_clear(func):
    """
    드라이버 종료 데코레이터

    :return:
    """

    def decorator(*args, **kwargs):
        self = args[0]
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
        finally:
            if self.driver:
                print('Driver Close')
                self.driver.close()
                print('Driver Quit')
                self.driver.quit()

    return decorator


class Driver:
    """
    브라우저 드라이버 정보
    """
    name: AnyStr
    zip_name: AnyStr
    path: AnyStr
    zip_path: AnyStr

    def __init__(self, name, zip_name):
        self.name = name
        self.path = tmpPath + name
        self.zip_name = zip_name
        self.zip_path = tmpPath + zip_name


class Binary:
    """
    아마존 리눅스에서 사용할 바이너리 정보 객체
    """
    name: AnyStr
    zip_name: AnyStr
    path: AnyStr
    zip_path: AnyStr

    def __init__(self, name, zip_name):
        self.name = name
        self.path = tmpPath + name
        self.zip_name = zip_name
        self.zip_path = tmpPath + zip_name


class SeleniumManager:
    """
    셀레니움 관리객체
    """

    browser: AnyStr
    bucketKey: AnyStr
    driver: Driver
    binary: Binary
    is_linux = False
    _driver: webdriver  # 실질적인 드라이버
    _is_headless: bool

    def __init__(self, **kwargs):
        """
        초기화 - 환경에따라 다른 드라이버명 세팅 및 바이너리명 세팅
        """

        print('셀레니움 매니져 생성')

        """ 기초데이터 세팅 - 일단은 크롬만 """
        # 브라우저, 버킷경로 세팅
        self.browser = 'chrome'
        self.bucketKey = 'headless_chrome/headless_chrome_69_driver_2.43'

        # 드라이버 세팅 - 맥과 윈도우는 자체 크롬 이용하도록 - 바이너리 사용안함
        name, zip_name = None, None
        if platform.system() == 'Linux':
            name = 'chromedriver'
            zip_name = 'chromedriver_2.43_linux64_69-71.zip'
            self.is_linux = True

        elif platform.system() == 'Darwin':
            name = 'chromedriver'
            zip_name = 'chromedriver_mac64_80.zip'

        elif platform.system() == 'Windows':
            name = 'chromedriver.exe'
            zip_name = 'chromedriver_2.43_win32_69-71.zip'

        self.driver = Driver(name, zip_name)

        # 바이너리 세팅 - 아마존 리눅스(람다) 전용
        binary_name = 'headless-chromium'
        binary_zip_name = 'stable-headless-chromium-amazonlinux-2017-03.zip'

        self.binary = Binary(binary_name, binary_zip_name)
        """ 기초데이터 세팅 END - 일단은 크롬만 """

        self._is_headless = kwargs.get('headless')
        self.__create_selenium_driver()

    def _driver_check(self):
        """
        드라이버와 바이너리를 체크하고, 없으면 다운받는다.
        바이너리는 아마존 리눅스에서만 체크한다.

        :return: boolean
        """

        """ 드라이버 및 바이너리 체크 """
        print('크롬 드라이버 유무 체크 : ' + str(os.path.isfile(self.driver.path)), self.driver.path)
        if not os.path.isfile(self.driver.path):
            print('크롬 드라이버 다운로드 시작')
            print('경로 : ' + self.driver.zip_path)
            driver_zip_file_data = S3.getS3File(self.bucketKey + '/' + self.driver.zip_name)

            f = open(self.driver.zip_path, 'wb')
            f.write(driver_zip_file_data)
            f.close()

            driver_zip_file = zipfile.ZipFile(self.driver.zip_path)
            driver_zip_file.extractall(tmpPath)
            driver_zip_file.close()

            os.chmod(self.driver.path, 0o777)
            print('크롬 드라이버 다운로드 완료')

        # 아마존리눅스(람다) 환경일경우 크롬 headless-binary 필요함
        if platform.system() == 'Linux':
            print('headless 크롬 바이너리 유무 체크 : ' + str(os.path.isfile(self.binary.path)), self.binary.path)

            if not os.path.isfile(self.binary.path):
                print('headless 크롬 다운로드 시작')
                print('경로 : ' + self.binary.zip_path)
                binary_file_data = S3.getS3File(self.bucketKey + '/' + self.binary.zip_name)
                f = open(self.binary.zip_path, 'wb')
                f.write(binary_file_data)
                f.close()

                binary_zip_file = zipfile.ZipFile(self.binary.zip_path)
                binary_zip_file.extractall(tmpPath)
                binary_zip_file.close()

                os.chmod(self.binary.path, 0o777)
                print('headless 크롬 바이너리 다운로드 완료')

        print('드라이버 체크 완료')
        """ 드라이버 및 바이너리 체크 END """

    def get_options(self):
        """
        브라우저별 옵션정보 리턴 - 일단 크롬만

        :param headless:
        :return:
        """

        options = None
        if self.browser == 'chrome':
            options = webdriver.ChromeOptions()

            options.add_argument('homedir='+tmpPath)
            options.add_argument('data-path='+tmpPath+'data-path')
            options.add_argument('disk-cache-dir='+tmpPath+'cache-dir')

            # 헤드리스모드일 경우
            if self._is_headless:
                options.add_argument('window-size=1920x1080')
                options.add_argument('headless')  # 드라이버 버전 60부터 사용가능
                options.add_argument('disable-gpu')
                options.add_argument('no-sandbox')
                options.add_argument('remote-debugging-port=9222')
                options.add_argument('disable-dev-shm-usage')  # DevToolsActivePort file doesn't exist 에러 떄문에 추가
                options.add_argument('single-process')

            # 속도 향상용 옵션 추가
            '''
            options.add_argument("disable-infobars")
            options.add_argument("--disable-extensions")
            prefs = {'profile.default_content_setting_values':
                {
                    'cookies': 2, 'images': 2, 'plugins': 2, 'popups': 2,
                    'geolocation': 2, 'notifications': 2,
                    'auto_select_certificate': 2, 'fullscreen': 2,
                    'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                    'media_stream_mic': 2, 'media_stream_camera': 2,
                    'protocol_handlers': 2, 'ppapi_broker': 2,
                    'automatic_downloads': 2, 'midi_sysex': 2,
                    'push_messaging': 2, 'ssl_cert_decisions': 2,
                    'metro_switch_to_desktop': 2,
                    'protected_media_identifier': 2, 'app_banner': 2,
                    'site_engagement': 2, 'durable_storage': 2
                }
            }
            options.add_experimental_option('prefs', prefs)
            '''
            # 속도 향상용 옵션 추가 END

            # 아마존리눅스(람다) 환경일 경우
            if self.is_linux:
                options.binary_location = self.binary.path

        return options

    def __create_selenium_driver(self):
        """
        드라이버 생성자
        :param kwargs:
        :return:
        """
        """ 드라이버 생성구간 """
        # 드라이버 체크 및 생성
        self._driver_check()

        print('헤드리스 모드: ', self._is_headless)

        print('드라이버 옵션생성')
        options = self.get_options()

        if self.browser == 'chrome':
            print('드라이버 생성')
            driver = webdriver.Chrome(self.driver.path, chrome_options=options)
            print('드라이버 생성완료')

            print('모든 쿠키 삭제')
            driver.delete_all_cookies()

            self._driver = driver
        """ 드라이버 생성구간 END """

    def get_selenium_driver(self):
        """
        셀레니움 드라이버 생성 및 리턴

        :param headless:
        :return:
        """

        try:
            self._driver.execute(Command.STATUS)
            return self._driver
        except Exception as e:
            self.__create_selenium_driver()
            return self._driver

    def driver_clear(self):
        """
        드라이버 버전이 갱신이 안될때 드라이버 삭제용 함수

        :return:
        """

        print('driver clear start!')

        if os.path.exists(self.driver.path):
            os.remove(self.driver.path)
            print('driver removed.')

        if os.path.exists(self.driver.zip_path):
            os.remove(self.driver.zip_path)
            print('driver zip removed.')

        if os.path.exists(self.binary.path):
            os.remove(self.binary.path)
            print('binary removed.')

        if os.path.exists(self.binary.zip_path):
            os.remove(self.binary.zip_path)
            print('binary zip removed.')

        print('driver clear end!')

    def get_test_driver(self):

        chrome_path = '/tmp/chrome_83'
        chrome_driver_path = '/tmp/chromedriver_83'

        # 드라이버 다운로드
        print('드라이버 다운로드')
        driver_file_data = S3.getS3File('headless_chrome/amazonlinux_test/chromedriver_83')
        f = open(chrome_driver_path, 'wb')
        f.write(driver_file_data)
        f.close()

        print('드라이버 권한변경')
        os.chmod(chrome_driver_path, 0o777)

        print('바이너리 다운로드')
        binary_file_data = S3.getS3File('headless_chrome/amazonlinux_test/amazonlinux_chrome_83')
        f = open(chrome_path, 'wb')
        f.write(binary_file_data)
        f.close()

        print('바이너리 권한변경')
        os.chmod(chrome_path, 0o777)

        print('헤드리스 옵션 생성')
        options = self.get_options()

        # 최신 크롬 설정이라고 해서 추가해봄
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        print('테스트용 바이너리 경로 세팅')
        options.binary_location = chrome_path

        print('드라이버 생성')
        driver = webdriver.Chrome(chrome_driver_path, chrome_options=options)

        return driver

    def quit(self):
        self._driver.quit()
