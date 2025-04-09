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
        padding: 0.5rem;
        border-radius: 50px;
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border-radius: 50px !important;
        padding: 0.5rem 1rem !important;
        font-family: 'Jua', sans-serif;
        color: #66545e !important;
        font-size: 1rem;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #ffb7c5 !important;
        color: white !important;
        box-shadow: 0 2px 4px rgba(255, 183, 197, 0.3);
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
    
    /* 주제 추천 결과 컨테이너 스타일 수정 */
    .recommendation-result {
        background-color: white;
        border-radius: 12px;
        padding: 1rem;
        max-height: 300px;
        overflow-y: auto;
        margin-top: 1rem;
        margin-bottom: 1rem;
        border: 2px solid #ffb7c5;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
    st.markdown('<h2 style="text-align: center; margin-top: 0;">토론부기-지혜로운 토론 친구</h2>', unsafe_allow_html=True)
    
    # 앱 사용법
    st.markdown("## 앱 사용법")
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
    st.markdown("""
    <div class="tip-item">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #ffb7c5; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; justify-content: center; align-items: center; margin-right: 10px; font-weight: bold;">1</div>
            <h3 style="margin: 0; color: #66545e; font-weight: bold;">경청하기</h3>
        </div>
        <p style="margin-left: 38px; margin-top: 5px;">부엉이는 귀가 좋아서 잘 들어요. 친구들 말도 집중해서 들어보세요.</p>
    </div>
    <div style="border-bottom: 1px dashed #ffd1dc; margin: 10px 0;"></div>
    """, unsafe_allow_html=True)
    
    # 팁 2
    st.markdown("""
    <div class="tip-item">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #ffd1dc; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; justify-content: center; align-items: center; margin-right: 10px; font-weight: bold;">2</div>
            <h3 style="margin: 0; color: #66545e; font-weight: bold;">근거 말하기</h3>
        </div>
        <p style="margin-left: 38px; margin-top: 5px;">"왜냐하면~", "예를 들면~"으로 이유를 설명하세요.</p>
    </div>
    <div style="border-bottom: 1px dashed #ffd1dc; margin: 10px 0;"></div>
    """, unsafe_allow_html=True)
    
    # 팁 3
    st.markdown("""
    <div class="tip-item">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #ffe0e6; color: #66545e; border-radius: 50%; width: 28px; height: 28px; display: flex; justify-content: center; align-items: center; margin-right: 10px; font-weight: bold;">3</div>
            <h3 style="margin: 0; color: #66545e; font-weight: bold;">질문하기</h3>
        </div>
        <p style="margin-left: 38px; margin-top: 5px;">"왜 그렇게 생각해요?", "예시를 들어줄래요?"</p>
    </div>
    <div style="border-bottom: 1px dashed #ffd1dc; margin: 10px 0;"></div>
    """, unsafe_allow_html=True)
    
    # 팁 4
    st.markdown("""
    <div class="tip-item">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #fff0f5; color: #66545e; border-radius: 50%; width: 28px; height: 28px; display: flex; justify-content: center; align-items: center; margin-right: 10px; font-weight: bold;">4</div>
            <h3 style="margin: 0; color: #66545e; font-weight: bold;">존중하기</h3>
        </div>
        <p style="margin-left: 38px; margin-top: 5px;">다른 의견도 소중해요!</p>
    </div>
    <div style="border-bottom: 1px dashed #ffd1dc; margin: 10px 0;"></div>
    """, unsafe_allow_html=True)
    
    # 팁 5
    st.markdown("""
    <div class="tip-item">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #fff5f8; color: #66545e; border-radius: 50%; width: 28px; height: 28px; display: flex; justify-content: center; align-items: center; margin-right: 10px; font-weight: bold;">5</div>
            <h3 style="margin: 0; color: #66545e; font-weight: bold;">마음 열기</h3>
        </div>
        <p style="margin-left: 38px; margin-top: 5px;">내 생각이 바뀔 수도 있어요.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 마무리 메시지
    st.markdown("""
    <div style="background-color: #fff5f2; padding: 10px; border-radius: 5px; margin-top: 15px; text-align: center;">
        <p style="margin: 0; font-style: italic; color: #66545e;">토론은 정답을 찾는 게 아니라, 여러 생각을 나누는 거예요! 🦉✨</p>
    </div>
    """, unsafe_allow_html=True)
    
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

# 앱 타이틀 및 설명
st.markdown('<div style="text-align: center; margin-bottom: 2rem;">', unsafe_allow_html=True)
st.markdown('<div class="big-emoji">🦉</div>', unsafe_allow_html=True)
st.title("토론부기 - 지혜로운 토론 친구")
st.markdown('<div class="subtitle">AI활용 경기 토론 수업 모형 지원 도구</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 기능 설명을 카드 형태로 표시
st.markdown("""
<div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
    <div style="flex: 1; min-width: 200px; background-color: white; padding: 1rem; border-radius: 12px; border-left: 5px solid #ffb7c5; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <h3 style="margin-top:0; color: #66545e;">📚 경기 토론 수업 모형</h3>
        <p style="margin-bottom:0; color: #66545e;">토론을 어떻게 하면 좋을지 3단계로 쉽게 알려줘요.</p>
    </div>
    
    <div style="flex: 1; min-width: 200px; background-color: white; padding: 1rem; border-radius: 12px; border-left: 5px solid #ffd1dc; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <h3 style="margin-top:0; color: #66545e;">🔍 토론 주제 추천</h3>
        <p style="margin-bottom:0; color: #66545e;">관심 있는 것을 입력하면 재미있는 토론 주제를 추천해 줄게요!</p>
    </div>
    
    <div style="flex: 1; min-width: 200px; background-color: white; padding: 1rem; border-radius: 12px; border-left: 5px solid #ffe0e6; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <h3 style="margin-top:0; color: #66545e;">💡 찬반 논거 아이디어</h3>
        <p style="margin-bottom:0; color: #66545e;">어떤 주제든 '찬성' 의견과 '반대' 의견을 모두 알려줘요.</p>
    </div>
    
    <div style="flex: 1; min-width: 200px; background-color: white; padding: 1rem; border-radius: 12px; border-left: 5px solid #fff0f5; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <h3 style="margin-top:0; color: #66545e;">📝 의견 피드백 받기</h3>
        <p style="margin-bottom:0; color: #66545e;">의견에 대한 조언을 받고, 함께 새로운 해결책을 만들어요.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 안내 메시지
st.markdown("""
<div style="background: linear-gradient(135deg, #f0f8ff 0%, #e6f7ff 100%); padding: 1rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; border-left: 5px solid #a5d8ff;">
    <p style="font-weight:bold; font-size:1.2rem; margin:0; color: #66545e;">아래 탭을 선택하여 각 기능을 사용해보세요! ✨</p>
</div>
""", unsafe_allow_html=True)

# 탭 메뉴로 기능 분리
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📚 경기 토론 수업 모형", 
    "🔍 토론 주제 추천", 
    "💡 찬반 논거 아이디어", 
    "📝 의견 피드백 받기",
    "🤝 토론 마무리하기"
])

# ============================
# 1. 경기 토론 수업 모형 안내 기능
# ============================
with tab1:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.header("📚 경기 토론 수업 모형 알아보기")

    # 경기 토론 수업 모형 설명 
    st.markdown("""
    <div style="text-align:center; margin-bottom:20px;">
        <h2 style="color:#66545e; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); background:none; box-shadow:none;">
            😀 경기 토론 수업 모형은 이렇게 진행해요!
        </h2>
        <p style="font-size:1.2rem;">친구들과 함께 토론할 때 어떻게 하면 좋을지 알려주는 방법이에요.<br>
        세 가지 단계로 이루어져 있답니다!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 1단계 설명 - 카드 형태로 시각적 표현
    st.markdown("""
    <div style="background-color: #fff5f2; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border-left: 5px solid #ffb7c5;">
        <h3 style="color:#66545e; margin-top:0; border-bottom: 2px dashed #ffb7c5; padding-bottom: 0.5rem;">1️⃣ 다름과 마주하기</h3>
        <p>다양한 생각이 있다는 것을 알아보는 단계예요.</p>
        <ul>
            <li>토론 주제에 대해 처음 생각해보기</li>
            <li>친구들은 어떻게 생각하는지 듣기</li>
            <li>주제가 왜 중요한지 이해하기</li>
        </ul>
        <p><b>예시:</b> "학교에서 스마트폰을 사용하는 것"에 대해 찬성하는 친구도 있고, 반대하는 친구도 있다는 것을 알게 됩니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2단계 설명
    st.markdown("""
    <div style="background-color: #ffeef2; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border-left: 5px solid #ffd1dc;">
        <h3 style="color:#66545e; margin-top:0; border-bottom: 2px dashed #ffd1dc; padding-bottom: 0.5rem;">2️⃣ 다름을 이해하기</h3>
        <p>서로 다른 생각을 더 깊이 이해하는 단계예요.</p>
        <ul>
            <li>내 의견을 논리적으로 설명하기</li>
            <li>친구들의 의견이 왜 그런지 이해하기</li>
            <li>질문하고 답변하며 생각 나누기</li>
        </ul>
        <p><b>예시:</b> "스마트폰으로 수업 정보를 찾을 수 있어요"라는 의견과 "스마트폰이 수업에 집중하는 것을 방해해요"라는 의견이 왜 나오는지 서로 이야기해봅니다.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3단계 설명
    st.markdown("""
    <div style="background-color: #fff9f9; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border-left: 5px solid #ffe0e6;">
        <h3 style="color:#66545e; margin-top:0; border-bottom: 2px dashed #ffe0e6; padding-bottom: 0.5rem;">3️⃣ 다름과 공존하기</h3>
        <p>서로 다른 의견이 모두 소중하다는 것을 알고 함께 좋은 방법을 찾는 단계예요.</p>
        <ul>
            <li>서로의 의견을 존중하기</li>
            <li>좋은 점들을 모아 새로운 해결책 생각하기</li>
            <li>함께 성장하기</li>
        </ul>
        <p><b>예시:</b> "스마트폰은 수업 시간에는 꺼두고, 조사 활동이 필요할 때만 선생님 허락을 받고 사용하자"와 같이 모두가 만족할 수 있는 방법을 찾습니다.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: linear-gradient(135deg, #f0f8ff 0%, #e6f7ff 100%); border-radius: 12px; padding: 1.5rem; border-left: 5px solid #a5d8ff;">
        <h3 style="margin-top:0; color: #66545e;">👉 이 도구는 위 세 단계 모두 도움을 줄 수 있어요!</h3>
        <ul>
            <li>토론 주제 추천은 <span class="rainbow-text">'다름과 마주하기'</span>를 도와줘요</li>
            <li>찬반 논거 아이디어는 <span class="rainbow-text">'다름을 이해하기'</span>를 도와줘요</li> 
            <li>피드백 받기와 마무리 활동은 <span class="rainbow-text">'다름과 공존하기'</span>를 연습하는데 도움이 돼요</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
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
    col1, col2 = st.columns([3, 1])
    with col1:
        topic_interest = st.text_input("", 
                                   key="topic_interest_input", 
                                   placeholder="관심 있는 주제를 입력해 보세요!")
    with col2:
        # 버튼 클릭 시 처리 (고유 키 부여)
        if st.button("주제 추천 받기 🚀", key="topic_recommend_button"):
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
                        # 결과를 고정 크기 컨테이너에 표시
                        st.markdown(f"""
                        <div style="margin-top:15px;">
                            <h3 style="color: #66545e; border-bottom: 2px dashed #ffb7c5; padding-bottom: 0.5rem;">'{topic_interest}'에 관한 토론 주제 추천 📋</h3>
                        </div>
                        <div class="recommendation-result">
                            {response}
                        </div>
                        """, unsafe_allow_html=True)
                        st.success("이 주제들 중에 마음에 드는 것이 있다면, '찬반 논거 아이디어 보기' 탭을 선택해 보세요! 👇")
                    else:
                        st.error("앗! 주제를 찾는데 문제가 생겼어요. 다른 관심사를 입력해 볼까요?")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
                for i, topic_title in enumerate(recommended_topics):
                    # 각 주제에 대한 버튼 생성
                    button_key = f"use_topic_{i}"
                    if st.button(f"➡️ '{topic_title}' 사용하기", key=button_key):
                        # 버튼 클릭 시 해당 주제를 세션 상태에 저장하고 입력 필드 업데이트 준비
                        st.session_state.selected_topic_for_tab3 = topic_title
                        # Streamlit이 재실행되면서 아래 text_input의 value가 업데이트됨
                        st.rerun() # 입력 필드 값을 즉시 업데이트하기 위해 rerun

    # 토론 주제 입력 필드 (고유 키 부여) - 버튼 클릭 시 업데이트됨
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<label style="font-weight: bold; margin-bottom: 0.5rem; display: block;">어떤 주제에 대한 논거 아이디어가 필요하니?</label>', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        # 버튼 클릭으로 선택된 주제가 있으면 해당 주제를 기본값으로 사용
        argument_topic_value = st.session_state.selected_topic_for_tab3 if st.session_state.selected_topic_for_tab3 else ""
        argument_topic = st.text_input("",
                                value=argument_topic_value, # 선택된 주제를 값으로 설정
                                key="argument_topic_input",
                                placeholder="토론하고 싶은 주제를 입력하거나 위에서 선택하세요!")
    with col2:
        # 버튼 클릭 시 처리 (고유 키 부여)
        if st.button("논거 아이디어 보기 💭", key="argument_idea_button"):
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
                        
                        # 결과를 고정 크기 컨테이너에 표시
                        st.markdown(f"""
                        <div style="margin-top:15px;">
                            <h3 style="color: #66545e; border-bottom: 2px dashed #ffb7c5; padding-bottom: 0.5rem;">'{current_argument_topic}'에 대한 찬반 논거 아이디어 ⚖️</h3>
                        </div>
                        <div class="recommendation-result">
                            {response}
                        </div>
                        """, unsafe_allow_html=True)
                        st.success("이제 이 아이디어들을 바탕으로 나만의 의견을 만들어 보세요! '의견 피드백 받기' 탭으로 이동해 의견을 확인받을 수 있어요 👇")
                    else:
                        st.error("아이디어를 찾는데 문제가 생겼어요. 다른 주제로 시도해볼까요?")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown('<label style="font-weight: bold; margin-bottom: 0.5rem; display: block;">어떤 주제에 대한 의견인가요?</label>', unsafe_allow_html=True)
    feedback_topic = st.text_input("", 
                             value=previous_topic, # 이전 단계 주제를 기본값으로 설정
                             key="feedback_topic_input",
                             placeholder="토론 주제를 입력해 주세요 (예: 학교 스마트폰 사용, 로봇 반려동물)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 논거/의견 입력 필드 (고유 키 부여, 텍스트 영역으로 충분한 입력 공간 제공)
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<label style="font-weight: bold; margin-bottom: 0.5rem; display: block;">내 의견을 자유롭게 적어보세요:</label>', unsafe_allow_html=True)
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
        st.markdown("""
        <div style="background-color: #fff5f2; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border-left: 5px solid #ffb7c5;">
        <h3 style="margin-top:0; color: #66545e;">예시 1: 학교 스마트폰 사용에 대한 의견</h3>
        
        <blockquote style="background-color: white; padding: 1rem; border-radius: 8px; border-left: 3px solid #ffb7c5;">
        저는 학교에서 스마트폰 사용을 제한적으로 허용하는 것이 좋다고 생각해요. 왜냐하면 긴급 상황에 부모님께 연락할 수 있고, 수업 중에 궁금한 것을 바로 찾아볼 수 있기 때문이에요. 하지만 완전히 자유롭게 사용하면 게임이나 SNS에 집중해서 수업에 방해가 될 수 있어요. 그래서 꼭 필요할 때만 선생님 허락을 받고 사용하는 방법이 좋다고 생각해요.
        </blockquote>
        </div>
        
        <div style="background-color: #ffeef2; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border-left: 5px solid #ffd1dc;">
        <h3 style="margin-top:0; color: #66545e;">예시 2: 로봇 반려동물에 대한 의견</h3>
        
        <blockquote style="background-color: white; padding: 1rem; border-radius: 8px; border-left: 3px solid #ffd1dc;">
        저는 로봇 반려동물보다 진짜 반려동물이 더 좋다고 생각해요. 진짜 반려동물은 정말 나를 좋아하고 감정을 표현할 수 있어요. 로봇은 프로그램대로만 움직이니까 진짜 정이 들기 어려울 것 같아요. 하지만 알레르기가 있거나 돌볼 시간이 부족한 사람들에게는 로봇 반려동물이 좋은 선택일 수 있다고 생각해요.
        </blockquote>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================
# 5. 토론 마무리 활동 도구
# ============================
with tab5:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.header("🤝 토론 마무리하기")

    # 토론 마무리 설명
    with st.expander("토론 마무리 활동이란?", expanded=True):
        st.markdown("""
        <div style="background-color: #fff9f9; padding: 1.5rem; border-radius: 12px; border-left: 5px solid #ffe0e6;">
        <h2 style="color: #66545e; margin-top:0; border-bottom: 2px dashed #ffe0e6; padding-bottom: 0.5rem;">함께 생각 모으기</h2>
        
        <p>토론은 '이기는 것'이 아니라 '함께 더 나은 생각을 찾는 것'이 목표예요.<br>
        토론 마무리 활동을 통해 서로 다른 생각에서 좋은 점을 찾고,<br>
        새로운 해결책을 함께 만들어 봐요!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 마무리 활동 가이드
        st.markdown("""
        <div style="background-color: #fff5f2; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; border-left: 5px solid #ffb7c5;">
            <h3 style="color:#66545e; margin-top:0; border-bottom: 2px dashed #ffb7c5; padding-bottom: 0.5rem;">🧩 마무리 활동 방법</h3>
            <ol>
                <li>토론 주제와 주요 찬성/반대 의견을 입력하세요</li>
                <li>각 의견에서 가장 가치 있다고 생각하는 점을 적어보세요</li>
                <li>두 관점을 모두 고려한 새로운 해결책을 함께 만들어보세요</li>
                <li>토론을 통해 내 생각이 어떻게 변했는지 성찰해보세요</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    # 토론 주제 입력
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    st.markdown('<label style="font-weight: bold; margin-bottom: 0.5rem; display: block;">토론했던 주제는 무엇인가요?</label>', unsafe_allow_html=True)
    topic = st.text_input("", 
                      key="topic_input",
                      placeholder="예: 학교에서 스마트폰 사용 허용 여부")
    st.markdown('</div>', unsafe_allow_html=True)

    # 두 칼럼으로 나누기
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div style="background-color: #ffeef2; border-radius: 12px; padding: 1rem; height: 100%;">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#66545e; margin-top:0; border-bottom: 2px dashed #ffd1dc; padding-bottom: 0.5rem;'>💙 찬성 측 의견</h3>", unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="background-color: #fff5f2; border-radius: 12px; padding: 1rem; height: 100%;">', unsafe_allow_html=True)
        st.markdown("<h3 style='color:#66545e; margin-top:0; border-bottom: 2px dashed #ffb7c5; padding-bottom: 0.5rem;'>💜 반대 측 의견</h3>", unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

    # 공통된 해결책 찾기
    st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#66545e; margin-top:0; border-bottom: 2px dashed #ffb7c5; padding-bottom: 0.5rem;'>🌈 함께 만드는 새로운 해결책</h3>", unsafe_allow_html=True)
    new_solution = st.text_area(
        "두 관점의 좋은 점을 모아 새로운 해결책을 만들어 보세요.",
        key="new_solution",
        placeholder="예: 스마트폰은 기본적으로 보관함에 두고, 선생님이 학습 목적으로 필요하다고 판단할 때만 사용하도록 해요. 또한 디지털 시민교육을 통해 올바른 스마트폰 사용법을 배워요.",
        height=120
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 성찰하기
    st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
    st.markdown("<h3 style='color:#66545e; margin-top:0; border-bottom: 2px dashed #ffe0e6; padding-bottom: 0.5rem;'>🌱 나의 성장 일기</h3>", unsafe_allow_html=True)
    reflection = st.text_area(
        "토론을 통해 내 생각이 어떻게 변했나요? 무엇을 새롭게 배웠나요?",
        key="reflection",
        placeholder="처음에는 스마트폰 사용을 무조건 찬성했지만, 집중력 문제도 중요하다는 것을 알게 되었어요. 서로 다른 의견을 듣는 것이 중요하다는 것을 배웠어요.",
        height=120
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 의견 저장 및 공유 기능
    st.markdown('<div class="button-container-center" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
    submitted = st.button("🔖 마무리 활동 정리하기", key="summary_button")
    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if topic:
            st.success("토론 마무리 활동 내용이 정리되었어요! 아래 정리된 내용을 확인해보세요.")
            
            # 마무리 결과 출력
            st.markdown("""
            <div style="background-color: white; border-radius: 12px; padding: 1.5rem; margin-top: 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); border: 2px solid #ffe0e6;">
            <h2 style="color:#66545e; text-align:center; margin-bottom: 1.5rem;">📋 토론 마무리 정리</h2>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background-color: #fff9f9; border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem; border-left: 5px solid #ffe0e6;">
            <h3 style="margin-top:0; color: #66545e;">주제</h3>
            <p style="font-size: 1.2rem; color: #66545e;">{topic}</p>
            </div>
            
            <div style="display: flex; gap: 20px; margin-top: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 250px;">
                <div style="background-color: #ffeef2; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border-left: 5px solid #ffd1dc;">
                <h3 style="margin-top:0; color: #66545e;">💙 찬성 측 의견과 가치</h3>
                <p style="color: #66545e;">{pro_opinion}</p>
                
                <p style="color: #66545e;"><strong>가치 있는 점</strong>:</p>
                <p style="color: #66545e;">{pro_good_points}</p>
                </div>
            </div>
            
            <div style="flex: 1; min-width: 250px;">
                <div style="background-color: #fff5f2; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border-left: 5px solid #ffb7c5;">
                <h3 style="margin-top:0; color: #66545e;">💜 반대 측 의견과 가치</h3>
                <p style="color: #66545e;">{con_opinion}</p>
                
                <p style="color: #66545e;"><strong>가치 있는 점</strong>:</p>
                <p style="color: #66545e;">{con_good_points}</p>
                </div>
            </div>
            </div>
            
            <div style="background-color: #fff0f5; border-radius: 12px; padding: 1rem; margin-top: 1.5rem; margin-bottom: 1.5rem; border-left: 5px solid #ffb7c5;">
            <h3 style="margin-top:0; color: #66545e;">🌟 우리가 함께 만든 새로운 해결책</h3>
            <p style="color: #66545e;">{new_solution}</p>
            </div>
            
            <div style="background-color: #fff9f9; border-radius: 12px; padding: 1rem; margin-top: 1.5rem; border-left: 5px solid #ffe0e6;">
            <h3 style="margin-top:0; color: #66545e;">🌱 나의 성장과 배움</h3>
            <p style="color: #66545e;">{reflection}</p>
            </div>
            
            <div style="text-align: center; margin-top: 1.5rem; padding: 1rem; font-style: italic; color: #66545e; background-color: #fff5f2; border-radius: 12px;">
            <p style="margin: 0;">다름을 존중하고 이해하며 함께 성장해요! - 토론부기</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 결과 공유 옵션
            st.markdown('<div class="button-container-center" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
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
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:
            st.warning("토론 주제를 입력해주세요!")

    # 토론 마무리 활동 TIP 제공
    with st.expander("토론부기의 마무리 활동 TIP"):
        st.markdown("""
        <div style="background-color: #fff5f2; border-radius: 12px; padding: 1rem; border-left: 5px solid #ffb7c5;">
        <h3 style="margin-top:0; color: #66545e;">🦉 토론부기의 마무리 활동 꿀팁</h3>

        <ol>
            <li><strong>비판이 아닌 가치 찾기</strong>: 상대 의견의 단점보다 가치 있는 점을 먼저 찾아봐요.</li>
            
            <li><strong>모두의 참여</strong>: 해결책을 만들 때 모든 친구의 의견을 조금씩 반영해봐요.</li>
            
            <li><strong>감정 표현하기</strong>: "나는 ~라고 생각해" 형식으로 자기 감정을 솔직하게 표현해요.</li>
            
            <li><strong>열린 마음</strong>: 처음과 다른 생각을 하게 되었다면, 그것도 아주 훌륭한 성장이에요!</li>
            
            <li><strong>기록하기</strong>: 토론 전후의 내 생각 변화를 기록해두면 나중에 보았을 때 내가 얼마나 성장했는지 알 수 있어요.</li>
        </ol>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 푸터 추가
footer_html = """
<div style="position: relative; bottom: 0; width: 100%; text-align: center; padding: 10px; margin-top: 2rem; background-color: #fff5f2; border-radius: 12px;">
    <p style="margin: 0; font-size: 12px; color: #66545e;">
        © 2025 안양 박달초 김문정 | ❤️ <a href="https://www.youtube.com/@%EB%B0%B0%EC%9B%80%EC%9D%98%EB%8B%AC%EC%9D%B8-p5v/videos" target="_blank" style="color: #66545e; text-decoration: underline;">유튜브 배움의 달인</a>
    </p>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)