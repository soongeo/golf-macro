import pytest
import pytesseract
from PIL import Image
import os
from google.cloud import vision
import io
from dotenv import load_dotenv
from google.cloud.vision_v1 import ImageAnnotatorClient
from google.oauth2 import service_account
import json
import requests

# .env 파일 로드
load_dotenv()

def get_vision_client():
    """Google Cloud Vision API 클라이언트 생성"""
    # 서비스 계정 키 JSON 파일 경로 설정
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'golf-macro-79dbf0a87591.json'
    return vision.ImageAnnotatorClient()

def process_captcha_with_google_vision(img_path):
    """Google Cloud Vision API를 사용한 캡차 이미지 처리"""
    try:
        client = get_vision_client()
        
        # 이미지 파일 읽기
        with io.open(img_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)
        
        # OCR 수행
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if not texts:
            return []

        # 첫 번째 텍스트 결과에서 숫자만 추출
        full_text = texts[0].description.strip()
        results = []
        
        # 4자리 숫자 패턴 찾기
        for line in full_text.split('\n'):
            line = ''.join(filter(str.isdigit, line))
            if line and len(line) == 4:
                results.append(line)

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))

        return list(set(results))
    except Exception as e:
        print(f"Google Vision API 에러: {e}")
        return []

def preprocess_image(img_path, save_name):
    """이미지 전처리 함수"""
    # 이미지 로드
    img = Image.open(img_path)
    
    # 이미지 크기 4배 확대
    width, height = img.size
    img = img.resize((width * 4, height * 4), Image.Resampling.LANCZOS)
    
    # 그레이스케일로 변환
    img = img.convert('L')
    
    # 이진화 임계값 조정 (더 낮은 값으로 설정)
    threshold = 140  # 임계값 감소
    img = img.point(lambda x: 0 if x < threshold else 255, '1')
    
    # 처리된 이미지 저장
    processed_image_path = f'processed_{save_name}.png'
    img.save(processed_image_path, quality=100, optimize=False)  # 최고 품질로 저장
    print(f"Saved processed image as: {processed_image_path}")
    
    return processed_image_path

def process_captcha_with_ocrspace(img_path, save_name):
    """OCR.space API를 사용한 캡차 이미지 처리"""
    try:
        # OCR.space API 키 (무료 키 사용)
        api_key = os.getenv('OCRSPACE_API_KEY', 'K81428265788957')
        
        # API 엔드포인트
        url = 'https://api.ocr.space/parse/image'
        
        # 이미지 파일 열기
        with open(img_path, 'rb') as image_file:
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
            files = {
                'file': image_file
            }
            
            # API 요청
            response = requests.post(url, files=files, data=payload)
            result = response.json()
            
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
                
                return list(set(results))
            else:
                print(f"OCR.space API 에러: {result.get('ErrorMessage', '알 수 없는 에러')}")
                return []
                
    except Exception as e:
        print(f"OCR.space API 에러: {e}")
        return []

def process_captcha(img_path, save_name, use_google_vision=False, use_ocrspace=False):
    """캡차 이미지 처리 함수"""
    if use_google_vision:
        return process_captcha_with_google_vision(img_path)
    elif use_ocrspace:
        return process_captcha_with_ocrspace(img_path, save_name)
        
    # 이미지 전처리
    processed_img_path = preprocess_image(img_path, save_name)
    
    # OCR 설정
    configs = [
        '--psm 10 -c tessedit_char_whitelist=0123456789 -c tessedit_pageseg_mode=10 -c textord_min_linesize=1.0',
        '--psm 13 -c tessedit_char_whitelist=0123456789 -c tessedit_pageseg_mode=13 -c textord_min_linesize=1.0'
    ]
    
    results = []
    for config in configs:
        try:
            result = pytesseract.image_to_string(Image.open(processed_img_path), config=config).strip()
            if result and len(result) == 4 and result.isdigit():
                results.append(result)
        except Exception as e:
            print(f"OCR 에러 발생: {e}")
            continue
    
    return list(set(results))

def test_captcha_recognition_image1():
    """첫 번째 캡차 이미지 인식 테스트"""
    # Tesseract 경로 설정
    tesseract_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tesseract', 'tesseract.exe')
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # 테스트할 이미지 경로
    img_path = os.path.join('capchaImg', '1.png')
    
    # Tesseract OCR 수행
    results = process_captcha(img_path, "image1")
    print(f"Tesseract OCR 이미지 1 인식 결과들: {results}")
    
    # Google Vision OCR 수행
    try:
        google_results = process_captcha(img_path, "image1", use_google_vision=True)
        print(f"Google Vision OCR 이미지 1 인식 결과들: {google_results}")
        results.extend(google_results)
    except Exception as e:
        print(f"Google Vision API 에러: {e}")
    
    # OCR.space OCR 수행
    try:
        ocrspace_results = process_captcha(img_path, "image1", use_ocrspace=True)
        print(f"OCR.space OCR 이미지 1 인식 결과들: {ocrspace_results}")
        results.extend(ocrspace_results)
    except Exception as e:
        print(f"OCR.space API 에러: {e}")
    
    # 결과 검증
    results = list(set(results))  # 중복 제거
    print(f"최종 이미지 1 인식 결과들: {results}")
    assert '7171' in results, f"기대값 7171이 인식 결과 {results}에 없습니다."

def test_captcha_recognition_image2():
    """두 번째 캡차 이미지 인식 테스트"""
    # Tesseract 경로 설정
    tesseract_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tesseract', 'tesseract.exe')
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # 테스트할 이미지 경로
    img_path = os.path.join('capchaImg', '2.png')
    
    # Tesseract OCR 수행
    results = process_captcha(img_path, "image2")
    print(f"Tesseract OCR 이미지 2 인식 결과들: {results}")
    
    # Google Vision OCR 수행
    try:
        google_results = process_captcha(img_path, "image2", use_google_vision=True)
        print(f"Google Vision OCR 이미지 2 인식 결과들: {google_results}")
        results.extend(google_results)
    except Exception as e:
        print(f"Google Vision API 에러: {e}")
    
    # OCR.space OCR 수행
    try:
        ocrspace_results = process_captcha(img_path, "image2", use_ocrspace=True)
        print(f"OCR.space OCR 이미지 2 인식 결과들: {ocrspace_results}")
        results.extend(ocrspace_results)
    except Exception as e:
        print(f"OCR.space API 에러: {e}")
    
    # 결과 검증
    results = list(set(results))  # 중복 제거
    print(f"최종 이미지 2 인식 결과들: {results}")
    assert '0001' in results, f"기대값 0001이 인식 결과 {results}에 없습니다."

if __name__ == '__main__':
    test_captcha_recognition_image1()
    test_captcha_recognition_image2() 