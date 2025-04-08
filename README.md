# AI 토론 학습 도우미 (경기 토론 모형 기반)

이 애플리케이션은 경기 토론 수업 모형을 기반으로 토론 학습을 돕기 위한 AI 도우미입니다. Streamlit과 Gemini AI를 활용하여 개발되었습니다.

## 주요 기능

1. **토론 주제 추천받기**: 관심사를 입력하면 그에 맞는 토론 주제를 추천 받을 수 있습니다.
2. **찬반 논거 아이디어 보기**: 토론 주제를 입력하면 찬성/반대 측 논거 아이디어를 얻을 수 있습니다.
3. **경기 토론 수업 모형 단계 안내**: 경기 토론 수업 모형의 3단계에 대해 알아볼 수 있습니다.
4. **피드백 받기**: 토론 주제와 나의 의견/논거를 입력하면 간단한 피드백을 받을 수 있습니다.

## 설치 및 실행 방법

### 1. 필요 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. Gemini API 키 설정

#### 로컬 실행 시
1. 프로젝트 루트 디렉토리에 `.streamlit` 폴더를 생성하세요.
2. `.streamlit` 폴더 안에 `secrets.toml` 파일을 생성하고 다음 내용을 추가하세요:
```toml
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
```
3. `YOUR_API_KEY_HERE` 부분을 실제 Gemini API 키로 대체하세요.

#### Streamlit Cloud 배포 시
1. Streamlit Cloud 대시보드에서 앱 설정으로 이동하세요.
2. 'Settings' > 'Secrets' 메뉴에서 `GEMINI_API_KEY` 항목을 추가하세요.

### 3. 애플리케이션 실행

```bash
streamlit run app.py
```

## 사용 방법

1. 웹 브라우저에서 애플리케이션에 접속합니다 (기본 URL: http://localhost:8501).
2. 원하는 기능을 선택하고 필요한 정보를 입력한 후 해당 버튼을 클릭하여 결과를 확인합니다.
3. 사이드바의 안내를 참고하여 앱을 효과적으로 활용하세요.

## 기술 스택

- **언어**: Python
- **웹 프레임워크**: Streamlit
- **AI 모델**: Google Gemini API 