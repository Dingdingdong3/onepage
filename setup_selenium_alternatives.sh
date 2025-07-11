#!/bin/bash

# 전기차 보조금 크롤링 - Selenium 대안 라이브러리 설치 스크립트
# Anaconda 환경에서 requests-html, Playwright, Pyppeteer 설치

echo "🚗 전기차 보조금 크롤링 - Selenium 대안 설치 시작"
echo "=" * 60

# Anaconda 환경 활성화
echo "🐍 Anaconda 환경 확인 중..."
if [ ! -d "/opt/anaconda3" ]; then
    echo "❌ /opt/anaconda3 경로를 찾을 수 없습니다."
    exit 1
fi

source /opt/anaconda3/bin/activate

# 환경 선택
read -p "새 conda 환경을 생성하시겠습니까? (y/n): " create_env
if [ "$create_env" = "y" ] || [ "$create_env" = "Y" ]; then
    echo "🔨 새 환경 'ev_scraper' 생성 중..."
    conda create -n ev_scraper python=3.9 -y
    conda activate ev_scraper
    echo "✅ 환경 생성 완료"
else
    echo "📦 base 환경 사용"
fi

# 기본 라이브러리 설치
echo "📚 기본 라이브러리 설치 중..."
conda install -c conda-forge requests beautifulsoup4 pandas -y

echo ""
echo "🔧 Selenium 대안 라이브러리 설치 옵션:"
echo "1. requests-html (가장 간단, 권장)"
echo "2. Playwright (현대적, 빠름)"
echo "3. Pyppeteer (Python Puppeteer 포트)"
echo "4. 모두 설치"
echo ""

read -p "선택하세요 (1-4): " choice

case $choice in
    1)
        echo "🌐 requests-html 설치 중..."
        pip install requests-html
        echo "✅ requests-html 설치 완료"
        INSTALLED_LIBS="requests-html"
        ;;
    2)
        echo "🎭 Playwright 설치 중..."
        pip install playwright
        echo "🔽 Playwright 브라우저 다운로드 중..."
        playwright install chromium
        echo "✅ Playwright 설치 완료"
        INSTALLED_LIBS="playwright"
        ;;
    3)
        echo "🐍 Pyppeteer 설치 중..."
        pip install pyppeteer
        echo "✅ Pyppeteer 설치 완료"
        INSTALLED_LIBS="pyppeteer"
        ;;
    4)
        echo "📦 모든 라이브러리 설치 중..."

        echo "🌐 requests-html 설치 중..."
        pip install requests-html

        echo "🎭 Playwright 설치 중..."
        pip install playwright
        playwright install chromium

        echo "🐍 Pyppeteer 설치 중..."
        pip install pyppeteer

        echo "✅ 모든 라이브러리 설치 완료"
        INSTALLED_LIBS="requests-html, playwright, pyppeteer"
        ;;
    *)
        echo "❌ 잘못된 선택입니다."
        exit 1
        ;;
esac

# 설치 확인
echo ""
echo "🔍 설치 확인 중..."

# Python 테스트 스크립트
cat > test_installation.py << 'EOF'
import sys

def test_library(lib_name, import_statement):
    try:
        exec(import_statement)
        print(f"✅ {lib_name}: 설치됨")
        return True
    except ImportError as e:
        print(f"❌ {lib_name}: 미설치 - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {lib_name}: 설치되었지만 오류 - {e}")
        return True

print("📋 라이브러리 설치 상태:")
print("-" * 40)

# 기본 라이브러리 확인
test_library("requests", "import requests")
test_library("BeautifulSoup4", "from bs4 import BeautifulSoup")
test_library("pandas", "import pandas as pd")

# Selenium 대안 라이브러리 확인
test_library("requests-html", "from requests_html import HTMLSession")
test_library("Playwright", "from playwright.sync_api import sync_playwright")
test_library("Pyppeteer", "import pyppeteer")

print("-" * 40)
print(f"Python 경로: {sys.executable}")
EOF

python test_installation.py
rm test_installation.py

# 환경 정보 저장
if [ "$create_env" = "y" ] || [ "$create_env" = "Y" ]; then
    ENV_NAME="ev_scraper"
    PYTHON_PATH="/opt/anaconda3/envs/ev_scraper/bin/python"
else
    ENV_NAME="base"
    PYTHON_PATH="/opt/anaconda3/bin/python"
fi

cat > environment_info.txt << EOF
=== 전기차 보조금 크롤러 환경 정보 ===
설치 날짜: $(date)
환경명: $ENV_NAME
Python 경로: $PYTHON_PATH
설치된 라이브러리: $INSTALLED_LIBS

=== 환경 활성화 명령어 ===
source /opt/anaconda3/bin/activate
conda activate $ENV_NAME

=== 실행 명령어 ===
$PYTHON_PATH ev_crawler.py

=== 각 방법별 특징 ===
1. requests (기본):
   - 가장 빠름
   - JavaScript 미지원
   - 정적 콘텐츠만 가능

2. requests-html:
   - 간단한 설정
   - JavaScript 지원
   - Selenium보다 가벼움
   - 중간 정도 속도

3. Playwright:
   - 매우 빠름
   - 현대적 API
   - 강력한 JavaScript 지원
   - Microsoft 개발/지원

4. Pyppeteer:
   - 비동기 처리
   - Puppeteer의 Python 포트
   - 복잡한 상호작용 가능

=== 사용 예시 ===
# 자동 방법 선택 (권장)
manager = EVSubsidyManager(method='auto')

# 특정 방법 지정
manager = EVSubsidyManager(method='requests-html')
manager = EVSubsidyManager(method='playwright')
manager = EVSubsidyManager(method='pyppeteer')
manager = EVSubsidyManager(method='requests')
EOF

echo ""
echo "✅ 설치 완료!"
echo "📋 환경 정보가 environment_info.txt에 저장되었습니다."
echo ""
echo "🚀 사용법:"
echo "1. 환경 활성화: source /opt/anaconda3/bin/activate && conda activate $ENV_NAME"
echo "2. 크롤러 실행: python ev_crawler.py"
echo ""
echo "💡 팁:"
echo "- 자동 방법 선택을 사용하면 설치된 라이브러리 중 최적의 방법을 선택합니다"
echo "- requests-html은 가장 간단하고 안정적입니다"
echo "- Playwright는 가장 현대적이고 빠릅니다"
echo "- 문제 발생시 requests 방법으로 fallback됩니다"