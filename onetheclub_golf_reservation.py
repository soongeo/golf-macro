from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from datetime import datetime
import time
import pytesseract
from PIL import Image
import io
import base64
import re
import os
import requests

class OneTheClubGolfReservation:
    def __init__(self):
        self.driver = None
        self.base_url = "https://www.onetheclub.com/reservation/golf"
        self.target_club = "클럽72CC 바다 레이크"  # 기본값 설정
        self.time_range = {
            'start': (13, 30),  # (시, 분)
            'end': (14, 30)     # (시, 분)
        }
        self.target_date = "2025-03-07"  # 기본값 설정
        # Tesseract 경로 설정 (프로젝트 디렉토리 내 tesseract 폴더)
        tesseract_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tesseract', 'tesseract.exe')
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
    def setup_driver(self):
        """웹드라이버 설정"""
        options = uc.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--incognito')  # 시크릿 모드 추가
        
        # User-Agent 설정
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36')
        
        # reCAPTCHA 우회를 위한 추가 설정
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--disable-gpu')
        
        # Chrome 버전 호환성을 위한 설정
        self.driver = uc.Chrome(
            options=options,
            version_main=132  # 현재 설치된 Chrome 버전 지정
        )
        
        # reCAPTCHA 우회를 위한 JavaScript 실행
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                window.chrome = {
                    runtime: {}
                }
            '''
        })
        
    def check_login_status(self):
        """로그인 상태 확인"""
        try:
            print("로그인 상태 확인 중...")
            # 헤더의 로그인/로그아웃 텍스트 확인
            header_text = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "headerTextLogin"))
            )
            
            if header_text.text == "LOGOUT":
                print("이미 로그인되어 있습니다.")
                return True
            else:
                print("로그인이 필요합니다.")
                return False
        except:
            print("로그인 상태 확인 실패, 로그인이 필요합니다.")
            return False

    def login(self, username, password):
        """로그인 수행"""
        try:
            print("웹사이트로 이동 중...")
            self.driver.get(self.base_url)
            
            # 페이지가 완전히 로드될 때까지 대기
            print("페이지 로드 대기 중...")
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 로그인 상태 확인
            if self.check_login_status():
                return True
            
            # 로그인이 필요한 경우
            print("로그인 프로세스 시작...")
            # 로그인 버튼이 나타날 때까지 대기 후 클릭
            print("로그인 버튼 찾는 중...")
            login_btn = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "headerUrlLogin"))
            )
            print("로그인 버튼 클릭...")
            self.driver.execute_script("arguments[0].click();", login_btn)
            
            # 로그인 폼이 로드될 때까지 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "usrId"))
            )
            
            # JavaScript를 사용하여 로그인 처리
            print("로그인 정보 입력 중...")
            login_script = f"""
                document.getElementById('usrId').value = '{username}';
                document.getElementById('usrPwd').value = '{password}';
                document.getElementById('fnLogin').click();
            """
            self.driver.execute_script(login_script)
            
            # 팝업 알림 버튼 대기 및 클릭
            print("팝업 알림 버튼 찾는 중...")
            try:
                popup_btn = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.ID, "popupAlert_btn"))
                )
                print("팝업 알림 버튼 클릭...")
                self.driver.execute_script("arguments[0].click();", popup_btn)
            except:
                print("팝업 알림 버튼이 없습니다.")
            
            # 로그인 성공 여부 확인
            try:
                print("로그인 성공 여부 확인 중...")
                header_text = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "headerTextLogin"))
                )
                if header_text.text == "LOGOUT":
                    print("로그인 성공")
                    return True
                else:
                    print("로그인 실패 - 헤더 텍스트가 LOGOUT이 아님")
                    return False
            except:
                print("로그인 실패 - 헤더 텍스트를 찾을 수 없음")
                return False
                
        except Exception as e:
            print(f"로그인 중 오류 발생: {str(e)}")
            return False
            
    def select_date(self, target_date):
        """날짜 선택"""
        try:
            # 날짜 형식을 변환 (YYYY-MM-DD -> AYYYYMMDD)
            date_id = "A" + target_date.replace("-", "")
            print(f"날짜 선택 중... (ID: {date_id})")
            
            # 날짜 선택 버튼이 클릭 가능할 때까지 대기
            date_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, date_id))
            )
            self.driver.execute_script("arguments[0].click();", date_element)
            
            # 날짜 선택 후 페이지 업데이트 대기
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            return True
        except Exception as e:
            print(f"날짜 선택 중 오류 발생: {str(e)}")
            return False
            
    def set_target_club(self, club_name):
        """골프장 이름 설정"""
        self.target_club = club_name
        
    def set_time_range(self, start_hour, start_minute, end_hour, end_minute):
        """시간 범위 설정"""
        self.time_range = {
            'start': (start_hour, start_minute),
            'end': (end_hour, end_minute)
        }
        
    def set_target_date(self, date):
        """날짜 설정 (YYYY-MM-DD 형식)"""
        self.target_date = date
        
    def process_captcha(self, img_path):
        """캡차 이미지 처리"""
        try:
            # OCR.space API 키 (무료 키 사용)
            api_key = os.getenv('OCRSPACE_API_KEY', 'K81428265788957')
            
            # API 엔드포인트
            url = 'https://api.ocr.space/parse/image'
            
            # API 요청 파라미터
            payload = {
                'apikey': api_key,
                'isOverlayRequired': 'false',
                'language': 'eng',
                'ocrengine': '2',  # 엔진 2 사용 (더 정확한 엔진)
                'scale': 'true',   # 이미지 스케일링 활성화
                'detectOrientation': 'true',
                'isTable': 'false',
                'filetype': 'PNG'
            }

            # 파일 데이터
            with open(img_path, 'rb') as image_file:
                files = {
                    'file': image_file
                }
                
                # API 요청
                ocr_response = requests.post(url, files=files, data=payload)
                result = ocr_response.json()
                
                if result.get('OCRExitCode') == 1:  # 성공
                    texts = result.get('ParsedResults', [])
                    results = []
                    
                    for text in texts:
                        # 텍스트에서 숫자만 추출
                        line = ''.join(filter(str.isdigit, text.get('ParsedText', '')))
                        # 4자리 숫자 패턴 찾기
                        if line and len(line) >= 4:
                            # 4자리씩 분할하여 결과에 추가
                            for i in range(0, len(line) - 3):
                                number = line[i:i+4]
                                if len(number) == 4:
                                    results.append(number)
                    
                    if results:
                        print(f"OCR.space API 결과: {results}")
                        return results[0]
                    else:
                        print("OCR.space API: 4자리 숫자를 찾을 수 없음")
                        return None
                else:
                    print(f"OCR.space API 에러: {result.get('ErrorMessage', '알 수 없는 에러')}")
                    return None
                    
        except Exception as e:
            print(f"캡차 처리 중 오류 발생: {str(e)}")
            return None

    def select_golf_club(self):
        """골프장 선택"""
        try:
            print("골프장 목록 확인 중...")
            # 모든 골프장 이름 요소 찾기
            company_names = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "company_name"))
            )
            
            # 지정된 골프장 찾기
            target_club = None
            company_id = None
            for name in company_names:
                if self.target_club in name.text:
                    target_club = name
                    # 부모 요소 찾기
                    parent_div = target_club.find_element(By.XPATH, "./parent::*")
                    # 예약 버튼 찾기
                    reserve_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ".//button[contains(@data-target, 'company_list_')]"))
                    )
                    # data-target 속성에서 company_id 추출
                    data_target = reserve_btn.get_attribute("data-target")
                    company_id = data_target.replace("company_list_", "").replace("#", "")
                    break
            
            if target_club and company_id:
                print(f"{self.target_club} 찾음 (company_id: {company_id})")
                
                print("예약 버튼 클릭...")
                reserve_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f".//button[contains(@data-target, 'company_list_{company_id}')]"))
                )
                self.driver.execute_script("arguments[0].click();", reserve_btn)
                
                # 시간대 목록이 로드될 때까지 대기
                time_div = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"div[data-name='company_list_{company_id}']"))
                )
                
                # 시간대 목록이 완전히 로드될 때까지 대기
                WebDriverWait(self.driver, 10).until(
                    lambda driver: len(time_div.find_elements(By.CSS_SELECTOR, "ul.list > li.grid")) > 0
                )
                
                print("시간대 목록 찾기...")
                # ul 안의 모든 li 요소 찾기
                time_slots = time_div.find_elements(By.CSS_SELECTOR, "ul.list > li.grid")
                target_time = None
                target_time_text = None
                
                # 시간 범위를 분으로 변환
                start_minutes = self.time_range['start'][0] * 60 + self.time_range['start'][1]
                end_minutes = self.time_range['end'][0] * 60 + self.time_range['end'][1]
                
                for slot in time_slots:
                    # li 안의 첫 번째 span(시간) 찾기
                    time_span = WebDriverWait(slot, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "span.col:first-child"))
                    )
                    time_text = time_span.text.strip()
                    print(f"시간대 확인: {time_text}")
                    
                    # 시간을 숫자로 변환 (HH:MM 형식)
                    hour, minute = map(int, time_text.split(":"))
                    time_value = hour * 60 + minute  # 분 단위로 변환
                    
                    # 지정된 시간 범위 내에 있는지 확인
                    if start_minutes <= time_value <= end_minutes:
                        target_time = slot
                        target_time_text = time_text
                        break
                
                if target_time:
                    print(f"시간대 찾음: {target_time_text}")
                    # 신청 버튼 클릭
                    apply_btn = WebDriverWait(target_time, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-res"))
                    )
                    self.driver.execute_script("arguments[0].click();", apply_btn)
                    
                    # 예약 정보 페이지가 표시될 때까지 대기
                    print("예약 정보 페이지 로딩 대기 중...")
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "info_inner"))
                    )
                    
                    # 페이지가 완전히 로드될 때까지 대기
                    WebDriverWait(self.driver, 10).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                    try:
                        # 인증번호 처리
                        print("인증번호 입력 중...")
                        # 인증번호 요소가 로드될 때까지 대기
                        cert_number_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "span.color-04.f_w-600.f_size-22px"))
                        )
                        cert_number = cert_number_element.text.strip()
                        print(f"인증번호: {cert_number}")
                        
                        cert_input = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "certNoChk"))
                        )
                        self.driver.execute_script(f"arguments[0].value='{cert_number}';", cert_input)
                        
                        # 캡차 이미지 처리
                        print("캡차 이미지 처리 중...")
                        captcha_img = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "captImg"))
                        )
                        captcha_input = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "captAnswer"))
                        )
                        
                        # 새로고침 버튼 찾기
                        reload_btn = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.ID, "captReload"))
                        )
                        
                        # 캡차 인식 시도 (최대 3번)
                        for attempt in range(3):
                            print(f"캡차 인식 시도 {attempt + 1}/3")
                            
                            # 새로운 캡차 이미지 가져오기
                            captcha_img = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.ID, "captImg"))
                            )
                            
                            # 이미지를 canvas로 캡처하여 base64로 저장
                            script = """
                                var canvas = document.createElement('canvas');
                                var img = document.getElementById('captImg');
                                canvas.width = img.width;
                                canvas.height = img.height;
                                var ctx = canvas.getContext('2d');
                                ctx.drawImage(img, 0, 0);
                                return canvas.toDataURL('image/png');
                            """
                            img_base64 = self.driver.execute_script(script)
                            
                            # base64 데이터를 이미지로 변환하여 저장
                            img_data = base64.b64decode(img_base64.split(',')[1])
                            img_filename = f'captcha_{attempt + 1}.png'
                            with open(img_filename, 'wb') as f:
                                f.write(img_data)
                            print(f"캡차 이미지 저장됨: {img_filename}")
                            
                            # 현재 이미지 처리
                            captcha_text = self.process_captcha(img_filename)
                            if not captcha_text:
                                print(f"캡차 인식 실패 (시도 {attempt + 1}/3)")
                                if attempt < 2:
                                    continue
                                else:
                                    print("캡차 인식 최대 시도 횟수 초과")
                                    return False
                            
                            print(f"캡차 인식 결과: {captcha_text}")
                            
                            # 인식된 텍스트 입력
                            print("인식된 캡차 입력...")
                            self.driver.execute_script(f"arguments[0].value='{captcha_text}';", captcha_input)
                            
                            # 캡차 확인 버튼 클릭
                            captcha_check_btn = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.ID, "captCheck"))
                            )
                            self.driver.execute_script("arguments[0].click();", captcha_check_btn)
                            
                            # 알림창 처리
                            try:
                                alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                                alert_text = alert.text
                                print(f"알림창 메시지: {alert_text}")
                                alert.accept()
                                
                                if "일치하지 않습니다" in alert_text:
                                    print("캡차 인식 실패, 다시 시도합니다.")
                                    continue
                            except:
                                print("캡차 인식 성공!")
                                
                                # reCAPTCHA 처리
                                print("reCAPTCHA 처리 중...")
                                try:
                                    # reCAPTCHA iframe으로 전환
                                    recaptcha_iframe = WebDriverWait(self.driver, 10).until(
                                        EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[src*='recaptcha']"))
                                    )
                                    
                                    # reCAPTCHA 체크박스 클릭
                                    recaptcha_checkbox = WebDriverWait(self.driver, 10).until(
                                        EC.element_to_be_clickable((By.CLASS_NAME, "recaptcha-checkbox-border"))
                                    )
                                    self.driver.execute_script("arguments[0].click();", recaptcha_checkbox)
                                    
                                    # reCAPTCHA 성공 여부 확인
                                    try:
                                        print("reCAPTCHA 확인 중...")
                                        # 체크박스의 부모 요소가 checked 클래스를 가질 때까지 대기
                                        checkbox_parent = WebDriverWait(self.driver, 10).until(
                                            EC.presence_of_element_located((By.CLASS_NAME, "recaptcha-checkbox"))
                                        )
                                        
                                        # 최대 10초 동안 0.5초 간격으로 체크박스 상태 확인
                                        max_attempts = 20
                                        for attempt in range(max_attempts):
                                            if "recaptcha-checkbox-checked" in checkbox_parent.get_attribute("class"):
                                                print("reCAPTCHA 인증 성공!")
                                                break
                                            if attempt == max_attempts - 1:
                                                print("reCAPTCHA 체크박스 상태 확인 실패")
                                                return False
                                            time.sleep(0.5)
                                        
                                        # 기본 프레임으로 돌아가기
                                        self.driver.switch_to.default_content()
                                        
                                        # 페이지가 완전히 로드될 때까지 대기
                                        WebDriverWait(self.driver, 10).until(
                                            lambda driver: driver.execute_script("return document.readyState") == "complete"
                                        )
                                        
                                        # JavaScript로 예약 버튼 클릭
                                        print("예약 버튼 클릭 중...")
                                        self.driver.execute_script("golfSubmit();")
                                        
                                        # 예약 완료 확인
                                        try:
                                            alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                                            alert_text = alert.text
                                            print(f"알림창 메시지: {alert_text}")
                                            alert.accept()
                                            
                                            # 추가인증 메시지가 표시되면 reCAPTCHA 다시 시도
                                            if "추가인증을 하시기 바랍니다" in alert_text:
                                                print("추가인증 필요, reCAPTCHA 다시 시도...")
                                                
                                                # reCAPTCHA iframe으로 전환
                                                recaptcha_iframe = WebDriverWait(self.driver, 10).until(
                                                    EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[src*='recaptcha']"))
                                                )
                                                
                                                # reCAPTCHA 체크박스 클릭
                                                recaptcha_checkbox = WebDriverWait(self.driver, 10).until(
                                                    EC.element_to_be_clickable((By.CLASS_NAME, "recaptcha-checkbox-border"))
                                                )
                                                self.driver.execute_script("arguments[0].click();", recaptcha_checkbox)
                                                
                                                # reCAPTCHA 성공 여부 재확인
                                                print("reCAPTCHA 재확인 중...")
                                                # 체크박스의 부모 요소 찾기
                                                checkbox_parent = WebDriverWait(self.driver, 10).until(
                                                    EC.presence_of_element_located((By.CLASS_NAME, "recaptcha-checkbox"))
                                                )
                                                
                                                # 최대 10초 동안 0.5초 간격으로 체크박스 상태 확인
                                                for attempt in range(max_attempts):
                                                    if "recaptcha-checkbox-checked" in checkbox_parent.get_attribute("class"):
                                                        print("reCAPTCHA 재인증 성공!")
                                                        break
                                                    if attempt == max_attempts - 1:
                                                        print("reCAPTCHA 체크박스 상태 확인 실패")
                                                        return False
                                                    time.sleep(0.5)
                                                
                                                # 기본 프레임으로 돌아가기
                                                self.driver.switch_to.default_content()
                                                
                                                # 페이지가 완전히 로드될 때까지 대기
                                                WebDriverWait(self.driver, 10).until(
                                                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                                                )
                                                
                                                # JavaScript로 예약 버튼 다시 클릭
                                                print("예약 버튼 다시 클릭 중...")
                                                self.driver.execute_script("golfSubmit();")
                                                
                                                # 최종 예약 완료 확인
                                                try:
                                                    final_alert = WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                                                    final_alert_text = final_alert.text
                                                    print(f"최종 알림창 메시지: {final_alert_text}")
                                                    final_alert.accept()
                                                except:
                                                    pass
                                            
                                        except:
                                            pass
                                        
                                        print("예약 완료!")
                                        return True
                                    except Exception as e:
                                        print(f"reCAPTCHA 확인 중 오류 발생: {str(e)}")
                                        return False
                                    
                                except Exception as e:
                                    print(f"reCAPTCHA 처리 중 오류 발생: {str(e)}")
                                    return False
                    except Exception as e:
                        print(f"예약 처리 중 오류 발생: {str(e)}")
                        return False
                else:
                    print("해당 시간대를 찾을 수 없습니다.")
                    return False
            else:
                print(f"{self.target_club}를 찾을 수 없습니다.")
                return False
                
        except Exception as e:
            print(f"골프장 선택 중 오류 발생: {str(e)}")
            return False
            
    def make_reservation(self, time_slot):
        """시간대 선택 및 예약
        time_slot: HH:MM 형식의 문자열
        """
        try:
            # 시간대 선택
            time_element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{time_slot}')]"))
            )
            time_element.click()
            
            # 예약 버튼 클릭
            reserve_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.reserve-button"))
            )
            reserve_btn.click()
            
            # 예약 확인 팝업 확인
            confirm_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.confirm-button"))
            )
            confirm_btn.click()
            return True
        except Exception as e:
            print(f"예약 중 오류 발생: {str(e)}")
            return False
            
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()

def main():
    # 사용 예시
    reservation = OneTheClubGolfReservation()
    try:
        # 사용자 입력 받기
        print("\n=== 예약 정보 입력 ===")
        
        # 날짜 입력 받기
        while True:
            date_input = input("예약 날짜를 입력하세요 (YYYY-MM-DD 형식, 기본값: 2025-03-07): ").strip()
            if not date_input:  # 입력이 없으면 기본값 사용
                date_input = "2025-03-07"
            
            # 날짜 형식 검증
            try:
                year, month, day = map(int, date_input.split("-"))
                if len(date_input) == 10 and 2024 <= year <= 2025 and 1 <= month <= 12 and 1 <= day <= 31:
                    break
                else:
                    print("올바른 날짜 범위를 입력해주세요.")
            except:
                print("올바른 날짜 형식으로 입력해주세요 (YYYY-MM-DD)")
        
        # 골프장 입력 받기
        club_input = input(f"골프장 이름을 입력하세요 (기본값: {reservation.target_club}): ").strip()
        if club_input:
            reservation.set_target_club(club_input)
            
        # 시간 범위 입력 받기
        print("\n시간 범위 입력 (24시간 형식)")
        while True:
            try:
                start_time = input("시작 시간 (HH:MM 형식, 기본값: 13:30): ").strip()
                if not start_time:
                    start_hour, start_minute = 13, 30
                else:
                    start_hour, start_minute = map(int, start_time.split(":"))
                
                end_time = input("종료 시간 (HH:MM 형식, 기본값: 14:30): ").strip()
                if not end_time:
                    end_hour, end_minute = 14, 30
                else:
                    end_hour, end_minute = map(int, end_time.split(":"))
                
                if 0 <= start_hour <= 23 and 0 <= start_minute <= 59 and \
                   0 <= end_hour <= 23 and 0 <= end_minute <= 59:
                    break
                else:
                    print("올바른 시간 범위를 입력해주세요.")
            except:
                print("올바른 시간 형식으로 입력해주세요 (HH:MM)")
        
        # 입력받은 정보로 설정
        reservation.set_target_date(date_input)
        reservation.set_time_range(start_hour, start_minute, end_hour, end_minute)
        
        print("\n=== 입력된 예약 정보 ===")
        print(f"날짜: {reservation.target_date}")
        print(f"골프장: {reservation.target_club}")
        print(f"시간 범위: {start_hour:02d}:{start_minute:02d} ~ {end_hour:02d}:{end_minute:02d}")
        
        proceed = input("\n예약을 진행하시겠습니까? (y/n): ").strip().lower()
        if proceed != 'y':
            print("예약이 취소되었습니다.")
            return
            
        print("\n=== 예약 진행 중 ===")
        reservation.setup_driver()
        
        # 로그인 수행
        username = "ppsq1122"  # 실제 아이디 입력
        password = "710769"    # 실제 비밀번호 입력
        
        if reservation.login(username, password):
            print("로그인 확인됨")
            
            # 예약 페이지로 이동
            print("예약 페이지로 이동 중...")
            # 예약 페이지 버튼이 클릭 가능할 때까지 대기
            reservation_btn = WebDriverWait(reservation.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='/reservation/golf']"))
            )
            reservation.driver.execute_script("arguments[0].click();", reservation_btn)
            
            # 페이지 로드 완료 대기
            WebDriverWait(reservation.driver, 10).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # 날짜 선택
            if reservation.select_date(reservation.target_date):
                print(f"{reservation.target_date} 날짜 선택 성공")
                
                # 날짜 선택 후 페이지 업데이트 대기
                WebDriverWait(reservation.driver, 10).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                # 골프장 선택
                if reservation.select_golf_club():
                    print("골프장 선택 성공")
                else:
                    print("골프장 선택 실패")
            else:
                print("날짜 선택 실패")
        else:
            print("로그인 실패")
            
    except Exception as e:
        print(f"예약 프로세스 중 오류 발생: {str(e)}")
    finally:
        reservation.close()

if __name__ == "__main__":
    main() 