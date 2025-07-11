#!/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
전기차 보조금 크롤링 시스템 (Selenium 대안 버전)
requests-html, Playwright, Pyppeteer 등 다양한 방법 지원
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from datetime import datetime
import hashlib
import time
import asyncio
import sys

# Google Sheets 관련 imports (선택적)
try:
    import gspread
    from google.oauth2.service_account import Credentials

    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False
    print("⚠️  구글 시트 기능을 사용하려면 설치하세요: /opt/anaconda3/bin/pip install gspread google-auth")

# 선택적 imports (설치된 라이브러리에 따라)
try:
    from requests_html import HTMLSession, AsyncHTMLSession

    REQUESTS_HTML_AVAILABLE = True
except ImportError:
    REQUESTS_HTML_AVAILABLE = False
    print("⚠️  requests-html이 설치되지 않음. pip install requests-html")

try:
    from playwright.sync_api import sync_playwright
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  playwright가 설치되지 않음. pip install playwright && playwright install")

try:
    import pyppeteer

    PYPPETEER_AVAILABLE = True
except ImportError:
    PYPPETEER_AVAILABLE = False
    print("⚠️  pyppeteer가 설치되지 않음. pip install pyppeteer")


class GoogleSheetsManager:
    """구글 스프레드시트 관리 클래스"""

    def __init__(self, credentials_file, spreadsheet_id):
        if not GOOGLE_SHEETS_AVAILABLE:
            raise ImportError("구글 시트 라이브러리가 설치되지 않음. /opt/anaconda3/bin/pip install gspread google-auth")

        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        try:
            self.credentials = Credentials.from_service_account_file(
                credentials_file,
                scopes=self.scope
            )
            self.gc = gspread.authorize(self.credentials)
            self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            print(f"✅ 구글 시트 연결 성공: {self.spreadsheet.title}")
        except Exception as e:
            print(f"❌ 구글 시트 연결 실패: {e}")
            raise

    def upload_national_subsidy(self, df):
        """국고 보조금 데이터 업로드"""
        try:
            print(f"📊 국고보조금 데이터 업로드 시작: {len(df)}개 항목")
            print(f"🔍 DataFrame 정보: 컬럼={list(df.columns)}, 타입={type(df)}")

            # '국고보조금' 시트 가져오기 또는 생성
            try:
                worksheet = self.spreadsheet.worksheet('국고보조금')
                print("✅ 기존 '국고보조금' 시트 발견")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title='국고보조금', rows=1000, cols=10)
                print("✅ 새 '국고보조금' 시트 생성")

            # 기존 데이터 지우기
            worksheet.clear()
            print("🧹 기존 데이터 삭제 완료")

            # 헤더와 데이터 준비
            headers = list(df.columns)
            print(f"📋 헤더: {headers}")

            # DataFrame을 리스트로 변환
            data_list = df.values.tolist()
            print(f"📊 데이터 {len(data_list)}개 행 준비 완료")
            if data_list:
                print(f"🔍 첫 번째 데이터 샘플: {data_list[0]}")
                print(f"🔍 데이터 타입 확인: {[type(item) for item in data_list[0]]}")

            # 업데이트 시간 추가
            update_time = f"업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # 헤더 입력
            try:
                worksheet.update(values=[headers], range_name='A1:D1')
                print("✅ 헤더 입력 완료")
            except Exception as e:
                print(f"❌ 헤더 입력 실패: {e}")
                # 대안 방법 시도
                worksheet.update(range_name='A1:D1', values=[headers])
                print("✅ 헤더 입력 완료 (대안 방법)")

            # 데이터 입력
            if data_list:
                # 데이터 범위 계산
                end_row = len(data_list) + 1
                range_notation = f'A2:D{end_row}'
                print(f"📍 데이터 입력 범위: {range_notation}")

                try:
                    worksheet.update(values=data_list, range_name=range_notation)
                    print("✅ 데이터 입력 완료")
                except Exception as e:
                    print(f"❌ 데이터 입력 실패: {e}")
                    # 대안 방법 시도
                    worksheet.update(range_name=range_notation, values=data_list)
                    print("✅ 데이터 입력 완료 (대안 방법)")
            else:
                print("⚠️ 입력할 데이터가 없습니다")

            # 업데이트 시간 입력
            try:
                worksheet.update(values=[[update_time]], range_name='F1')
                print("✅ 업데이트 시간 입력 완료")
            except Exception as e:
                print(f"⚠️ 업데이트 시간 입력 실패: {e}")

            # 헤더 서식 설정
            try:
                worksheet.format('A1:D1', {
                    "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 1.0},
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
                })
                print("✅ 헤더 서식 설정 완료")
            except Exception as e:
                print(f"⚠️ 헤더 서식 설정 실패: {e}")

            print(f"📊 구글 시트 국고보조금 {len(df)}개 업로드 완료")

        except Exception as e:
            print(f"❌ 구글 시트 국고보조금 업로드 실패: {e}")
            import traceback
            traceback.print_exc()

    def upload_local_subsidy(self, df):
        """지자체 보조금 데이터 업로드"""
        try:
            print(f"🏢 지자체보조금 데이터 업로드 시작: {len(df)}개 항목")
            print(f"🔍 DataFrame 정보: 컬럼={list(df.columns)}, 타입={type(df)}")

            # '지자체보조금' 시트 가져오기 또는 생성
            try:
                worksheet = self.spreadsheet.worksheet('지자체보조금')
                print("✅ 기존 '지자체보조금' 시트 발견")
            except gspread.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(title='지자체보조금', rows=1000, cols=10)
                print("✅ 새 '지자체보조금' 시트 생성")

            # 기존 데이터 지우기
            worksheet.clear()
            print("🧹 기존 데이터 삭제 완료")

            # 헤더와 데이터 준비
            headers = list(df.columns)
            print(f"📋 헤더: {headers}")

            # DataFrame을 리스트로 변환
            data_list = df.values.tolist()
            print(f"📊 데이터 {len(data_list)}개 행 준비 완료")
            if data_list:
                print(f"🔍 첫 번째 데이터 샘플: {data_list[0]}")
                print(f"🔍 데이터 타입 확인: {[type(item) for item in data_list[0]]}")

            # 업데이트 시간 추가
            update_time = f"업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # 헤더 입력
            try:
                worksheet.update(values=[headers], range_name='A1:B1')
                print("✅ 헤더 입력 완료")
            except Exception as e:
                print(f"❌ 헤더 입력 실패: {e}")
                # 대안 방법 시도
                worksheet.update(range_name='A1:B1', values=[headers])
                print("✅ 헤더 입력 완료 (대안 방법)")

            # 데이터 입력
            if data_list:
                # 데이터 범위 계산
                end_row = len(data_list) + 1
                range_notation = f'A2:B{end_row}'
                print(f"📍 데이터 입력 범위: {range_notation}")

                try:
                    worksheet.update(values=data_list, range_name=range_notation)
                    print("✅ 데이터 입력 완료")
                except Exception as e:
                    print(f"❌ 데이터 입력 실패: {e}")
                    # 대안 방법 시도
                    worksheet.update(range_name=range_notation, values=data_list)
                    print("✅ 데이터 입력 완료 (대안 방법)")
            else:
                print("⚠️ 입력할 데이터가 없습니다")

            # 업데이트 시간 입력
            try:
                worksheet.update(values=[[update_time]], range_name='D1')
                print("✅ 업데이트 시간 입력 완료")
            except Exception as e:
                print(f"⚠️ 업데이트 시간 입력 실패: {e}")

            # 헤더 서식 설정
            try:
                worksheet.format('A1:B1', {
                    "backgroundColor": {"red": 1.0, "green": 0.6, "blue": 0.2},
                    "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
                })
                print("✅ 헤더 서식 설정 완료")
            except Exception as e:
                print(f"⚠️ 헤더 서식 설정 실패: {e}")

            print(f"🏢 구글 시트 지자체보조금 {len(df)}개 업로드 완료")

        except Exception as e:
            print(f"❌ 구글 시트 지자체보조금 업로드 실패: {e}")
            import traceback
            traceback.print_exc()


class EVSubsidyManager:
    def __init__(self, data_dir='ev_data', method='auto',
                 use_google_sheets=False, credentials_file=None, spreadsheet_id=None):
        self.url = "https://www.ev.or.kr/nportal/buySupprt/initBuySubsidySupprtAction.do"
        self.data_dir = data_dir
        self.national_file = os.path.join(data_dir, 'national_subsidy.csv')
        self.local_file = os.path.join(data_dir, 'local_subsidy.csv')
        self.metadata_file = os.path.join(data_dir, 'metadata.json')

        # 크롤링 방법 선택 (auto, requests, requests-html, playwright, pyppeteer)
        self.method = method

        # 구글 시트 설정
        self.use_google_sheets = use_google_sheets
        print(f"🔧 구글 시트 설정:")
        print(f"   - use_google_sheets: {use_google_sheets}")
        print(f"   - credentials_file: {credentials_file}")
        print(f"   - spreadsheet_id: {spreadsheet_id}")
        print(f"   - GOOGLE_SHEETS_AVAILABLE: {GOOGLE_SHEETS_AVAILABLE}")

        if use_google_sheets and credentials_file and spreadsheet_id and GOOGLE_SHEETS_AVAILABLE:
            try:
                print("📊 구글 시트 매니저 생성 시도...")
                self.sheets_manager = GoogleSheetsManager(credentials_file, spreadsheet_id)
                print("✅ 구글 시트 연동 활성화")
            except Exception as e:
                print(f"⚠️ 구글 시트 연동 실패, CSV만 저장: {e}")
                import traceback
                traceback.print_exc()
                self.sheets_manager = None
        else:
            self.sheets_manager = None
            if use_google_sheets:
                print("⚠️ 구글 시트 설정 불완전:")
                if not GOOGLE_SHEETS_AVAILABLE:
                    print("   - GOOGLE_SHEETS_AVAILABLE = False")
                if not credentials_file:
                    print("   - credentials_file 없음")
                if not spreadsheet_id:
                    print("   - spreadsheet_id 없음")
                print("   → CSV만 저장됩니다")

        # 데이터 디렉토리 생성
        os.makedirs(data_dir, exist_ok=True)

        # 메타데이터 로드
        self.metadata = self.load_metadata()

        # 사용 가능한 방법 확인
        self.available_methods = self._check_available_methods()
        print(f"🔧 사용 가능한 크롤링 방법: {', '.join(self.available_methods)}")

    def _check_available_methods(self):
        """사용 가능한 크롤링 방법 확인"""
        methods = ['requests']  # 기본적으로 requests는 항상 사용 가능

        if REQUESTS_HTML_AVAILABLE:
            methods.append('requests-html')
        if PLAYWRIGHT_AVAILABLE:
            methods.append('playwright')
        if PYPPETEER_AVAILABLE:
            methods.append('pyppeteer')

        return methods

    def _select_method(self):
        """최적의 크롤링 방법 자동 선택"""
        if self.method != 'auto':
            return self.method

        # 우선순위: requests-html > playwright > pyppeteer > requests
        # JavaScript 렌더링 가능한 방법을 우선 선택
        if 'requests-html' in self.available_methods:
            return 'requests-html'
        elif 'playwright' in self.available_methods:
            return 'playwright'
        elif 'pyppeteer' in self.available_methods:
            print("💡 pyppeteer 사용 - JavaScript 렌더링으로 더 많은 데이터 수집 가능")
            return 'pyppeteer'
        else:
            print("⚠️  JavaScript 렌더링 라이브러리가 없어 제한적인 데이터만 수집됩니다.")
            return 'requests'

    def load_metadata(self):
        """메타데이터 로드"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'last_updated': None,
            'national_hash': None,
            'local_hash': None,
            'total_runs': 0,
            'method_used': None
        }

    def save_metadata(self):
        """메타데이터 저장"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

    def calculate_data_hash(self, data):
        """데이터의 해시값 계산"""
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode()).hexdigest()

    # 방법 1: 기본 requests + BeautifulSoup
    def crawl_with_requests(self):
        """기본 requests를 사용한 크롤링"""
        try:
            print("📡 requests 방법으로 크롤링 시작...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }

            session = requests.Session()
            response = session.get(self.url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            return self.extract_both_tables(soup, "requests")

        except Exception as e:
            print(f"❌ requests 크롤링 실패: {e}")
            return None, None

    # 방법 2: requests-html (가장 간단한 JavaScript 렌더링)
    def crawl_with_requests_html(self):
        """requests-html을 사용한 크롤링"""
        if not REQUESTS_HTML_AVAILABLE:
            print("❌ requests-html이 설치되지 않음")
            return None, None

        try:
            print("🌐 requests-html 방법으로 크롤링 시작...")
            session = HTMLSession()

            # 요청
            r = session.get(self.url)

            # JavaScript 렌더링 (최대 10초 대기)
            print("⏳ JavaScript 렌더링 중... (최대 10초)")
            r.html.render(wait=3, timeout=10)

            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(r.html.html, 'html.parser')

            # 세션 정리
            session.close()

            return self.extract_both_tables(soup, "requests-html")

        except Exception as e:
            print(f"❌ requests-html 크롤링 실패: {e}")
            return None, None

    # 방법 3: Playwright (현대적이고 빠름)
    def crawl_with_playwright(self):
        """Playwright를 사용한 크롤링"""
        if not PLAYWRIGHT_AVAILABLE:
            print("❌ Playwright가 설치되지 않음")
            return None, None

        try:
            print("🎭 Playwright 방법으로 크롤링 시작...")

            with sync_playwright() as p:
                # 브라우저 시작 (headless 모드)
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # User-Agent 설정
                page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

                # 페이지 로드
                print("📄 페이지 로딩 중...")
                page.goto(self.url, wait_until='networkidle', timeout=30000)

                # 테이블이 로드될 때까지 대기
                try:
                    page.wait_for_selector('table.table01.fz15', timeout=10000)
                    print("✅ 테이블 로드 완료")
                except:
                    print("⚠️  테이블 로드 대기 시간 초과")

                # HTML 추출
                html_content = page.content()
                browser.close()

                # BeautifulSoup으로 파싱
                soup = BeautifulSoup(html_content, 'html.parser')
                return self.extract_both_tables(soup, "playwright")

        except Exception as e:
            print(f"❌ Playwright 크롤링 실패: {e}")
            return None, None

    # 방법 4: Pyppeteer (비동기 처리)
    def crawl_with_pyppeteer(self):
        """Pyppeteer를 사용한 크롤링"""
        if not PYPPETEER_AVAILABLE:
            print("❌ Pyppeteer가 설치되지 않음")
            return None, None

        try:
            print("🐍 Pyppeteer 방법으로 크롤링 시작...")

            # 비동기 함수 실행
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._pyppeteer_crawl())
            loop.close()

            return result

        except Exception as e:
            print(f"❌ Pyppeteer 크롤링 실패: {e}")
            return None, None

    async def _pyppeteer_crawl(self):
        """Pyppeteer 비동기 크롤링 함수"""
        browser = await pyppeteer.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu'
            ]
        )
        page = await browser.newPage()

        # User-Agent 설정
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        # 페이지 로드
        print("📄 페이지 로딩 중...")
        response = await page.goto(self.url, {'waitUntil': 'networkidle0', 'timeout': 30000})
        print(f"📊 페이지 응답 상태: {response.status}")

        # 현재 URL 확인
        current_url = page.url
        print(f"🔗 현재 URL: {current_url}")

        # 페이지 제목 확인
        title = await page.title()
        print(f"📄 페이지 제목: {title}")

        # 탭 또는 JavaScript 동작 확인을 위해 추가 대기
        print("⏳ JavaScript 실행 대기 중...")
        await page.waitFor(5000)  # 5초 대기

        # 지자체 보조금 탭이 있는지 확인하고 클릭 시도
        try:
            # 지자체 보조금 탭 또는 버튼 찾기
            tab_selectors = [
                'a[href*="지자체"]',
                'button:contains("지자체")',
                '.tab:contains("지자체")',
                '[data-tab*="local"]',
                '[data-tab*="지자체"]'
            ]

            tab_clicked = False
            for selector in tab_selectors:
                try:
                    await page.click(selector)
                    print(f"✅ 지자체 보조금 탭 클릭 성공: {selector}")
                    await page.waitFor(3000)  # 탭 전환 대기
                    tab_clicked = True
                    break
                except:
                    continue

            if not tab_clicked:
                print("⚠️  지자체 보조금 탭을 찾을 수 없습니다.")
        except Exception as e:
            print(f"⚠️  탭 클릭 시도 중 오류: {e}")

        # 테이블 대기 - 여러 선택자로 시도
        selectors_to_try = [
            'table.table01.fz15',
            'table.table01',
            'table',
            '.subWrap table'
        ]

        table_found = False
        for selector in selectors_to_try:
            try:
                elements = await page.querySelectorAll(selector)
                if elements:
                    print(f"✅ 테이블 발견: {len(elements)}개 (선택자: {selector})")
                    table_found = True
                    break
            except:
                continue

        if not table_found:
            print("⚠️  테이블을 찾을 수 없습니다.")

        # 페이지의 모든 테이블 정보 수집
        try:
            tables_info = await page.evaluate('''() => {
                const tables = document.querySelectorAll('table');
                return Array.from(tables).map((table, index) => {
                    const rows = table.querySelectorAll('tr');
                    const headers = Array.from(table.querySelectorAll('th, tr:first-child td')).map(h => h.textContent.trim());
                    return {
                        index: index,
                        className: table.className,
                        rowCount: rows.length,
                        headers: headers.slice(0, 5), // 처음 5개 헤더만
                        parentDiv: table.closest('div') ? table.closest('div').className : 'none'
                    };
                });
            }''')

            print(f"🔍 페이지 내 모든 테이블 정보:")
            for info in tables_info:
                print(f"   테이블 {info['index']}: 클래스='{info['className']}', 행수={info['rowCount']}")
                print(f"   헤더: {info['headers']}")
                print(f"   부모 div: {info['parentDiv']}")
                print()

        except Exception as e:
            print(f"⚠️  테이블 정보 수집 중 오류: {e}")

        # HTML 추출
        html_content = await page.content()

        # HTML 일부 저장 (디버깅용)
        debug_html_file = os.path.join(self.data_dir, 'debug_page_source.html')
        with open(debug_html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"📁 페이지 소스 저장: {debug_html_file}")

        await browser.close()

        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        return self.extract_both_tables(soup, "pyppeteer")

    def extract_both_tables(self, soup, method_name):
        """국고 보조금과 지자체 보조금 테이블 추출"""
        print(f"🔍 {method_name} 방법으로 테이블 데이터 추출 중...")

        # 모든 테이블 분석 및 분류
        all_tables = soup.find_all('table', class_='table01 fz15')
        print(f"🔍 총 {len(all_tables)}개 테이블 발견")

        national_table = None
        local_table = None

        for i, table in enumerate(all_tables):
            # 헤더 확인
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            else:
                first_row = table.find('tr')
                headers = [td.get_text(strip=True) for td in first_row.find_all(['th', 'td'])] if first_row else []

            print(f"   테이블 {i}: {headers}")

            # 지자체 보조금 테이블 식별 (시도, 전기자동차 컬럼이 있는 경우)
            if any('시도' in h for h in headers) and any('전기' in h for h in headers):
                local_table = table
                print(f"   ✅ 테이블 {i}를 지자체 보조금으로 식별")

            # 국고 보조금 테이블 식별 (구분, 제조사, 차종, 보조금 컬럼이 있고 행이 많은 경우)
            elif (any('구분' in h for h in headers) and
                  any('제조' in h or '수입' in h for h in headers) and
                  any('차종' in h for h in headers) and
                  any('보조금' in h for h in headers)):

                # 행 수 확인
                tbody = table.find('tbody')
                if tbody:
                    row_count = len(tbody.find_all('tr'))
                    if row_count > 10 and national_table is None:  # 행이 많은 첫 번째 테이블
                        national_table = table
                        print(f"   ✅ 테이블 {i}를 국고 보조금으로 식별 (행수: {row_count})")

        # 국고 보조금 데이터 추출
        national_data = []
        if national_table:
            national_div = national_table.find_parent('div')
            national_data = self.extract_table_from_div(national_div, "국고 보조금")

            # 데이터가 부족한 경우 대안 파서 시도
            if len(national_data) < 90:
                print(f"🔄 수집된 데이터가 적음 ({len(national_data)}개), 대안 파서 시도...")
                alternative_data = self.use_alternative_html_parser(soup)
                if alternative_data and len(alternative_data) > len(national_data):
                    print(f"✅ 대안 파서로 더 많은 데이터 수집: {len(alternative_data)}개")
                    national_data = alternative_data
        else:
            print("❌ 국고 보조금 테이블을 찾을 수 없습니다.")

        # 지자체 보조금 데이터 추출
        local_data = []
        if local_table:
            local_div = local_table.find_parent('div')
            local_data = self.extract_local_subsidy_table(local_table)
        else:
            print("❌ 지자체 보조금 테이블을 찾을 수 없습니다.")

        # 메타데이터에 사용된 방법 기록
        self.metadata['method_used'] = method_name

        return national_data, local_data

    def use_alternative_html_parser(self, soup):
        """대안 HTML 파서 - 더 많은 데이터 수집 시도"""
        print("🔄 대안 파서 실행 중...")

        # 모든 테이블에서 전기차 관련 데이터 수집
        all_data = []
        all_tables = soup.find_all('table')

        for table in all_tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 3:
                    cell_texts = [cell.get_text(strip=True) for cell in cells]

                    # 전기차 관련 키워드 확인
                    row_text = ' '.join(cell_texts).lower()
                    if any(keyword in row_text for keyword in ['전기', 'ev', 'electric', '아이오닉', '코나']):
                        # 기본 구조로 매핑
                        if len(cell_texts) >= 4:
                            data_row = {
                                '차량구분': cell_texts[0] if cell_texts[0] else '승용',
                                '제조사': cell_texts[1],
                                '모델명': cell_texts[2],
                                '국고보조금': cell_texts[3] if cell_texts[3].isdigit() else '0'
                            }
                            all_data.append(data_row)

        return all_data

    def extract_local_subsidy_table(self, table):
        """지자체 보조금 테이블 전용 추출 함수"""
        print("🏢 지자체 보조금 테이블 처리 중...")

        # 헤더 추출
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        else:
            first_row = table.find('tr')
            headers = [td.get_text(strip=True) for td in first_row.find_all(['th', 'td'])] if first_row else []

        print(f"📋 지자체 보조금 헤더: {headers}")

        # tbody에서 데이터 행 추출
        tbody = table.find('tbody')
        if not tbody:
            print("❌ 지자체 보조금 tbody를 찾을 수 없습니다.")
            return []

        rows = tbody.find_all('tr')
        data = []

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 2:  # 최소 2개 컬럼 (지역, 보조금)
                row_data = {}

                for i, cell in enumerate(cells):
                    if i < len(headers):
                        header_name = headers[i]
                        cell_text = cell.get_text(strip=True)
                        row_data[header_name] = cell_text

                # 빈 행이 아닌 경우 추가
                if any(value.strip() for value in row_data.values()):
                    # 지자체 보조금 데이터 표준화
                    standardized = self._standardize_local_subsidy_data(row_data)
                    if standardized:
                        data.append(standardized)

        print(f"✅ 지자체 보조금 데이터 {len(data)}개 추출 완료")
        return data

    def extract_table_from_div(self, div_element, subsidy_type):
        """특정 div 내의 테이블 데이터 추출 (전기자동차만 필터링, rowspan 처리 개선)"""
        if not div_element:
            print(f"❌ {subsidy_type} div를 찾을 수 없습니다.")
            return []

        table = div_element.find('table', class_='table01 fz15')
        if not table:
            print(f"❌ {subsidy_type} 테이블을 찾을 수 없습니다.")
            return []

        data = []

        # 헤더 추출
        header_row = table.find('thead')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        else:
            first_row = table.find('tr')
            if first_row:
                headers = [td.get_text(strip=True) for td in first_row.find_all(['th', 'td'])]
            else:
                print(f"❌ {subsidy_type} 헤더를 찾을 수 없습니다.")
                return []

        # 불완전한 헤더 정리 (5번째 컬럼 제거)
        if len(headers) > 4:
            headers = headers[:4]

        print(f"📋 {subsidy_type} 헤더: {headers}")

        # tbody에서 데이터 행 추출
        tbody = table.find('tbody')
        if not tbody:
            print(f"❌ {subsidy_type} tbody를 찾을 수 없습니다.")
            return []

        rows = tbody.find_all('tr')

        # rowspan 처리를 위한 변수들
        rowspan_values = {}  # {column_index: {'value': str, 'remaining': int}}
        electric_keywords = ['전기', 'EV', 'electric', 'Electrified', 'e-', '아이오닉', '레이', 'EQC', 'EQS', 'Model', '볼트',
                             '코나', 'KONA', 'GV60', 'GV70', 'ATTO', 'BYD', '일렉트릭', '캐스퍼', 'EV6', 'EV9', 'bZ4X',
                             'Taycan', 'e-tron', 'EQA', 'EQB', 'EQV', 'iX3', 'i7', 'Polestar', 'XC40', 'C40', 'EX90']
        total_rows = 0
        filtered_rows = 0

        # 누락 분석용 변수
        skipped_reasons = {
            '빈_행': 0,
            '전기차_아님': 0,
            '표준화_실패': 0,
            '재시도_실패': 0
        }

        # 제외된 행들을 저장할 리스트
        skipped_rows = []

        for row_idx, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue

            total_rows += 1
            row_data = {}

            # rowspan 값들의 remaining 감소
            for col_idx in list(rowspan_values.keys()):
                rowspan_values[col_idx]['remaining'] -= 1
                if rowspan_values[col_idx]['remaining'] <= 0:
                    del rowspan_values[col_idx]

            # 각 헤더 컬럼에 대해 값 설정 (rowspan 처리 개선)
            cell_idx = 0
            for col_idx, header in enumerate(headers):
                if col_idx in rowspan_values:
                    # rowspan으로 유지되는 값 사용
                    row_data[header] = rowspan_values[col_idx]['value']
                elif cell_idx < len(cells):
                    # 새로운 셀 값 사용
                    cell = cells[cell_idx]
                    cell_text = cell.get_text(strip=True)
                    rowspan = int(cell.get('rowspan', 1))

                    row_data[header] = cell_text

                    # rowspan이 1보다 크면 저장
                    if rowspan > 1:
                        rowspan_values[col_idx] = {
                            'value': cell_text,
                            'remaining': rowspan - 1
                        }

                    cell_idx += 1
                else:
                    # 값이 없는 경우 빈 문자열
                    row_data[header] = ''

            # 디버깅: 문제가 있는 행 미리 확인
            if (row_data.get('차종', '').isdigit() or
                    row_data.get('제조/수입사', '').isdigit() or
                    (row_data.get('구분', '') and self._is_car_model_name(row_data.get('구분', '')))):
                print(f"🔍 rowspan 오류 의심 행: {row_data}")

            # 빈 행 체크
            if not any(value.strip() for value in row_data.values()):
                skipped_reasons['빈_행'] += 1
                skipped_rows.append(('빈_행', row_idx + 1, row_data))
                continue

            # 전기자동차 필터링
            is_electric = False

            # 모든 셀 내용에서 전기차 키워드 확인
            all_text = ' '.join(row_data.values()).lower()
            for ek in electric_keywords:
                if ek.lower() in all_text:
                    is_electric = True
                    break

            # 구분이 승용, 경소형인 경우 추가 확인 (수소차 제외)
            if not is_electric and '구분' in row_data:
                category = row_data['구분'].lower()
                if any(cat in category for cat in ['승용', '경', '소형']) and '수소' not in category and '화물' not in category:
                    # 차종명이 있고 수소차가 아닌 경우 전기차로 간주
                    car_model = row_data.get('차종', '')
                    if car_model.strip() and '수소' not in car_model.lower():
                        is_electric = True

            # 전기차인 경우에만 추가
            if is_electric:
                # 제조사 정보 업데이트 (rowspan 추적용)
                if '제조/수입사' in row_data and row_data['제조/수입사'].strip():
                    self._set_last_manufacturer(row_data['제조/수입사'])

                # 국고 보조금과 지자체 보조금의 컬럼명 통일
                if subsidy_type == "지자체 보조금":
                    standardized_data = self._standardize_local_subsidy_data(row_data)
                else:
                    standardized_data = self._standardize_national_subsidy_data(row_data)

                if standardized_data:
                    data.append(standardized_data)
                    filtered_rows += 1
                    if len(data) <= 5:  # 처음 5개만 출력
                        print(f"✅ 추가됨: {standardized_data}")
                else:
                    # 표준화 실패한 경우 추가 시도
                    retry_data = self._retry_failed_standardization(row_data)
                    if retry_data:
                        data.append(retry_data)
                        filtered_rows += 1
                        print(f"✅ 재시도 성공: {retry_data}")
                    else:
                        skipped_reasons['표준화_실패'] += 1
                        skipped_rows.append(('표준화_실패', row_idx + 1, row_data))
                        print(f"❌ 표준화 실패: {row_data}")
            else:
                # 전기차가 아닌 경우
                skipped_reasons['전기차_아님'] += 1
                skipped_rows.append(('전기차_아님', row_idx + 1, row_data))

                # 수소차인지 확인
                if '수소' in all_text:
                    print(f"⚪ 수소차 필터링 ({row_idx + 1}행): {row_data}")
                else:
                    print(f"⚪ 전기차 키워드 미인식 ({row_idx + 1}행): {row_data}")

        print(f"📊 {subsidy_type}: 전체 {total_rows}개 행 중 전기차 {filtered_rows}개 추출")

        # 누락된 데이터 분석
        missing_count = total_rows - filtered_rows
        if missing_count > 0:
            print(f"🔍 누락된 {missing_count}개 데이터 상세 분석:")
            for reason, count in skipped_reasons.items():
                if count > 0:
                    print(f"   - {reason}: {count}개")

            # 제외된 행들 상세 출력
            print(f"\n📝 제외된 {len(skipped_rows)}개 행 상세 내용:")
            for i, (reason, row_num, row_data) in enumerate(skipped_rows, 1):
                print(f"   {i}. 행 {row_num} ({reason}): {row_data}")

            # 누락된 데이터가 적은 경우 더 자세히 분석
            if missing_count <= 5:
                print(f"\n💡 전기차 키워드 확장 검토:")
                for reason, row_num, row_data in skipped_rows:
                    if reason == '전기차_아님':
                        all_text = ' '.join(row_data.values()).lower()
                        print(f"   행 {row_num}: '{all_text}'")

                        # 숨겨진 전기차 패턴 확인
                        hidden_patterns = ['phev', 'hybrid', 'h2', 'fcev', 'bev', 'ev6', 'ioniq', 'id.', 'e-tron',
                                           'taycan']
                        for pattern in hidden_patterns:
                            if pattern in all_text:
                                print(f"      → 발견된 패턴: '{pattern}' (전기차 키워드 추가 고려)")
                                break

        print(f"✅ {subsidy_type} 전기차 데이터 {len(data)}개 추출 완료")
        return data

    def _retry_failed_standardization(self, row_data):
        """표준화 실패한 데이터 재시도"""
        # 다양한 패턴으로 재시도
        attempts = [
            # 시도 1: 모든 필드를 한 칸씩 밀기
            {
                '차량구분': '승용',
                '제조사': self._get_previous_manufacturer(),
                '모델명': row_data.get('구분', ''),
                '국고보조금': row_data.get('제조/수입사', '')
            },
            # 시도 2: 제조사와 차종 바꾸기
            {
                '차량구분': row_data.get('구분', ''),
                '제조사': self._get_previous_manufacturer(),
                '모델명': row_data.get('제조/수입사', ''),
                '국고보조금': row_data.get('차종', '')
            },
            # 시도 3: 차종과 보조금 바꾸기
            {
                '차량구분': row_data.get('구분', ''),
                '제조사': row_data.get('제조/수입사', ''),
                '모델명': row_data.get('국고보조금 지원금액(만원)', ''),
                '국고보조금': row_data.get('차종', '')
            }
        ]

        for attempt in attempts:
            if self._validate_standardized_data(attempt):
                return attempt

        return None

    def _standardize_national_subsidy_data(self, row_data):
        """국고 보조금 데이터 표준화 (rowspan 오류 완전 복구)"""
        standardized = {}

        # 원본 데이터 분석
        category = row_data.get('구분', '').strip()
        manufacturer = row_data.get('제조/수입사', '').strip()
        model = row_data.get('차종', '').strip()
        subsidy = row_data.get('국고보조금 지원금액(만원)', '').strip()

        # rowspan 오류 패턴 감지 및 수정
        if model.isdigit() and not subsidy:
            # 패턴 1: 차종 자리에 보조금이 들어간 경우
            print(f"🔧 rowspan 오류 감지 및 수정: 차종({model})이 숫자")

            # 데이터 재배열
            fixed_category = category if category in ['승용', '경·소형'] else '승용'  # 기본값
            fixed_manufacturer = self._get_previous_manufacturer()  # 이전 제조사 사용
            fixed_model = manufacturer  # 제조사 → 모델명
            fixed_subsidy = model  # 차종 → 보조금

            # 제조사가 실제 차종명인지 확인
            if self._is_car_model_name(manufacturer):
                standardized = {
                    '차량구분': fixed_category,
                    '제조사': fixed_manufacturer,
                    '모델명': fixed_model,
                    '국고보조금': fixed_subsidy
                }
                print(f"✅ 수정 완료: {standardized}")
                return standardized

        elif manufacturer.isdigit() and not subsidy:
            # 패턴 2: 제조사 자리에 보조금이 들어간 경우
            print(f"🔧 rowspan 오류 감지 및 수정: 제조사({manufacturer})가 숫자")

            if self._is_car_model_name(category):
                standardized = {
                    '차량구분': '승용',  # 기본값
                    '제조사': self._get_previous_manufacturer(),
                    '모델명': category,  # 구분 → 모델명
                    '국고보조금': manufacturer  # 제조사 → 보조금
                }
                print(f"✅ 수정 완료: {standardized}")
                return standardized

        # 새로운 패턴 3: 구분에 제조사명이 들어가고 제조사에 모델명이 들어간 경우
        elif self._is_manufacturer_name(category) and self._is_car_model_name(manufacturer):
            print(f"🔧 rowspan 오류 감지 및 수정: 구분({category})에 제조사, 제조사({manufacturer})에 모델명")

            standardized = {
                '차량구분': '승용',  # 기본값
                '제조사': category,  # 구분 → 제조사
                '모델명': manufacturer,  # 제조사 → 모델명
                '국고보조금': model if model.isdigit() else '0'  # 차종 → 보조금
            }
            print(f"✅ 수정 완료: {standardized}")
            return standardized

        # 새로운 패턴 4: 구분에 모델명이 들어가고 제조사에 보조금이 들어간 경우
        elif self._is_car_model_name(category) and manufacturer.isdigit():
            print(f"🔧 rowspan 오류 감지 및 수정: 구분({category})에 모델명, 제조사({manufacturer})에 보조금")

            standardized = {
                '차량구분': '승용',  # 기본값
                '제조사': self._get_previous_manufacturer(),  # 이전 제조사 사용
                '모델명': category,  # 구분 → 모델명
                '국고보조금': manufacturer  # 제조사 → 보조금
            }
            print(f"✅ 수정 완료: {standardized}")
            return standardized

        # 정상적인 경우 또는 다른 패턴
        else:
            standardized = {
                '차량구분': category,
                '제조사': manufacturer,
                '모델명': model,
                '국고보조금': subsidy
            }

        # 제조사 정보 업데이트 (다음 행에서 사용)
        if manufacturer and not manufacturer.isdigit():
            self._set_last_manufacturer(manufacturer)

        # 데이터 유효성 검사
        if not self._validate_standardized_data(standardized):
            print(f"⚠️  표준화 실패 상세: {standardized}")
            return None

        return standardized

    def _is_manufacturer_name(self, text):
        """텍스트가 제조사명인지 판단"""
        if not text:
            return False

        # 제조사명 리스트
        manufacturers = [
            '현대자동차', '기아', 'BMW', '테슬라코리아', '메르세데스벤츠코리아',
            '케이지모빌리티', '폴스타오토모티브코리아', '볼보자동차코리아',
            '폭스바겐그룹코리아', '비와이디코리아', 'BYD', '현대', '기아자동차',
            '테슬라', '메르세데스벤츠', '볼보', '폴스타', '폭스바겐'
        ]

        # 부분 매칭도 고려
        for mfr in manufacturers:
            if mfr.lower() in text.lower() or text.lower() in mfr.lower():
                return True

        return False

    def _is_car_model_name(self, text):
        """텍스트가 차량 모델명인지 판단"""
        if not text or text.isdigit():
            return False

        # 차량 모델명 특징
        model_indicators = [
            'EV', 'electric', 'Electrified', 'e-tron', 'Model', 'GV60', 'GV70',
            '아이오닉', '레이', '코나', 'KONA', 'ID.', 'i4', 'iX', 'MINI',
            'Polestar', 'EQA', 'EQB', '캐스퍼', '토레스', 'EVX', '볼보', 'EX30',
            'ATTO', 'BYD', '일렉트릭', '전기', 'EV6', 'EV9', 'e-GMP', 'bZ4X',
            'Taycan', 'e-tron', 'EQS', 'EQC', 'EQV', 'iX3', 'i7', 'Polestar',
            'XC40', 'C40', 'EX90', 'EM90', 'Seal', 'Dolphin', 'Yuan', 'Song'
        ]

        # 모델명 키워드가 포함되어 있거나 길이가 적절한 경우
        if any(indicator.lower() in text.lower() for indicator in model_indicators):
            return True

        # 적절한 길이의 텍스트이고 숫자가 아닌 경우
        if len(text) > 3 and not text.isdigit() and any(c.isalpha() for c in text):
            return True

        return False

    def _validate_standardized_data(self, data):
        """표준화된 데이터 유효성 검사"""
        required_fields = ['차량구분', '제조사', '모델명', '국고보조금']

        for field in required_fields:
            if field not in data or not data[field]:
                return False

        # 보조금이 숫자인지 확인
        if not data['국고보조금'].isdigit():
            return False

        # 차량구분이 올바른지 확인
        if data['차량구분'] not in ['승용', '경·소형']:
            return False

        # 모델명이 숫자만으로 구성되지 않았는지 확인
        if data['모델명'].isdigit():
            return False

        return True

    def _get_previous_manufacturer(self):
        """이전에 처리된 제조사명 반환 (rowspan 오류 복구용)"""
        if not hasattr(self, '_last_manufacturer'):
            # 기본값들 중에서 선택
            self._last_manufacturer = '현대자동차'
        return self._last_manufacturer

    def _set_last_manufacturer(self, manufacturer):
        """마지막 제조사명 저장"""
        # 유효한 제조사명만 저장
        valid_manufacturers = [
            '현대자동차', '기아', 'BMW', '테슬라코리아', '메르세데스벤츠코리아',
            '케이지모빌리티', '폴스타오토모티브코리아', '볼보자동차코리아',
            '폭스바겐그룹코리아', '비와이디코리아'
        ]

        if manufacturer and any(mfr in manufacturer for mfr in valid_manufacturers):
            self._last_manufacturer = manufacturer

    def _standardize_local_subsidy_data(self, row_data):
        """지자체 보조금 데이터 표준화 (전기차만, 수소차 제외)"""
        standardized = {}

        # 지자체 보조금의 컬럼 구조에 맞게 매핑 (전기차만)
        column_mapping = {
            '시도': '지역',
            '전기자동차': '전기차보조금'
        }

        for original_key, standard_key in column_mapping.items():
            if original_key in row_data and row_data[original_key].strip():
                value = row_data[original_key].strip()
                if standard_key == '지역':  # 지역명은 항상 포함
                    standardized[standard_key] = value
                elif value and value != '-' and value != '미지원' and any(c.isdigit() for c in value):
                    # 전기차 보조금만 포함 (숫자가 포함된 경우)
                    # 보조금 데이터 정제
                    cleaned_subsidy = self._clean_subsidy_amount(value)
                    if cleaned_subsidy:
                        standardized[standard_key] = cleaned_subsidy

        # 지자체 보조금의 경우 지역과 전기차보조금이 모두 있어야 함
        if '지역' in standardized and '전기차보조금' in standardized:
            return standardized
        return None

    def _clean_subsidy_amount(self, amount_str):
        """보조금 금액 데이터 정제"""
        if not amount_str:
            return None

        # 문자열 정제
        cleaned = amount_str.strip()

        # 쌍따옴표 제거
        cleaned = cleaned.replace('"', '').replace("'", "")

        # 쉼표 제거 (1,100 → 1100)
        cleaned = cleaned.replace(',', '')

        # 범위 표시(~)가 있는 경우 최소값만 추출
        if '~' in cleaned:
            # "200~484" → "200"
            min_amount = cleaned.split('~')[0].strip()
            cleaned = min_amount

        # 숫자만 추출 (단위 제거)
        import re
        numbers = re.findall(r'\d+\.?\d*', cleaned)

        if numbers:
            # 첫 번째 숫자 사용 (소수점 처리)
            amount = numbers[0]

            # 소수점이 있는 경우 정수로 변환
            if '.' in amount:
                amount = str(int(float(amount)))

            return amount

        return None

    def load_existing_data(self, file_path):
        """기존 데이터 로드"""
        if os.path.exists(file_path):
            try:
                return pd.read_csv(file_path, encoding='utf-8-sig')
            except Exception as e:
                print(f"⚠️  기존 데이터 로드 오류 ({file_path}): {e}")
                return pd.DataFrame()
        return pd.DataFrame()

    def update_data(self, new_data, existing_df, subsidy_type):
        """데이터 업데이트"""
        if not new_data:
            print(f"⚠️  {subsidy_type}: 새 데이터가 없습니다.")
            return existing_df, False

        new_df = pd.DataFrame(new_data)

        # 새 데이터 해시 계산
        new_hash = self.calculate_data_hash(new_data)

        # 기존 해시와 비교
        hash_key = 'national_hash' if subsidy_type == '국고 보조금' else 'local_hash'
        if self.metadata.get(hash_key) == new_hash:
            print(f"ℹ️  {subsidy_type}: 데이터 변경사항이 없습니다.")
            return existing_df, False

        # 해시 업데이트
        self.metadata[hash_key] = new_hash

        if existing_df.empty:
            print(f"🆕 {subsidy_type}: 새로운 데이터셋 생성")
            return new_df, True

        print(f"🔄 {subsidy_type}: 전체 데이터 업데이트")
        return new_df, True

    def save_data(self, df, file_path, subsidy_type):
        """데이터 저장 (CSV + 구글 시트)"""
        try:
            # CSV 저장 (기존)
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"💾 {subsidy_type} 데이터 저장 완료: {file_path}")

            # DataFrame 정보 출력 (디버깅)
            print(f"🔍 {subsidy_type} DataFrame 정보:")
            print(f"   - 타입: {type(df)}")
            print(f"   - 크기: {df.shape}")
            print(f"   - 컬럼: {list(df.columns)}")
            print(f"   - 비어있음: {df.empty}")
            if not df.empty:
                print(f"   - 첫 번째 행: {df.iloc[0].to_dict()}")

            # 구글 시트 저장 (추가)
            if self.sheets_manager:
                print(f"📊 {subsidy_type} 구글 시트 업로드 시작...")
                if subsidy_type == "국고 보조금":
                    self.sheets_manager.upload_national_subsidy(df)
                elif subsidy_type == "지자체 보조금":
                    self.sheets_manager.upload_local_subsidy(df)
                print(f"📊 {subsidy_type} 구글 시트 업로드 완료")
            else:
                print(f"⚠️ {subsidy_type}: 구글 시트 매니저가 없음")

        except Exception as e:
            print(f"❌ {subsidy_type} 데이터 저장 오류: {e}")
            import traceback
            traceback.print_exc()

    def debug_page_structure(self, soup, save_to_file=True):
        """페이지 구조 디버깅 및 분석"""
        print("\n" + "=" * 60)
        print("🔍 페이지 구조 디버깅")
        print("=" * 60)

        debug_info = []

        # 1. 모든 div 태그 분석
        all_divs = soup.find_all('div')
        debug_info.append(f"총 div 태그 수: {len(all_divs)}")

        # 2. class 속성이 있는 div 분석
        class_divs = soup.find_all('div', class_=True)
        debug_info.append(f"class 속성이 있는 div 수: {len(class_divs)}")

        # 3. subWrap 관련 div 찾기
        subwrap_divs = soup.find_all('div', class_=lambda x: x and 'subWrap' in ' '.join(x) if isinstance(x,
                                                                                                          list) else 'subWrap' in x if x else False)
        debug_info.append(f"subWrap 관련 div 수: {len(subwrap_divs)}")

        for i, div in enumerate(subwrap_divs):
            class_name = ' '.join(div.get('class', []))
            debug_info.append(f"  - subWrap div {i + 1}: class='{class_name}'")

        # 4. 테이블 분석
        tables = soup.find_all('table')
        debug_info.append(f"총 table 태그 수: {len(tables)}")

        table01_tables = soup.find_all('table', class_='table01 fz15')
        debug_info.append(f"table01 fz15 클래스 테이블 수: {len(table01_tables)}")

        # 5. 각 테이블의 헤더 분석
        for i, table in enumerate(table01_tables):
            debug_info.append(f"\n--- 테이블 {i + 1} 분석 ---")

            # 헤더 추출
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            else:
                first_row = table.find('tr')
                headers = [td.get_text(strip=True) for td in first_row.find_all(['th', 'td'])] if first_row else []

            debug_info.append(f"헤더: {headers}")

            # 데이터 행 수 확인
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
            else:
                rows = table.find_all('tr')[1:] if len(table.find_all('tr')) > 1 else []

            debug_info.append(f"데이터 행 수: {len(rows)}")

            # 첫 번째 데이터 행 샘플
            if rows:
                first_row_data = [td.get_text(strip=True) for td in rows[0].find_all(['td', 'th'])]
                debug_info.append(f"첫 번째 행 데이터: {first_row_data}")

        # 6. 텍스트에서 키워드 검색
        page_text = soup.get_text()
        keywords = ['국고', '지자체', '전기', '수소', '보조금']
        for keyword in keywords:
            count = page_text.count(keyword)
            debug_info.append(f"'{keyword}' 키워드 등장 횟수: {count}")

        # 출력
        for info in debug_info:
            print(info)

        # 파일로 저장
        if save_to_file:
            debug_file = os.path.join(self.data_dir, 'debug_page_structure.txt')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(debug_info))
                f.write('\n\n--- 전체 HTML 구조 ---\n')
                f.write(soup.prettify())
            print(f"📁 디버그 정보가 {debug_file}에 저장되었습니다.")

        print("=" * 60 + "\n")
        return debug_info

    def generate_report(self, national_df, local_df, method_used):
        """수집 결과 리포트 생성"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'method_used': method_used,
            'national_subsidy': {
                'count': len(national_df) if not national_df.empty else 0,
                'columns': list(national_df.columns) if not national_df.empty else []
            },
            'local_subsidy': {
                'count': len(local_df) if not local_df.empty else 0,
                'columns': list(local_df.columns) if not local_df.empty else []
            }
        }

        print("\n" + "=" * 60)
        print("📊 전기차 보조금 수집 결과 리포트")
        print("=" * 60)
        print(f"🕐 수집 시간: {report['timestamp']}")
        print(f"🔧 사용 방법: {report['method_used']}")
        print(f"🏛️  국고 보조금: {report['national_subsidy']['count']}개 항목")
        print(f"🏢 지자체 보조금: {report['local_subsidy']['count']}개 항목")

        if not national_df.empty:
            print(f"📋 국고 보조금 컬럼: {', '.join(report['national_subsidy']['columns'])}")

        if not local_df.empty:
            print(f"📋 지자체 보조금 컬럼: {', '.join(report['local_subsidy']['columns'])}")

        # JavaScript 필요 경고
        if method_used == 'requests' and (
                report['national_subsidy']['count'] < 50 or report['local_subsidy']['count'] == 0):
            print("\n⚠️  경고: requests 방법으로는 JavaScript가 필요한 데이터를 수집할 수 없습니다.")
            print("💡 더 많은 데이터를 위해 다음 라이브러리 설치를 권장합니다:")
            print("   /opt/anaconda3/bin/pip install requests-html")
            print("   또는")
            print(
                "   /opt/anaconda3/bin/pip install playwright && /opt/anaconda3/bin/python -m playwright install chromium")

        print("=" * 60 + "\n")
        return report

    def run(self, method=None, debug_mode=False, verbose_missing=False):
        """전체 프로세스 실행"""
        # verbose_missing 설정을 인스턴스 변수로 저장
        self.verbose_missing = verbose_missing

        # 방법 선택
        selected_method = method if method else self._select_method()

        if selected_method not in self.available_methods:
            print(f"❌ 선택한 방법 '{selected_method}'을 사용할 수 없습니다.")
            print(f"사용 가능한 방법: {', '.join(self.available_methods)}")
            return None, None

        print(f"🚀 전기차 보조금 데이터 수집 시작 (방법: {selected_method})")
        print(f"📈 실행 횟수: {self.metadata['total_runs'] + 1}")
        if debug_mode:
            print("🐛 디버그 모드 활성화")
        if verbose_missing:
            print("🔍 누락 데이터 상세 분석 모드 활성화")

        # 기존 데이터 로드
        existing_national = self.load_existing_data(self.national_file)
        existing_local = self.load_existing_data(self.local_file)

        # 선택된 방법으로 크롤링 실행
        national_data, local_data = None, None
        soup = None  # 디버깅용

        if selected_method == 'requests':
            national_data, local_data = self.crawl_with_requests()
        elif selected_method == 'requests-html':
            result = self.crawl_with_requests_html()
            if result and len(result) == 3:  # soup도 함께 반환하도록 수정된 경우
                national_data, local_data, soup = result
            else:
                national_data, local_data = result if result else (None, None)
        elif selected_method == 'playwright':
            national_data, local_data = self.crawl_with_playwright()
        elif selected_method == 'pyppeteer':
            national_data, local_data = self.crawl_with_pyppeteer()

        # 디버그 모드인 경우 페이지 구조 분석
        if debug_mode and soup:
            self.debug_page_structure(soup)

        # 실패시 다른 방법으로 시도
        if (not national_data and not local_data) and selected_method != 'requests':
            print(f"⚠️  {selected_method} 실패, 다른 방법으로 재시도...")

            for fallback_method in ['requests-html', 'playwright', 'requests']:
                if fallback_method != selected_method and fallback_method in self.available_methods:
                    print(f"🔄 {fallback_method} 방법으로 재시도...")

                    if fallback_method == 'requests':
                        national_data, local_data = self.crawl_with_requests()
                    elif fallback_method == 'requests-html':
                        national_data, local_data = self.crawl_with_requests_html()
                    elif fallback_method == 'playwright':
                        national_data, local_data = self.crawl_with_playwright()

                    if national_data or local_data:
                        selected_method = fallback_method
                        break

        if not national_data and not local_data:
            print("❌ 모든 방법으로 데이터 수집 실패")
            return None, None

        # 데이터 업데이트
        updated_national, national_changed = self.update_data(national_data, existing_national, "국고 보조금")
        updated_local, local_changed = self.update_data(local_data, existing_local, "지자체 보조금")

        # 변경사항이 있는 경우에만 저장
        if national_changed:
            self.save_data(updated_national, self.national_file, "국고 보조금")

        if local_changed:
            self.save_data(updated_local, self.local_file, "지자체 보조금")

        # 메타데이터 업데이트
        self.metadata['last_updated'] = datetime.now().isoformat()
        self.metadata['total_runs'] += 1
        self.metadata['method_used'] = selected_method
        self.save_metadata()

        # 리포트 생성
        report = self.generate_report(updated_national, updated_local, selected_method)

        print("✅ 프로세스 완료")
        return updated_national, updated_local


# 사용 예시 및 실행 부분
if __name__ == "__main__":
    print("🚗 전기차 보조금 크롤링 시스템 (개선된 버전)")
    print("=" * 50)

    # 구글 시트 설정 (기본 활성화)
    USE_GOOGLE_SHEETS = True  # 기본적으로 구글 시트 사용
    CREDENTIALS_FILE = "/Users/cullen/Documents/eccc/youtube-search-api-447606-43654b5c40cc.json"  # 실제 JSON 경로
    SPREADSHEET_ID = "1KqwyiVutE4_pCwNnAi5DZS0u7SbugLOCpCPDk3vI4AM"  # 실제 스프레드시트 ID

    # 구글 시트 비활성화 옵션 (필요한 경우)
    if '--no-google-sheets' in sys.argv:
        USE_GOOGLE_SHEETS = False
        print("📁 CSV 전용 모드 (구글 시트 비활성화)")

    # 스프레드시트 ID가 명령행 인수로 제공된 경우 (덮어쓰기)
    for i, arg in enumerate(sys.argv):
        if arg == '--spreadsheet-id' and i + 1 < len(sys.argv):
            SPREADSHEET_ID = sys.argv[i + 1]
            print(f"📄 사용자 지정 스프레드시트 ID: {SPREADSHEET_ID}")
            break

    # 매니저 인스턴스 생성
    if USE_GOOGLE_SHEETS and SPREADSHEET_ID:
        print("📊 구글 시트 연동 모드 (기본)")
        print(f"📄 스프레드시트: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")
        try:
            manager = EVSubsidyManager(
                method='auto',
                use_google_sheets=True,
                credentials_file=CREDENTIALS_FILE,
                spreadsheet_id=SPREADSHEET_ID
            )
        except Exception as e:
            print(f"⚠️ 구글 시트 연동 실패, CSV만 저장: {e}")
            manager = EVSubsidyManager(method='auto')
    else:
        print("📁 CSV 전용 모드")
        manager = EVSubsidyManager(method='auto')

    # 사용 가능한 방법 출력
    print(f"🔧 사용 가능한 방법: {', '.join(manager.available_methods)}")

    # JavaScript 렌더링 가능 여부 확인
    js_methods = [m for m in manager.available_methods if m in ['requests-html', 'playwright', 'pyppeteer']]
    if not js_methods:
        print("⚠️  JavaScript 렌더링 라이브러리가 설치되지 않았습니다.")
        print("💡 더 많은 데이터 수집을 위해 다음 중 하나를 설치하세요:")
        print("   /opt/anaconda3/bin/pip install requests-html     (가장 간단)")
        print(
            "   /opt/anaconda3/bin/pip install playwright && /opt/anaconda3/bin/python -m playwright install chromium  (고성능)")
        print("")

        # 사용자 선택
        user_choice = input("그래도 계속 진행하시겠습니까? (y/n): ").strip().lower()
        if user_choice not in ['y', 'yes', '네', 'ㅇ']:
            print("설치 후 다시 실행해주세요.")
            sys.exit(0)

    # 디버그 모드 옵션
    debug_mode = '--debug' in sys.argv or '-d' in sys.argv
    verbose_missing = '--verbose' in sys.argv or '-v' in sys.argv

    if debug_mode:
        print("🐛 디버그 모드로 실행 중...")

    if verbose_missing:
        print("🔍 누락 데이터 상세 분석 모드로 실행 중...")

    # 실행
    national_df, local_df = manager.run(debug_mode=debug_mode, verbose_missing=verbose_missing)

    # 결과 확인
    if national_df is not None and not national_df.empty:
        print(f"\n🏛️  국고 보조금 전기차 데이터:")
        print(f"   총 {len(national_df)}개 항목")
        print("\n📋 컬럼 정보:")
        for col in national_df.columns:
            print(f"   - {col}")
        print(f"\n🔍 데이터 미리보기:")
        print(national_df.head(3).to_string(index=False))

        # 데이터가 적은 경우 경고
        if len(national_df) < 10:
            print(f"\n⚠️  수집된 데이터가 적습니다 ({len(national_df)}개)")
            print("💡 JavaScript 렌더링 라이브러리 설치를 권장합니다:")
            print("   /opt/anaconda3/bin/pip install requests-html")
    else:
        print("❌ 국고 보조금 데이터를 찾을 수 없습니다.")

    if local_df is not None and not local_df.empty:
        print(f"\n🏢 지자체 보조금 전기차 데이터:")
        print(f"   총 {len(local_df)}개 항목")
        print("\n📋 컬럼 정보:")
        for col in local_df.columns:
            print(f"   - {col}")
        print(f"\n🔍 데이터 미리보기:")
        print(local_df.head(3).to_string(index=False))
    else:
        print("❌ 지자체 보조금 데이터를 찾을 수 없습니다.")
        print("💡 JavaScript 렌더링이 필요할 수 있습니다.")

    print(f"\n📁 데이터 저장 위치: {manager.data_dir}")

    # 최종 권장사항
    total_items = len(national_df) if national_df is not None else 0
    total_items += len(local_df) if local_df is not None else 0

    if total_items < 20:
        print(f"\n💡 수집된 총 데이터: {total_items}개")
        print("더 많은 데이터를 위해 JavaScript 렌더링 라이브러리를 설치하세요:")
        print("/opt/anaconda3/bin/pip install requests-html")

    print("🎉 크롤링 완료!")

    # 구글 시트 연동된 경우 링크 표시
    if manager.sheets_manager:
        print(f"📊 구글 시트에서 확인: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/")
        print("💡 팀원들과 실시간으로 데이터를 공유할 수 있습니다!")

    if debug_mode:
        print(f"\n💡 디버그 파일 확인: {os.path.join(manager.data_dir, 'debug_page_structure.txt')}")