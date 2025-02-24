# 골프장 예약 매크로

원더클럽 골프장 예약 자동화 매크로입니다.

## 설치 방법

### 1. Python 설치하기
1. [Python 공식 웹사이트](https://www.python.org/downloads/)에 접속합니다.
2. "Download Python" 버튼을 클릭합니다. (Python 3.8 이상 버전 선택)
3. 다운로드된 설치 파일을 실행합니다.
4. 설치 시 반드시 "Add Python to PATH" 옵션을 체크해주세요.
5. "Install Now"를 클릭하여 설치를 진행합니다.

### 2. Chrome 브라우저 설치
1. [Chrome 다운로드 페이지](https://www.google.com/chrome/)에서 Chrome 브라우저를 다운로드합니다.
2. 설치 파일을 실행하여 Chrome을 설치합니다.

### 3. 프로그램 다운로드
1. [여기를 클릭하여](https://github.com/사용자이름/golf-macro/archive/refs/heads/main.zip) 프로그램 파일을 다운로드 받습니다.
2. 다운로드 받은 ZIP 파일을 찾습니다. (보통 '다운로드' 폴더에 있습니다)
3. ZIP 파일을 마우스 오른쪽 버튼으로 클릭하고 '압축 풀기' 또는 '모두 추출'을 선택합니다.
4. 압축을 풀 위치를 선택합니다. (예: C:\Users\사용자이름\Documents)
5. '압축 풀기' 또는 '추출' 버튼을 클릭합니다.

### 4. 필요한 패키지 설치
1. 윈도우 검색창에서 "cmd" 또는 "명령 프롬프트"를 검색하여 실행합니다.
2. 압축을 푼 폴더로 이동합니다. 예시:
   ```
   cd C:\Users\사용자이름\Documents\golf-macro-main
   ```
3. 아래 명령어를 실행하여 필요한 패키지를 설치합니다:
   ```
   pip install -r requirements.txt
   ```

## 프로그램 실행 방법

1. 명령 프롬프트(cmd)에서 프로그램 폴더로 이동한 후 아래 명령어를 실행합니다:
   ```
   python onetheclub_golf_reservation.py
   ```
2. 프로그램이 실행되면 화면의 안내에 따라 필요한 정보를 입력합니다.

## 주의사항

- Chrome 브라우저가 설치되어 있어야 합니다.
- 인터넷 연결이 안정적이어야 합니다.
- 자동화된 예약 시스템 사용 시 해당 사이트의 이용약관을 확인하시기 바랍니다.
- 프로그램 실행 중에는 Chrome 브라우저를 임의로 닫거나 조작하지 마세요.

## 문제 해결

### "python 명령어를 찾을 수 없습니다" 오류가 발생하는 경우
1. Python이 정상적으로 설치되었는지 확인합니다.
2. 윈도우를 재시작합니다.
3. 그래도 문제가 있다면 Python 설치 과정에서 "Add Python to PATH" 옵션을 체크했는지 확인하고, 필요한 경우 Python을 재설치합니다.

### "pip 명령어를 찾을 수 없습니다" 오류가 발생하는 경우
1. Python이 정상적으로 설치되었는지 확인합니다.
2. 윈도우를 재시작합니다.
3. 명령 프롬프트를 관리자 권한으로 실행해봅니다.

### 기타 오류가 발생하는 경우
1. 인터넷 연결을 확인합니다.
2. Chrome 브라우저가 최신 버전인지 확인합니다.
3. 모든 패키지가 정상적으로 설치되었는지 확인합니다. 