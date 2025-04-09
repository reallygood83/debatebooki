"""
AI 활용 경기 토론 수업 지원 도구 (간단 개발 버전)
초등학교 6학년 대상 경기 토론 수업 모형 기반의 토론 학습 도우미

실행에 필요한 라이브러리:
- streamlit==1.32.0
- google-generativeai==0.3.2

이 라이브러리들은 requirements.txt 파일에 명시되어 있습니다.
설치 방법: pip install -r requirements.txt

API 키 설정 방법:
1. 로컬 실행 시: `.streamlit/secrets.toml` 파일에 `GEMINI_API_KEY = "YOUR_API_KEY_HERE"` 형식으로 저장
2. Streamlit Cloud 배포 시: Streamlit Cloud의 'Settings' > 'Secrets' 메뉴에서 설정
"""

import streamlit as st
import google.generativeai as genai
import traceback
import re # Add re import

# ============================
# 페이지 설정 
# ============================
# 페이지 제목, 아이콘, 레이아웃 설정
st.set_page_config(
    page_title="AI 토론 친구",  # 브라우저 탭에 표시될 제목
    page_icon="🦉",            # 부엉이 아이콘으로 변경
    layout="wide",             # 페이지 레이아웃 (wide: 넓게, centered: 중앙 정렬)
    initial_sidebar_state="expanded"  # 사이드바 기본 확장 상태
)

# 앱 스타일 설정 - 6학년 학생에게 친근하고 생동감 있는 디자인
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Jua&family=Gaegu:wght@400;700&display=swap');
    
    /* 기본 스타일 */
    .main {
        background: linear-gradient(135deg, #fff9f9 0%, #fff5f2 100%);
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    .stApp {
        font-family: 'Gaegu', cursive;
    }
    
    /* 애니메이션 정의 */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes rainbow {
        0% { color: #ffb7c5; }
        14% { color: #ffc1cc; }
        28% { color: #ffd1dc; }
        42% { color: #ffe0e6; }
        56% { color: #fff0f5; }
        70% { color: #fff5f8; }
        84% { color: #ffeff5; }
        100% { color: #ffb7c5; }
    }
    
    /* 헤더 스타일 */
    h1 {
        font-family: 'Jua', sans-serif;
        color: #66545e;
        font-size: 2.2rem;
        padding: 0.8rem;
        background: linear-gradient(to right, #ffe0e6, #ffd1dc);
        border-radius: 15px;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(255, 183, 197, 0.2);
        border-left: 8px solid #ffb7c5;
    }
    
    .header-box {
        background: linear-gradient(135deg, #ffb7c5, #ffd1dc);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        color: #66545e;
        animation: float 6s ease-in-out infinite;
    }
    
    .header-box h1, .header-box p, .header-box span, .header-box div {
        color: #66545e !important;
        margin: 0;
    }
    
    .header-box .subtitle {
        color: #66545e !important;
        font-size: 1.2em;
        margin-top: 10px;
    }
    
    .header-box:hover {
        box-shadow: 0 6px 20px rgba(255, 183, 197, 0.15);
        transform: translateY(-3px);
    }
    
    .subtitle {
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 0.5rem;
        padding: 0.5rem 1rem;
        background: linear-gradient(120deg, #ffb7c5, #ffd1dc);
        color: #66545e;
        border-radius: 50px;
        display: inline-block;
        box-shadow: 0 4px 8px rgba(255, 183, 197, 0.2);
    }
    
    /* 섹션 헤더 */
    h2 {
        font-family: 'Jua', sans-serif;
        font-size: 1.6rem;
        padding: 0.8rem 1rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #66545e;
        background: linear-gradient(to right, #ffd1dc, #ffe0e6);
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(255, 183, 197, 0.3);
    }
    
    h3 {
        font-size: 1.3rem;
        color: #66545e;
        margin-top: 1.5rem;
        border-bottom: 3px dashed #ffb7c5;
        padding-bottom: 5px;
        display: inline-block;
    }
    
    p, li {
        font-size: 1.1rem;
        line-height: 1.5;
        color: #66545e;
    }
    
    /* 버튼 스타일 */
    .stButton>button {
        font-family: 'Jua', sans-serif;
        background: linear-gradient(to right, #ffb7c5, #ffd1dc);
        color: white !important;
        border-radius: 50px;
        font-weight: bold;
        border: none;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        width: 100%;
        margin-top: 8px;
        text-align: center;
    }
    
    .stButton>button:hover {
        background: linear-gradient(to right, #ffd1dc, #ffb7c5);
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .stButton>button p {
        color: white !important;
        margin: 0;
    }
    
    /* 결과 상자 스타일 수정 - 세로 길이 조정 */
    .stTextArea>div>div>textarea {
        max-height: 300px !important;
        min-height: 150px !important;
        border-radius: 12px;
        border: 1px solid #ffd1dc;
    }
    
    /* 텍스트 크기 조화 */
    .big-emoji {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* 확장 패널 */
    .stExpander {
        border-radius: 12px;
        border: 2px solid #ffe0e6;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    .stExpander:hover {
        border-color: #ffb7c5;
        box-shadow: 0 5px 15px rgba(255, 183, 197, 0.15);
        transform: translateY(-2px);
    }
    
    /* 입력 필드 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        font-family: 'Gaegu', cursive;
        font-size: 1.1rem;
        border-radius: 12px;
        border: 2px solid #ffe0e6;
    }
    
    .step-card-1, .step-card-2, .step-card-3 {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .step-card-1 h3, .step-card-2 h3, .step-card-3 h3 {
        font-size: 1.2rem;
        margin-top: 0;
    }
    
    .step-card-1 p, .step-card-2 p, .step-card-3 p, 
    .step-card-1 li, .step-card-2 li, .step-card-3 li {
        font-size: 1rem;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #fff5f2;
        padding: 0.8rem;
        border-radius: 50px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(255, 183, 197, 0.2);
        border: 2px solid rgba(255, 183, 197, 0.3);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 50px !important;
        padding: 0.6rem 1.2rem !important;
        font-family: 'Jua', sans-serif;
        color: #66545e !important;
        font-size: 1.4rem !important;  /* 글자 크기 증가 */
        font-weight: bold !important;  /* 볼드 처리 */
        border: none !important;
        transition: all 0.3s ease !important;  /* 부드러운 전환 효과 */
        letter-spacing: 0.05em !important;  /* 자간 추가 */
        text-shadow: 0 1px 1px rgba(255, 183, 197, 0.2) !important;  /* 텍스트 그림자 추가 */
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 183, 197, 0.3) !important;  /* 호버 시 배경색 변경 */
        transform: translateY(-2px) !important;  /* 호버 시 약간 위로 올라가는 효과 */
        box-shadow: 0 4px 8px rgba(255, 183, 197, 0.2) !important;  /* 호버 시 그림자 효과 */
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #ffb7c5 !important;
        color: white !important;
        box-shadow: 0 4px 8px rgba(255, 183, 197, 0.4) !important;
        transform: translateY(-2px) !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1) !important;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        padding: 1rem;
        background-color: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #ffe0e6;
    }
    
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* 토론 꿀팁 박스 */
    .tip-box {
        background: linear-gradient(135deg, #fff5f2 0%, #ffe0e6 100%);
        border-radius: 15px;
        padding: 15px;
        margin: 1rem 0;
        border-left: 5px solid #ffb7c5;
    }
    
    /* 성공 메시지 */
    .success-box {
        background: linear-gradient(135deg, #f0f8ff 0%, #e6f7ff 100%);
        border-radius: 12px;
        padding: 15px;
        margin: 1rem 0;
        border-left: 5px solid #a5d8ff;
    }
    
    /* 경고 메시지 */
    .warning-box {
        background: linear-gradient(135deg, #fff9f0 0%, #fff4e6 100%);
        border-radius: 12px;
        padding: 15px;
        margin: 1rem 0;
        border-left: 5px solid #ffd8a8;
    }
    
    /* 무지개 애니메이션 텍스트 */
    .rainbow-text {
        font-weight: bold;
        animation: rainbow 8s linear infinite;
    }
    
    /* 주제 추천 결과 컨테이너 스타일 */
    .recommendation-result {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
        border: 2px solid #ffb7c5;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* 결과 표시 영역 - 새로운 스타일 */
    .result-display {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem; 
        margin-bottom: 1.5rem;
        border: 2px solid #ffb7c5; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* 결과 헤더 스타일 */
    .result-header {
        color: #66545e; 
        border-bottom: 2px dashed #ffb7c5; 
        padding-bottom: 0.5rem;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    /* 사이드바 스타일 */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #fff9f9 0%, #fff5f2 100%);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 1rem;
    }
    
    /* 탭 컨테이너 스타일 */
    .tab-container {
        margin-bottom: 2rem;
    }
    
    /* 입력 필드 컨테이너 */
    .input-container {
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    /* 버튼 정렬 컨테이너 */
    .button-container-right {
        display: flex;
        justify-content: flex-end;
        margin-top: 1rem;
    }
    
    .button-container-center {
        display: flex;
        justify-content: center;
        margin-top: 1rem;
    }
    
    /* 카드 컨테이너 */
    .card-container {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border: 1px solid #ffe0e6;
    }
    
    /* 특수 구분선 */
    .divider {
        border-bottom: 2px dashed #ffb7c5;
        margin: 1.5rem 0;
    }
    
    /* 강조 텍스트 */
    .highlight-text {
        background-color: #fff5f2;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: bold;
        color: #66545e;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# 사이드바 추가
# ============================
with st.sidebar:
    st.markdown('<div class="big-emoji">🦉</div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; margin-top: 0;">🦉 토론부기 사용법</h2>', unsafe_allow_html=True)
    
    # 앱 사용법
    st.markdown("""
    안녕하세요! 저는 토론부기예요. 토론 수업을 더 재미있고 효과적으로 만들어 줄 친구랍니다.
    
    이 도구는 여러분에게 다음과 같은 기능을 제공해요:
    - 토론 주제 추천
    - 찬성/반대 의견 아이디어
    - 경기 토론 수업 모형 안내
    - 여러분의 의견에 대한 피드백
    """)
    
    # 토론 팁 섹션
    st.markdown("## 🦉 토론부기의 지혜로운 꿀팁!")
    
    # 팁 1
    st.subheader("1. 경청하기")
    st.info("부엉이는 귀가 좋아서 잘 들어요. 친구들 말도 집중해서 들어보세요.")
    
    # 팁 2
    st.subheader("2. 근거 말하기")
    st.info('"왜냐하면~", "예를 들면~"으로 이유를 설명하세요.')
    
    # 팁 3
    st.subheader("3. 질문하기")
    st.info('"왜 그렇게 생각해요?", "예시를 들어줄래요?"')
    
    # 팁 4
    st.subheader("4. 존중하기")
    st.info("다른 의견도 소중해요!")
    
    # 팁 5
    st.subheader("5. 마음 열기")
    st.info("내 생각이 바뀔 수도 있어요.")
    
    # 마무리 메시지
    st.success("토론은 정답을 찾는 게 아니라, 여러 생각을 나누는 거예요! 🦉✨")
    
    # 선생님을 위한 도움말
    with st.expander("선생님을 위한 도움말"):
        st.markdown("""
        ### API 키 설정 방법
        1. [Google AI Studio](https://aistudio.google.com/)에서 API 키를 발급받으세요.
        2. 발급받은 키를 입력 상자에 넣고 저장하면 됩니다.
        
        ### 수업 활용 Tip
        - 토론 주제는 학생들의 관심사와 연결해 보세요.
        - 찬반 의견을 나눠 역할극처럼 진행해 보세요.
        - 모든 학생이 최소 한 번씩 의견을 말할 수 있도록 해주세요.
        """)
        # ============================
# API 키 설정 및 초기화 부분
# ============================
try:
    api_key_loaded = False
    # Streamlit Secrets에서 API 키 로드
    if "GEMINI_API_KEY" in st.secrets:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=GEMINI_API_KEY)  # Gemini API 구성
        api_key_loaded = True
    else:
        # API 키가 설정되지 않은 경우 오류 메시지 표시 및 앱 중지
        st.error("오류: Gemini API 키가 Streamlit secrets에 설정되지 않았습니다. 좌측 메뉴의 'Settings' > 'Secrets'에서 키를 설정해주세요.")
        st.stop()  # API 키 없으면 앱 중지

except Exception as e:
    # API 설정 중 예외 발생 시 오류 메시지 표시 및 앱 중지
    st.error(f"Gemini API 설정 중 오류 발생: {e}")
    traceback.print_exc()  # 개발 중에는 전체 오류 로그 확인용
    st.stop()  # 설정 오류 시 앱 중지

# ============================
# 프롬프트 템플릿 정의 부분
# ============================

# 1. 토론 주제 추천 프롬프트 템플릿
# - 사용자의 관심사를 바탕으로 토론 주제 3가지를 추천하는 프롬프트
RECOMMEND_TOPIC_PROMPT_TEMPLATE = """
# 역할: 경기 토론 수업 모형 전문가 (초등학교 6학년 대상)
# 목표: 주어진 학년과 관심사에 맞춰, 경기 토론 수업 모형의 '다름과 마주하기' 단계에 적합하며 초등학교 6학년 학생들이 흥미를 느끼고 깊이 있게 탐구할 수 있는 토론 주제 3가지를 추천한다. 각 주제는 찬성과 반대 양측이 균형 있게 논거를 펼칠 수 있어야 하며(Source 31), 사회적 관련성이 드러나야 한다(Source 9, 10).
# 출력 형식:
## 주제 [번호]: [주제명]
### 간단한 배경 정보: [주제가 왜 중요하고 논쟁적인지 초등학생 눈높이에서 1-2문장 설명]
### 핵심 쟁점: [토론에서 다루어야 할 주요 질문이나 논쟁점 2-3가지 (예: ~하면 어떤 점이 좋을까?, ~하면 어떤 문제가 생길까?)]

# 입력 정보:
학년: 초등학교 6학년
관심사: {interest_input}

# 지침:
- 반드시 '경기 토론 수업 모형'의 핵심 원칙(다양한 관점 존중, 논쟁성 유지, 비판적 사고력 함양 - Source 2, 6, 7)을 바탕으로 주제를 선정한다.
- 초등학교 6학년의 인지 발달 수준(Source 22, 23)과 사회적 관심사(Source 25)를 고려하여 이해하기 쉽고 구체적인 용어를 사용한다(Source 31).
- 첨부된 문서의 추천 주제 예시('학교 스마트폰 금지', '의무 코딩 교육', '종이책 vs 디지털 기기' - Source 33, 39, 44)와 유사한 수준의 복잡성과 관련성을 갖도록 한다.
- 배경 정보와 핵심 쟁점은 학생들이 토론의 방향(1단계: 다름과 마주하기)을 잡는 데 직접적인 도움을 줄 수 있도록 명확하게 제시한다(Source 17, 18).
- '보이텔스바흐 합의' 원칙에 따라 특정 견해를 주입하거나 강요하는 느낌을 주지 않도록 중립적으로 작성한다(Source 5).

# 추천 주제 생성 시작:
"""

# 2. 찬반 논거 아이디어 제시 프롬프트 템플릿 (계속)
ARGUMENT_IDEAS_PROMPT_TEMPLATE = """
# 역할: 경기 토론 수업 모형 토론 코치 (초등학교 6학년 대상)
# 목표: 주어진 토론 주제에 대해, 초등학교 6학년 학생들이 경기 토론 수업 모형의 '다름을 이해하기'(Source 18) 단계를 준비하며 자신의 입장을 정하고 논거를 구체화하는 데 도움을 줄 수 있는 기본적인 찬성 및 반대 논거 아이디어를 각각 3가지씩 제시한다. 이는 토론의 시작점을 제공하기 위함이다.
# 출력 형식:
## [{topic_input}] 토론을 위한 논거 아이디어

### 찬성 측 논거 아이디어 (이렇게 생각해 볼 수 있어요):
1. [찬성 논거 1 - 학생들이 이해하기 쉬운 구체적인 이유 포함]
2. [찬성 논거 2 - 학생들이 이해하기 쉬운 구체적인 이유 포함]
3. [찬성 논거 3 - 학생들이 이해하기 쉬운 구체적인 이유 포함]

### 반대 측 논거 아이디어 (이렇게 생각해 볼 수 있어요):
1. [반대 논거 1 - 학생들이 이해하기 쉬운 구체적인 이유 포함]
2. [반대 논거 2 - 학생들이 이해하기 쉬운 구체적인 이유 포함]
3. [반대 논거 3 - 학생들이 이해하기 쉬운 구체적인 이유 포함]

# 입력 정보:
토론 주제: {topic_input}

# 지침:
- 제시되는 논거는 학생들이 토론의 출발점으로 삼을 수 있는 기본적인 아이디어여야 하며, 초등학교 6학년 수준(Source 22, 23)에 맞춰 너무 어렵거나 추상적이지 않아야 한다.
- 각 논거는 해당 입장을 뒷받침하는 간략하고 명확한 이유를 포함하여 학생들이 논리적 연결을 쉽게 파악하도록 돕는다.
- '다름을 이해하기' 단계에서 필요한 질문과 반박(Source 18, 19)으로 이어질 수 있도록, 각 입장의 핵심적인 주장을 담는 것이 좋다.
- 긍정적이고 건설적인 토론(Source 27)을 유도하는 중립적인 표현을 사용한다.
- 첨부된 문서의 논거 예시('스마트폰 금지 찬반', '코딩 교육 찬반', '종이책/디지털 기기 찬반'의 논거 수준 참고)를 반영한다(Source 33-36, 39-42, 44-46).

# 논거 아이디어 생성 시작:
"""

# 3. 피드백 제공 프롬프트 템플릿
# - 사용자가 입력한 의견/논거에 대한 건설적인 피드백을 제공하는 프롬프트
FEEDBACK_PROMPT_TEMPLATE = """
# 역할: 경기 토론 수업 모형 피드백 조력자 (초등학교 6학년 대상)
# 목표: 학생이 제시한 특정 토론 주제에 대한 의견이나 논거를 분석하고, 경기 토론 수업 모형의 관점(특히 '다름을 이해하기' 및 '다름과 공존하기' 단계 지향)에서 건설적인 피드백을 제공한다. 피드백은 학생의 생각을 존중하며 더 깊은 사고(Source 13, 16)와 논리적 발전을 유도하는 데 초점을 맞춘다.
# 출력 형식:
### 학생 의견 분석 및 피드백

* **주제 관련성:** [입력된 내용이 토론 주제와 얼마나 관련 있는지 간단히 평가 (예: 주제와 직접적으로 관련 있어요, 주제와 조금 관련 있어요, 주제와 관련성을 찾기 어려워요)]
* **입장 구분:** [찬성, 반대, 중립 중 어느 입장에 더 가까운지 또는 명확한 입장이 드러나는지 평가 (예: 찬성 입장에 가까워 보여요, 반대 입장이 명확하게 드러나요, 여러 입장을 함께 고려하고 있어요)]
* **더 생각해 볼 점 (건설적 피드백):** [학생의 논거를 발전시키기 위한 구체적인 제안 1가지. 경기 토론 수업 모형의 '다름과 공존하기'(Source 20, 21)를 염두에 둔 질문 형태나 근거 보강(Source 56), 명확화 제안 등]

# 입력 정보:
토론 주제: {topic_input}
학생 입력 내용: {student_argument_input}

# 지침:
- 피드백은 초등학교 6학년 학생(Source 22, 25)이 이해하기 쉽도록 긍정적이고 격려하는 어조로 작성하며, 비판적이거나 평가적인 말투는 피한다(Source 27).
- 학생의 주장을 단순히 판단하기보다는, 논리적으로 더 탄탄하게 만들거나 다른 관점을 고려하도록 돕는 데 중점을 둔다.
- '더 생각해 볼 점' 항목에서는 다음 중 하나의 방향으로 구체적인 질문이나 제안을 한다:
    1.  **근거/예시 추가 제안:** "주장하는 내용을 뒷받침할 만한 구체적인 경험이나 예시를 한 가지 더 이야기해 줄 수 있을까요?"
    2.  **다른 관점 고려 유도 (다름과 공존하기):** "혹시 나와 다른 생각을 가진 친구가 이 의견을 들으면 어떤 질문을 할 수 있을지 상상해 볼까요?" (Source 20, 21)
    3.  **명확화/구체화 제안:** "이 의견에서 가장 중요하다고 생각하는 부분을 한 문장으로 다시 설명해 줄 수 있을까요?"
    4.  **논리 연결 확인:** "왜 그렇게 생각하는지 이유를 조금 더 자세히 설명해주면 친구들이 더 잘 이해할 수 있을 것 같아요."
- 학생이 스스로 생각하고 탐구하도록 질문 형태로 유도한다(Source 16).
- '보이텔스바흐 합의' 원칙(강제성 금지)에 따라 특정 입장을 정답으로 여기거나 강요하지 않는다(Source 5).

# 피드백 생성 시작:
"""

# ============================
# 유틸리티 함수 정의 부분
# ============================

# Gemini API 호출 함수
def get_gemini_response(prompt, model="gemini-2.0-flash"):
    """
    Gemini API를 호출하여 응답을 받아오는 함수
    
    매개변수:
    - prompt (str): API에 전송할 프롬프트 텍스트
    - model (str): 사용할 Gemini 모델명 (기본값: 'gemini-2.0-flash')
    
    반환값:
    - str: API 응답 텍스트 또는 오류 발생 시 None
    """
    try:
        # Gemini 모델 초기화
        model = genai.GenerativeModel(model)
        # 컨텐츠 생성 요청
        response = model.generate_content(prompt)
        # 응답 텍스트 반환
        return response.text
    except Exception as e:
        # 오류 발생 시 화면에 오류 메시지 표시
        st.error(f"API 호출 중 오류 발생: {str(e)}")
        # 디버깅을 위한 상세 오류 로그 출력
        traceback.print_exc()  # 개발 중에는 전체 오류 로그 확인용
        # 오류 시 None 반환
        return None

# ============================
# 앱 UI 구성 부분
# ============================

# 앱 타이틀 및 설명 - 핑크색 배경 추가
with st.container():
    # 스타일 추가
    st.markdown("""
    <style>
    /* 전체 컨테이너 스타일 */
    .main-header {
        background-color: #ffcdd2;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
    }
    
    /* 서브타이틀 스타일 */
    .subtitle {
        font-weight: bold;
        font-size: 1.4rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* 숫자 원형 스타일 */
    .number-circle {
        background-color: #ffcdd2;
        color: white;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 30px;
        font-weight: bold;
        margin: 0 auto;
    }
    
    /* 섹션 제목 스타일 */
    .section-title {
        font-weight: bold;
        color: #333333;
        margin-top: 1rem;
        font-size: 1.2rem;
    }
    
    /* 단계별 설명 컨테이너 */
    .step-container {
        background-color: #f8f8f8;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* 푸터 스타일 */
    .footer {
        text-align: center;
        padding: 1rem;
        margin-top: 2rem;
        border-top: 2px solid #ffe0e6;
        background-color: #fff5f2;
        border-radius: 0 0 10px 10px;
    }
    
    .footer-content {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    .footer-heart {
        color: #ff6b81;
        font-size: 1.2em;
        animation: heartbeat 1.5s infinite;
    }
    
    @keyframes heartbeat {
        0% { transform: scale(1); }
        15% { transform: scale(1.15); }
        30% { transform: scale(1); }
        45% { transform: scale(1.15); }
        60% { transform: scale(1); }
    }
    </style>
    
    <div class="main-header">
        <h1 style="margin: 0; font-size: 1.8rem; text-align: center;">
            <span style="margin-right: 10px;">🦉</span>토론부기 - 지혜로운 토론 친구
        </h1>
        <p class="subtitle" style="margin-top: 0.7rem;">AI활용 경기 토론 수업 모형 지원 도구</p>
    </div>
    """, unsafe_allow_html=True)

# 안내 메시지 
st.info("아래 탭을 선택하여 각 기능을 사용해보세요! ✨")

# 탭 메뉴로 기능 분리
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "**📚 경기 토론 수업 모형**", 
    "**🔍 토론 주제 추천**", 
    "**💡 찬반 논거 아이디어**", 
    "**📝 의견 피드백 받기**",
    "**🤝 토론 마무리하기**"
])

# ============================
# 1. 경기 토론 수업 모형 안내 기능
# ============================
with tab1:
    # 커스텀 CSS 스타일
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        * {
            font-family: 'Noto Sans KR', sans-serif;
        }
        
        .main {
            background: linear-gradient(135deg, #fff9f9 0%, #fff5f2 100%);
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #66545e;
            line-height: 1.4;
            margin-bottom: 0.8rem;
        }
        
        /* 헤더 스타일 */
        .header {
            background: linear-gradient(135deg, #ffb7c5, #ffd1dc);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            color: #66545e;
            margin: 0;
            padding: 10px 0;
            font-size: 2.2em;
        }
        
        .header p {
            color: #66545e;
            margin: 0;
            font-size: 1.2em;
        }
        
        /* 카드 스타일 */
        .card {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        
        /* 원칙 카드 스타일 */
        .principle-card {
            background-color: #fff5f2;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #ffb7c5;
        }
        
        /* 단계 카드 스타일 */
        .step-card {
            background-color: #fff5f2;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #ffd1dc;
        }
        
        .step-number {
            background-color: #ffb7c5;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2em;
            margin-right: 15px;
            float: left;
        }
        
        .step-content {
            margin-left: 55px;
        }
        
        /* 목표 카드 스타일 */
        .goal-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            height: 100%;
            border: 1px solid #ffe0e6;
        }
        
        .goal-icon {
            background-color: #ffd1dc;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 10px auto;
        }
        
        /* 예시 박스 스타일 */
        .example-box {
            background-color: white;
            border-radius: 8px;
            padding: 15px;
            margin-top: 10px;
            border: 1px solid #ffe0e6;
        }
        
        /* 특징 스타일 */
        .feature-box {
            background-color: #ffeef2;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        /* 둥근 원 네임택 */
        .circle-tag {
            display: inline-block;
            background-color: #ffb7c5;
            color: white;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            text-align: center;
            line-height: 25px;
            margin-right: 10px;
        }
        
        /* 목록 스타일 */
        ul.custom-list {
            list-style-type: none;
            padding-left: 0;
        }
        
        ul.custom-list li {
            position: relative;
            padding-left: 25px;
            margin-bottom: 8px;
        }
        
        ul.custom-list li:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #ffb7c5;
            font-weight: bold;
            font-size: 1.5em;
        }
        
        /* 푸터 스타일 */
        .footer {
            text-align: center;
            padding: 20px;
            color: #66545e;
            font-size: 0.8em;
            margin-top: 50px;
        }
        
        /* 섹션 타이틀 이모지 스타일 */
        .section-emoji {
            font-size: 1.2em;
            margin-right: 0.5rem;
            vertical-align: middle;
        }
    </style>
    """, unsafe_allow_html=True)

    # SVG 아이콘 함수
    def get_svg_icon(icon_name):
        icons = {
            "critical_thinking": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" width="24" height="24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>""",
            "collaboration": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" width="24" height="24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>""",
            "diversity": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" width="24" height="24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
            </svg>""",
            "citizen": """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" width="24" height="24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>"""
        }
        return icons.get(icon_name, "")

    # 헤더
    st.markdown("""
    <div class="header">
        <h1>📚 경기 토론 수업 모형</h1>
        <p>다름과 공존하는 경기토론교육 모형</p>
    </div>
    """, unsafe_allow_html=True)

    # 보이텔스바흐 합의 원칙
    st.markdown("""
    <div class="card">
        <h2><span class="section-emoji">📜</span> 보이텔스바흐 합의 원칙</h2>
        <p>경기 토론 수업 모형은 다음 세 가지 핵심 원칙에 기반합니다:</p>
    </div>
    """, unsafe_allow_html=True)

    principles_col1, principles_col2, principles_col3 = st.columns(3)

    with principles_col1:
        st.markdown("""
        <div class="principle-card">
            <div style="display: flex; align-items: center;">
                <div class="circle-tag">1</div>
                <h3 style="margin: 0;">강제성의 금지</h3>
            </div>
            <p>교사는 특정 견해를 주입하거나 강요해서는 안 됩니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with principles_col2:
        st.markdown("""
        <div class="principle-card">
            <div style="display: flex; align-items: center;">
                <div class="circle-tag">2</div>
                <h3 style="margin: 0;">논쟁성의 유지</h3>
            </div>
            <p>사회적으로 논쟁적인 주제는 교실에서도 다루어져야 하며, 다양한 관점을 탐색하는 기회를 제공해야 합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with principles_col3:
        st.markdown("""
        <div class="principle-card">
            <div style="display: flex; align-items: center;">
                <div class="circle-tag">3</div>
                <h3 style="margin: 0;">정치적 행위 능력의 강화</h3>
            </div>
            <p>학생들은 토론을 통해 사회 문제에 대한 비판적 사고력을 키우고 민주 시민으로서의 책임감을 함양해야 합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    # 핵심 특징
    st.markdown("""
    <div class="feature-box">
        <h2><span class="section-emoji">💬</span> 핵심 특징: 쟁점 중심 토론 교육</h2>
        <p>학생들이 특정 사회적 이슈나 논쟁거리에 대해 깊이 있게 탐구하고 자신의 입장을 논리적으로 펼치는 것을 강조합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # 3단계 프로세스
    st.markdown("""
    <div class="card">
        <h2><span class="section-emoji">🔄</span> 토론 수업 3단계 프로세스</h2>
    </div>
    """, unsafe_allow_html=True)

    # 1단계: 다름과 마주하기
    st.markdown("""
    <div class="step-card">
        <div class="step-number">1</div>
        <div class="step-content">
            <h3>🔎 다름과 마주하기</h3>
            <ul class="custom-list">
                <li>토론 주제를 처음 접하고, 관련 자료를 조사</li>
                <li>핵심 쟁점을 파악하고 토론의 방향 설정</li>
                <li>브레인스토밍을 통해 주제에 대한 생각을 자유롭게 표현</li>
                <li>핵심 용어를 정의하고 토론의 성격 파악</li>
            </ul>
            <div class="example-box">
                <p style="font-size: 0.9em; font-style: italic; margin: 0;">
                    <strong>예시:</strong> 해외여행 시 등산복 착용에 대한 토론을 준비할 때, 관련 기사를 찾아보고 자신의 경험을 떠올리며 질문을 던질 수 있습니다.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2단계: 다름을 이해하기
    st.markdown("""
    <div class="step-card">
        <div class="step-number">2</div>
        <div class="step-content">
            <h3>🤔 다름을 이해하기</h3>
            <ul class="custom-list">
                <li>질문과 반박을 통해 다양한 관점을 이해</li>
                <li>자신의 주장을 논리적으로 펼치기</li>
                <li>상대방의 주장을 주의 깊게 듣고 논리적 허점 파악</li>
                <li>적절한 질문을 통해 상대방의 논리 검증</li>
            </ul>
            <div class="example-box">
                <p style="font-size: 0.9em; font-style: italic; margin: 0;">
                    <strong>예시:</strong> 학교 내 스마트폰 사용 금지 토론에서 찬성 측은 학업 집중도 향상을, 반대 측은 학습 도구로서의 활용 가능성을 근거로 제시합니다.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3단계: 다름과 공존하기
    st.markdown("""
    <div class="step-card">
        <div class="step-number">3</div>
        <div class="step-content">
            <h3>🤝 다름과 공존하기</h3>
            <ul class="custom-list">
                <li>공동의 이익을 위한 실질적인 해결책 모색</li>
                <li>다양한 관점을 종합하고 서로의 의견을 존중</li>
                <li>합의점을 찾아가는 과정을 경험</li>
                <li>공동체에 도움이 되는 정책 제안 도출</li>
            </ul>
            <div class="example-box">
                <p style="font-size: 0.9em; font-style: italic; margin: 0;">
                    <strong>예시:</strong> 초등학교 급식 메뉴 토론에서 영양 균형, 학생 선호도, 환경 문제 등 다양한 요소를 고려하여 개선 방안을 함께 제안합니다.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 교육 목표
    st.markdown("""
    <div class="card">
        <h2 style="text-align: center; margin-bottom: 20px;"><span class="section-emoji">🎯</span> 교육 목표</h2>
    </div>
    """, unsafe_allow_html=True)

    goal_col1, goal_col2, goal_col3, goal_col4 = st.columns(4)

    with goal_col1:
        st.markdown(f"""
        <div class="goal-card">
            <div class="goal-icon">
                {get_svg_icon("critical_thinking")}
            </div>
            <h3>비판적 사고력</h3>
            <p style="font-size: 0.9em; margin-top: 10px;">이슈를 다양한 관점에서 분석하고 평가하는 능력 향상</p>
        </div>
        """, unsafe_allow_html=True)

    with goal_col2:
        st.markdown(f"""
        <div class="goal-card">
            <div class="goal-icon">
                {get_svg_icon("collaboration")}
            </div>
            <h3>협력적 문제 해결 능력</h3>
            <p style="font-size: 0.9em; margin-top: 10px;">다양한 의견을 존중하며 함께 해결책을 모색하는 능력 함양</p>
        </div>
        """, unsafe_allow_html=True)

    with goal_col3:
        st.markdown(f"""
        <div class="goal-card">
            <div class="goal-icon">
                {get_svg_icon("diversity")}
            </div>
            <h3>다양성 존중</h3>
            <p style="font-size: 0.9em; margin-top: 10px;">서로 다른 의견과 관점을 존중하고 이해하는 태도 배양</p>
        </div>
        """, unsafe_allow_html=True)

    with goal_col4:
        st.markdown(f"""
        <div class="goal-card">
            <div class="goal-icon">
                {get_svg_icon("citizen")}
            </div>
            <h3>민주 시민 역량</h3>
            <p style="font-size: 0.9em; margin-top: 10px;">사회 문제에 관심을 갖고 책임감 있게 참여하는 시민 의식 함양</p>
        </div>
        """, unsafe_allow_html=True)

    # 토론 모형 적용 팁
    with st.expander("토론 모형 적용 팁"):
        st.markdown("""
        ### 🌟 토론 수업 진행 팁
        
        1. **주제 선정**: 학생들의 관심사와 연결된 주제를 선택하거나, 다양한 관점에서 논의할 수 있는 쟁점을 고르세요.
        
        2. **자료 준비**: 다양한 관점의 자료를 미리 준비하여 학생들이 균형 잡힌 시각을 가질 수 있도록 지원하세요.
        
        3. **토론 규칙**: 상대방 의견 존중, 발언 시간 지키기, 논리적 근거 제시하기 등의 기본 규칙을 함께 정하세요.
        
        4. **교사의 역할**: 중립적인 입장에서 토론을 진행하며, 토론이 한쪽으로 치우치지 않도록 조정해주세요.
        
        5. **성찰 활동**: 토론 후에는 자신의 생각이 어떻게 변화했는지, 무엇을 배웠는지 성찰하는 시간을 가지세요.
        """)

    # 토론 주제 예시
    with st.expander("초등학교 토론 주제 예시"):
        st.markdown("""
        ### 📚 초등학교 토론 주제 예시
        
        #### 📝 학교생활 관련
        - 학교에서 스마트폰 사용은 허용되어야 할까요?
        - 교복(교칙)은 필요할까요?
        - 방학 숙제는 없애야 할까요?
        
        #### 🌍 환경 및 사회 이슈
        - 일회용 플라스틱은 금지해야 할까요?
        - 로봇이 인간의 일자리를 대체하는 것은 좋은 일일까요?
        - 반려동물 키우기는 제한되어야 할까요?
        
        #### 💭 가치 및 윤리 관련
        - SNS는 아이들에게 도움이 될까요, 해로울까요?
        - 게임은 취미 활동으로 적절한가요?
        - 어린이들도 자신의 모습을 꾸밀 권리가 있을까요?
        """)

    # 푸터
    st.markdown("""
    <div class="footer">
        <p>© 2025 경기도교육청 | 다름과 공존하는 경기토론교육 모형</p>
    </div>
    """, unsafe_allow_html=True)

    # 도구 안내 섹션
    st.success("""
    ### 👉 이 도구는 위 세 단계 모두 도움을 줄 수 있어요!
    
    * **토론 주제 추천**은 '다름과 마주하기'를 도와줘요
    * **찬반 논거 아이디어**는 '다름을 이해하기'를 도와줘요
    * **피드백 받기와 마무리 활동**은 '다름과 공존하기'를 연습하는데 도움이 돼요
    """)

# ============================
# 2. 토론 주제 추천 기능
# ============================
with tab2:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.header("🔍 토론 주제 추천받기")

    # 토론 주제 예시 설명
    with st.expander("토론 주제란?", expanded=False):
        st.markdown("""
        <div style="background-color: #fff5f2; border-radius: 12px; padding: 1rem; border-left: 5px solid #ffd1dc;">
        친구들이 관심을 가질 만한 다양한 주제를 추천해 줄 거야! 예를 들면:
        
        - **학교 스마트폰 사용** - 학교에서 스마트폰을 사용하는 것이 좋을까요? 
        - **로봇 반려동물** - 진짜 동물 대신 로봇 반려동물을 키우는 것이 좋을까요?
        - **학교 유니폼** - 학생들이 교복(유니폼)을 입어야 할까요?
        
        이런 주제들에 대해 친구들과 함께 다양한 생각을 나눌 수 있어요! 😊
        </div>
        """, unsafe_allow_html=True)

    # 사용자 관심사 입력 필드 (고유 키 부여)
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<label style="font-weight: bold; margin-bottom: 0.5rem; display: block;">어떤 것에 관심이 있니? (예: 게임, 환경, 학교, 미래 기술 등)</label>', unsafe_allow_html=True)
    
    # 입력 필드를 한 줄로 배치
    topic_interest = st.text_input("", 
                               key="topic_interest_input", 
                               placeholder="관심 있는 주제를 입력해 보세요!")
    
    # 버튼을 중앙에 배치
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        button_clicked = st.button("주제 추천 받기 🚀", key="topic_recommend_button", use_container_width=True)
    
    # 결과 컨테이너 미리 생성
    result_container = st.container()
    
    # 버튼 클릭 시 처리
    if button_clicked:
        if not topic_interest:
            # 입력값이 없을 경우 친근한 메시지
            st.warning("관심 있는 것을 알려주면 재미있는 토론 주제를 찾아줄게요! 😊")
        else:
            # 로딩 상태 표시하며 API 호출
            with st.spinner("토론 주제를 찾고 있어요... 조금만 기다려 주세요! 🔍"):
                # 입력값을 프롬프트에 포맷팅
                prompt = RECOMMEND_TOPIC_PROMPT_TEMPLATE.format(interest_input=topic_interest)
                # API 호출하여 응답 받기
                response = get_gemini_response(prompt)
                
                if response:
                    # 응답 결과를 세션 상태에 저장 (다른 기능에서도 참조 가능)
                    st.session_state.topic_recommendations = response
                    
                    # 결과를 컨테이너에 표시 (더 넓은 크기로)
                    with result_container:
                        st.subheader(f"'{topic_interest}'에 관한 토론 주제 추천 📋")
                        
                        # Streamlit의 기본 컴포넌트로 결과 표시
                        st.markdown(response)
                        
                        st.success("이 주제들 중에 마음에 드는 것이 있다면, '찬반 논거 아이디어 보기' 탭을 선택해 보세요! 👇")
                else:
                    with result_container:
                        st.error("앗! 주제를 찾는데 문제가 생겼어요. 다른 관심사를 입력해 볼까요?")
    
    st.markdown('</div>', unsafe_allow_html=True) # input-container 닫기
    st.markdown('</div>', unsafe_allow_html=True) # card-container 닫기

# ============================
# 3. 찬반 논거 아이디어 보기 기능
# ============================
with tab3:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.header("💡 찬반 논거 아이디어 보기")

    # 논거 아이디어란 무엇인지 설명
    with st.expander("논거 아이디어가 뭐예요?", expanded=False):
        st.markdown("""
        <div style="background-color: #ffeef2; border-radius: 12px; padding: 1rem; border-left: 5px solid #ffd1dc;">
        <strong>논거 아이디어</strong>는 토론에서 자신의 주장을 뒷받침하는 근거나 이유를 말해요! 
        
        예를 들어 '학교에서 스마트폰 사용 허용'이라는 주제를 토론한다면:
        
        <strong>찬성 의견의 논거</strong>로는:
        <ul>
        <li>"긴급 상황에서 부모님께 연락할 수 있어요"</li>
        <li>"인터넷 검색으로 수업 중 모르는 내용을 바로 찾아볼 수 있어요"</li>
        </ul>
        
        <strong>반대 의견의 논거</strong>로는:
        <ul>
        <li>"게임이나 SNS에 집중하느라 수업에 집중하기 어려워요"</li>
        <li>"친구들과 직접 대화하는 시간이 줄어들 수 있어요"</li>
        </ul>
        
        이런 식으로 자신의 주장을 뒷받침하는 여러 이유들을 <strong>논거</strong>라고 해요! 😊
        </div>
        """, unsafe_allow_html=True)

    # 세션 상태 초기화 (버튼 클릭 추적용)
    if 'selected_topic_for_tab3' not in st.session_state:
        st.session_state.selected_topic_for_tab3 = None

    # 이전 단계에서 추천받은 주제가 있다면 버튼과 함께 표시
    recommended_topics = []
    if 'topic_recommendations' in st.session_state and st.session_state.topic_recommendations:
        raw_recommendations = st.session_state.topic_recommendations
        # 정규 표현식을 사용하여 "## 주제 [번호]: [주제명]" 형식 추출
        recommended_topics = re.findall(r"## 주제 \[\d+\]: (.*?)\n", raw_recommendations)
        
        if recommended_topics:
            with st.expander("추천받은 주제를 사용하시겠어요?", expanded=True):
                st.info("위에서 추천받은 주제 중 하나를 선택하여 바로 논거 아이디어를 찾아보세요! 👇")
                # 주제 버튼들을 가로로 나열 (여러 개일 경우 여러 줄로)
                cols = st.columns(min(len(recommended_topics), 3))  # 한 줄에 최대 3개
                for i, topic_title in enumerate(recommended_topics):
                    with cols[i % 3]:  # 3개씩 나눠서 배치
                        # 각 주제에 대한 버튼 생성
                        button_key = f"use_topic_{i}"
                        if st.button(f"➡️ '{topic_title}' 사용하기", key=button_key, use_container_width=True):
                            # 버튼 클릭 시 해당 주제를 세션 상태에 저장하고 입력 필드 업데이트 준비
                            st.session_state.selected_topic_for_tab3 = topic_title
                            # Streamlit이 재실행되면서 아래 text_input의 value가 업데이트됨
                            st.rerun() # 입력 필드 값을 즉시 업데이트하기 위해 rerun

    # 토론 주제 입력 필드 (고유 키 부여) - 버튼 클릭 시 업데이트됨
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<label style="font-weight: bold; margin-bottom: 0.5rem; display: block;">📋 어떤 주제에 대한 논거 아이디어가 필요하니?</label>', unsafe_allow_html=True)
    
    # 버튼 클릭으로 선택된 주제가 있으면 해당 주제를 기본값으로 사용
    argument_topic_value = st.session_state.selected_topic_for_tab3 if st.session_state.selected_topic_for_tab3 else ""
    argument_topic = st.text_input("",
                            value=argument_topic_value, # 선택된 주제를 값으로 설정
                            key="argument_topic_input",
                            placeholder="토론하고 싶은 주제를 입력하거나 위에서 선택하세요!")
    
    # 버튼을 중앙에 배치
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        button_clicked = st.button("논거 아이디어 보기 💭", key="argument_idea_button", use_container_width=True)
    
    # 결과 컨테이너 미리 생성
    result_container = st.container()
    
    # 버튼 클릭 시 처리
    if button_clicked:
        # 버튼 클릭 시 선택된 주제 상태 초기화 (다음에 직접 입력 가능하도록)
        st.session_state.selected_topic_for_tab3 = None 
        
        # 입력 필드에서 최종 주제 가져오기
        current_argument_topic = st.session_state.argument_topic_input # text_input의 현재 값 사용
        
        if not current_argument_topic:
            # 입력값이 없을 경우 경고 메시지
            st.warning("토론하고 싶은 주제를 알려주면 찬성/반대 의견을 제시해 줄게요! 🙂")
        else:
            # 로딩 상태 표시하며 API 호출
            with st.spinner("찬성과 반대 의견을 생각하고 있어요... 잠시만요! 🧠"):
                # 입력값을 프롬프트에 포맷팅
                prompt = ARGUMENT_IDEAS_PROMPT_TEMPLATE.format(topic_input=current_argument_topic)
                # API 호출하여 응답 받기
                response = get_gemini_response(prompt)
                
                if response:
                    # 응답 결과를 세션 상태에 저장
                    st.session_state.argument_response = response
                    # 사용된 주제를 세션 상태에 저장 (Tab 4에서 사용)
                    st.session_state.argument_topic = current_argument_topic 
                    
                    # 결과를 컨테이너에 표시 (더 넓은 크기로)
                    with result_container:
                        st.subheader(f"'{current_argument_topic}'에 대한 찬반 논거 아이디어 ⚖️")
                        
                        # Streamlit의 기본 컴포넌트로 결과 표시
                        st.markdown(response)
                        
                        st.success("이제 이 아이디어들을 바탕으로 나만의 의견을 만들어 보세요! '의견 피드백 받기' 탭으로 이동해 의견을 확인받을 수 있어요 👇")
                else:
                    with result_container:
                        st.error("아이디어를 찾는데 문제가 생겼어요. 다른 주제로 시도해볼까요?")
    
    st.markdown('</div>', unsafe_allow_html=True) # input-container 닫기
    st.markdown('</div>', unsafe_allow_html=True) # card-container 닫기

# ============================
# 4. 간단 피드백 받기 기능
# ============================
with tab4:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.header("📝 내 의견 피드백 받기")

    # 피드백이란 무엇인지 설명
    with st.expander("피드백은 어떻게 받을 수 있나요?", expanded=False):
        st.markdown("""
        <div style="background-color: #fff9f9; border-radius: 12px; padding: 1rem; border-left: 5px solid #ffe0e6;">
        내가 생각한 의견을 더 잘 표현할 수 있도록 도움을 받는 기능이에요!
        
        <ol>
        <li>토론하고 싶은 주제를 입력해요 (예: 학교 스마트폰 사용)</li>
        <li>그 주제에 대한 내 생각을 자유롭게 적어요</li>
        <li>'피드백 받기' 버튼을 누르면:
           <ul>
           <li>내 의견이 찬성인지 반대인지 알려줘요</li>
           <li>내 생각을 더 탄탄하게 만들 수 있는 조언을 받을 수 있어요</li>
           <li>다른 친구들은 어떻게 생각할지도 생각해볼 수 있어요</li>
           </ul>
        </li>
        </ol>
        
        💡 <strong>도움말</strong>: 솔직하게 내 생각을 쓰면 더 도움이 되는 피드백을 받을 수 있어요!
        </div>
        """, unsafe_allow_html=True)

    # 이전 단계에서 사용한 주제가 있다면 가져오기
    previous_topic = st.session_state.get('argument_topic', "") # .get()으로 안전하게 접근

    # 이전 단계에서 선택한 주제가 있다면 보여주기
    if previous_topic:
        st.info(f"앞에서 '{previous_topic}' 주제에 대해 논거 아이디어를 살펴봤네요! 이 주제로 계속할까요?")

    # 토론 주제 입력 필드 (고유 키 부여) - 이전 주제 자동 완성
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<label style="font-weight: bold; margin-bottom: 0.5rem; display: block;">📌 어떤 주제에 대한 의견인가요?</label>', unsafe_allow_html=True)
    feedback_topic = st.text_input("", 
                             value=previous_topic, # 이전 단계 주제를 기본값으로 설정
                             key="feedback_topic_input",
                             placeholder="토론 주제를 입력해 주세요 (예: 학교 스마트폰 사용, 로봇 반려동물)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 논거/의견 입력 필드 (고유 키 부여, 텍스트 영역으로 충분한 입력 공간 제공)
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<label style="font-weight: bold; margin-bottom: 0.5rem; display: block;">📄 내 의견을 자유롭게 적어보세요:</label>', unsafe_allow_html=True)
    feedback_argument = st.text_area("", key="feedback_argument_input", 
                                height=150,
                                placeholder="이 주제에 대한 나의 생각을 솔직하게 적어보세요. 찬성하는지, 반대하는지, 왜 그렇게 생각하는지 적으면 더 좋아요!")
    st.markdown('</div>', unsafe_allow_html=True)

    # 피드백 버튼
    st.markdown('<div class="button-container-right">', unsafe_allow_html=True)
    if st.button("피드백 받기 ✨", key="feedback_button"):
        if not feedback_topic or not feedback_argument:
            # 필수 입력값이 없을 경우 경고 메시지
            st.warning("토론 주제와 내 의견을 모두 입력해야 피드백을 받을 수 있어요! 🙂")
        else:
            # 로딩 상태 표시하며 API 호출
            with st.spinner("의견을 분석하고 있어요... 금방 피드백을 알려드릴게요! 🔍"):
                # 입력값을 프롬프트에 포맷팅
                prompt = FEEDBACK_PROMPT_TEMPLATE.format(
                    topic_input=feedback_topic,
                    student_argument_input=feedback_argument
                )
                # API 호출하여 응답 받기
                response = get_gemini_response(prompt)
                
                if response:
                    # 응답 결과를 세션 상태에 저장
                    st.session_state.feedback_result = response
                    # 결과를 확장 패널에 표시 (기본 확장 상태)
                    with st.expander("내 의견에 대한 피드백 📋", expanded=True):
                        st.markdown(response)
                        st.balloons()  # 축하 효과 추가
                        st.success("피드백을 받았어요! 이제 이 내용을 바탕으로 의견을 더 발전시켜 보세요. 토론할 때 큰 도움이 될 거예요! 👍")
                else:
                    st.error("피드백을 생성하는데 문제가 생겼어요. 다시 시도해 볼까요?")
    st.markdown('</div>', unsafe_allow_html=True)

    # 예시 의견 보여주기
    with st.expander("의견 작성이 어렵다면? 예시를 참고해 보세요!", expanded=False):
        st.subheader("📱 예시 1: 학교 스마트폰 사용에 대한 의견")
        st.info("""
        저는 학교에서 스마트폰 사용을 제한적으로 허용하는 것이 좋다고 생각해요. 왜냐하면 긴급 상황에 부모님께 연락할 수 있고, 수업 중에 궁금한 것을 바로 찾아볼 수 있기 때문이에요. 하지만 완전히 자유롭게 사용하면 게임이나 SNS에 집중해서 수업에 방해가 될 수 있어요. 그래서 꼭 필요할 때만 선생님 허락을 받고 사용하는 방법이 좋다고 생각해요.
        """)
        
        st.subheader("🤖 예시 2: 로봇 반려동물에 대한 의견")
        st.info("""
        저는 로봇 반려동물보다 진짜 반려동물이 더 좋다고 생각해요. 진짜 반려동물은 정말 나를 좋아하고 감정을 표현할 수 있어요. 로봇은 프로그램대로만 움직이니까 진짜 정이 들기 어려울 것 같아요. 하지만 알레르기가 있거나 돌볼 시간이 부족한 사람들에게는 로봇 반려동물이 좋은 선택일 수 있다고 생각해요.
        """)

# ============================
# 5. 토론 마무리 활동 도구
# ============================
with tab5:
    # 마무리 활동 TIP
    st.header("🤝 토론 마무리하기")
    
    # 토론 마무리 활동 소개 (중앙 정렬)
    st.markdown("<h3 style='text-align:center'>😀 토론 마무리 활동 TIP! 이렇게 해보세요!</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>토론이 끝난 후에 친구들과 함께 할 수 있는, 생각을 정리하고 나누는 활동이에요.</p>", unsafe_allow_html=True)
    
    # 구분선 추가
    st.divider()
    
    # 팁 1
    st.markdown("""
    <div style="display: flex; align-items: flex-start; margin-bottom: 1rem; background-color: #f8f8f8; padding: 1rem; border-radius: 10px;">
        <div style="background-color: #ffcdd2; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 20px; margin-right: 15px;">1</div>
        <div style="flex: 1;">
            <h3 style="margin-top: 0; color: #333333;">📝 요약하기</h3>
            <div style="background-color: #e6f2ff; padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem;">
                <p style="margin: 0; color: #333333;">토론에서 나온 중요한 생각들을 정리해 봐요.</p>
            </div>
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                <li>찬성/반대 입장에서 나온 주요 의견들을 간단히 정리해 봅니다.</li>
                <li>가장 설득력 있었던 의견은 무엇인지 생각해 봅니다.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 구분선 추가
    st.divider()
    
    # 팁 2
    st.markdown("""
    <div style="display: flex; align-items: flex-start; margin-bottom: 1rem; background-color: #f8f8f8; padding: 1rem; border-radius: 10px;">
        <div style="background-color: #ffcdd2; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 20px; margin-right: 15px;">2</div>
        <div style="flex: 1;">
            <h3 style="margin-top: 0; color: #333333;">💭 공감하기</h3>
            <div style="background-color: #e6f2ff; padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem;">
                <p style="margin: 0; color: #333333;">내 생각과 다른 의견에서도 배울 점을 찾아봐요.</p>
            </div>
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                <li>나와 다른 생각을 들었을 때 어떤 느낌이 들었는지 나눠 봅니다.</li>
                <li>다른 친구의 의견 중 '좋은 점'을 찾아 이야기해 봅니다.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 구분선 추가
    st.divider()
    
    # 팁 3
    st.markdown("""
    <div style="display: flex; align-items: flex-start; margin-bottom: 1rem; background-color: #f8f8f8; padding: 1rem; border-radius: 10px;">
        <div style="background-color: #ffcdd2; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 20px; margin-right: 15px;">3</div>
        <div style="flex: 1;">
            <h3 style="margin-top: 0; color: #333333;">❓ 질문하기</h3>
            <div style="background-color: #e6f2ff; padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem;">
                <p style="margin: 0; color: #333333;">"왜 그렇게 생각해요?", "예시를 들어줄래요?"</p>
            </div>
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                <li>더 알고 싶은 내용이 있다면 질문을 통해 대화를 이어갑니다.</li>
                <li>열린 질문을 통해 다양한 생각을 더 깊이 탐색해 봅니다.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 구분선 추가
    st.divider()
    
    # 팁 4
    st.markdown("""
    <div style="display: flex; align-items: flex-start; margin-bottom: 1rem; background-color: #f8f8f8; padding: 1rem; border-radius: 10px;">
        <div style="background-color: #ffcdd2; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 20px; margin-right: 15px;">4</div>
        <div style="flex: 1;">
            <h3 style="margin-top: 0; color: #333333;">🤗 존중하기</h3>
            <div style="background-color: #e6f2ff; padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem;">
                <p style="margin: 0; color: #333333;">다른 의견도 소중해요!</p>
            </div>
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                <li>모든 의견에 감사하는 마음을 표현합니다.</li>
                <li>서로 다른 생각이 있어 더 풍부한 논의가 가능했음을 알아봅니다.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 구분선 추가
    st.divider()
    
    # 팁 5
    st.markdown("""
    <div style="display: flex; align-items: flex-start; margin-bottom: 1rem; background-color: #f8f8f8; padding: 1rem; border-radius: 10px;">
        <div style="background-color: #ffcdd2; color: white; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 20px; margin-right: 15px;">5</div>
        <div style="flex: 1;">
            <h3 style="margin-top: 0; color: #333333;">🌱 마음 열기</h3>
            <div style="background-color: #e6f2ff; padding: 0.5rem; border-radius: 5px; margin-bottom: 0.5rem;">
                <p style="margin: 0; color: #333333;">내 생각이 바뀔 수도 있어요.</p>
            </div>
            <ul style="margin-top: 0.5rem; padding-left: 1.5rem;">
                <li>토론 후 내 생각이 어떻게 변했는지 이야기해 봅니다.</li>
                <li>다른 사람의 의견을 듣고 새롭게 배운 점을 나눠 봅니다.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 구분선 추가
    st.divider()
    
    # 마무리 메시지
    st.success("토론은 정답을 찾는 게 아니라, 여러 생각을 나누는 거예요! 🦉✨")
    
    # 실제 토론 마무리 활동 입력 폼
    st.subheader("💬 토론 마무리 활동")
    st.markdown("토론에서 나온 생각들을 정리하고 새로운 해결책을 찾아보세요.")
    
    # 토론 주제 입력
    st.markdown("#### 📌 토론했던 주제는 무엇인가요?")
    topic = st.text_input("", key="topic_input", placeholder="예: 학교에서 스마트폰 사용 허용 여부")
    
    # 찬성/반대 의견 입력
    st.markdown("#### 📋 토론에서 나온 주요 의견들")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 💙 찬성 측 의견")
        pro_opinion = st.text_area(
            "찬성 측의 주요 의견은 무엇이었나요?",
            key="pro_opinion",
            placeholder="스마트폰으로 수업 정보를 빠르게 찾을 수 있고, 다양한 학습 앱을 활용할 수 있어요.",
            height=120
        )
        
        pro_good_points = st.text_area(
            "찬성 의견에서 가치 있다고 생각하는 점은?",
            key="pro_good_points",
            placeholder="디지털 도구를 활용한 학습 능력 향상, 정보 접근성 증가",
            height=80
        )
    
    with col2:
        st.markdown("##### 💜 반대 측 의견")
        con_opinion = st.text_area(
            "반대 측의 주요 의견은 무엇이었나요?",
            key="con_opinion",
            placeholder="스마트폰이 수업 집중을 방해하고, 게임이나 SNS 중독 위험이 있어요.",
            height=120
        )
        
        con_good_points = st.text_area(
            "반대 의견에서 가치 있다고 생각하는 점은?",
            key="con_good_points",
            placeholder="집중력 유지의 중요성, 디지털 기기 과의존 방지",
            height=80
        )

    # 공통된 해결책 찾기
    st.markdown("#### 🌈 함께 만드는 새로운 해결책")
    new_solution = st.text_area(
        "두 관점의 좋은 점을 모아 새로운 해결책을 만들어 보세요.",
        key="new_solution",
        placeholder="예: 스마트폰은 기본적으로 보관함에 두고, 선생님이 학습 목적으로 필요하다고 판단할 때만 사용하도록 해요. 또한 디지털 시민교육을 통해 올바른 스마트폰 사용법을 배워요.",
        height=120
    )

    # 성찰하기
    st.markdown("#### 🌱 나의 성장 일기")
    reflection = st.text_area(
        "토론을 통해 내 생각이 어떻게 변했나요? 무엇을 새롭게 배웠나요?",
        key="reflection",
        placeholder="처음에는 스마트폰 사용을 무조건 찬성했지만, 집중력 문제도 중요하다는 것을 알게 되었어요. 서로 다른 의견을 듣는 것이 중요하다는 것을 배웠어요.",
        height=120
    )

    # 의견 저장 및 공유 기능
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submitted = st.button("🔖 마무리 활동 정리하기", key="summary_button", use_container_width=True)

    if submitted:
        if topic:
            st.success("토론 마무리 활동 내용이 정리되었어요! 아래 정리된 내용을 확인해보세요.")

            # 마무리 결과 출력
            st.markdown("## 📋 토론 마무리 정리")
            
            st.markdown("### 📌 토론 주제")
            st.info(topic)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💙 찬성 측 의견과 가치")
                st.info(pro_opinion)
                
                st.markdown("**가치 있는 점:**")
                st.info(pro_good_points)
            
            with col2:
                st.markdown("### 💜 반대 측 의견과 가치")
                st.info(con_opinion)
                
                st.markdown("**가치 있는 점:**")
                st.info(con_good_points)
            
            st.markdown("### 🌟 우리가 함께 만든 새로운 해결책")
            st.info(new_solution)
            
            st.markdown("### 🌱 나의 성장과 배움")
            st.info(reflection)
            
            # 결과 다운로드 버튼
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 정리 내용 다운로드",
                    data=f"""토론 주제: {topic}
                    
찬성 측 의견:
{pro_opinion}

찬성 측 가치 있는 점:
{pro_good_points}

반대 측 의견:
{con_opinion}

반대 측 가치 있는 점:
{con_good_points}

함께 만든 해결책:
{new_solution}

나의 성장과 배움:
{reflection}
                    """,
                    file_name="토론마무리_결과.txt",
                    mime="text/plain",
                )
            
        else:
            st.warning("토론 주제를 입력해주세요!")
    
    # 선생님을 위한 도움말
    with st.expander("선생님을 위한 도움말"):
        st.markdown("""
        ### 🔑 API 키 설정 방법
        1. [Google AI Studio](https://aistudio.google.com/)에서 API 키를 발급받으세요.
        2. 발급받은 키를 입력 상자에 넣고 저장하면 됩니다.
        
        ### 📚 수업 활용 Tip
        - 토론 주제는 학생들의 관심사와 연결해 보세요.
        - 찬반 의견을 나눠 역할극처럼 진행해 보세요.
        - 모든 학생이 최소 한 번씩 의견을 말할 수 있도록 해주세요.
        """)

# 푸터 추가
st.markdown("""
<div class="footer">
    <div class="footer-content">
        <span>© 2025 안양 박달초 김문정</span>
        <span class="footer-heart">❤️</span>
        <a href="https://www.youtube.com/@%EB%B0%B0%EC%9B%80%EC%9D%98%EB%8B%AC%EC%9D%B8-p5v/videos" target="_blank">유튜브 배움의 달인</a>
    </div>
</div>
""", unsafe_allow_html=True)
