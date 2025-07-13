import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List
from datetime import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class EVSubsidyCrawler:
    def __init__(self):
        self.base_url = "https://ev.or.kr"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # 전체 지역 목록
        self.regions = [
            # 특별시/광역시
            {'code': '1100', 'name': '서울특별시'},
            {'code': '2600', 'name': '부산광역시'},
            {'code': '2700', 'name': '대구광역시'},
            {'code': '2800', 'name': '인천광역시'},
            {'code': '2900', 'name': '광주광역시'},
            {'code': '3000', 'name': '대전광역시'},
            {'code': '3100', 'name': '울산광역시'},
            {'code': '3611', 'name': '세종특별자치시'},
            
            # 경기도
            {'code': '4111', 'name': '수원시'},
            {'code': '4113', 'name': '성남시'},
            {'code': '4115', 'name': '의정부시'},
            {'code': '4117', 'name': '안양시'},
            {'code': '4119', 'name': '부천시'},
            {'code': '4121', 'name': '광명시'},
            {'code': '4122', 'name': '평택시'},
            {'code': '4125', 'name': '동두천시'},
            {'code': '4127', 'name': '안산시'},
            {'code': '4128', 'name': '고양시'},
            {'code': '4129', 'name': '과천시'},
            {'code': '4131', 'name': '구리시'},
            {'code': '4136', 'name': '남양주시'},
            {'code': '4137', 'name': '오산시'},
            {'code': '4139', 'name': '시흥시'},
            {'code': '4141', 'name': '군포시'},
            {'code': '4143', 'name': '의왕시'},
            {'code': '4145', 'name': '하남시'},
            {'code': '4146', 'name': '용인시'},
            {'code': '4148', 'name': '파주시'},
            {'code': '4150', 'name': '이천시'},
            {'code': '4155', 'name': '안성시'},
            {'code': '4157', 'name': '김포시'},
            {'code': '4159', 'name': '화성시'},
            {'code': '4161', 'name': '광주시'},
            {'code': '4163', 'name': '양주시'},
            {'code': '4165', 'name': '포천시'},
            {'code': '4167', 'name': '여주시'},
            {'code': '4180', 'name': '연천군'},
            {'code': '4182', 'name': '가평군'},
            {'code': '4183', 'name': '양평군'},
            
            # 강원도
            {'code': '4211', 'name': '춘천시'},
            {'code': '4213', 'name': '원주시'},
            {'code': '4215', 'name': '강릉시'},
            {'code': '4217', 'name': '동해시'},
            {'code': '4219', 'name': '태백시'},
            {'code': '4221', 'name': '속초시'},
            {'code': '4223', 'name': '삼척시'},
            {'code': '4272', 'name': '홍천군'},
            {'code': '4273', 'name': '횡성군'},
            {'code': '4275', 'name': '영월군'},
            {'code': '4276', 'name': '평창군'},
            {'code': '4277', 'name': '정선군'},
            {'code': '4278', 'name': '철원군'},
            {'code': '4279', 'name': '화천군'},
            {'code': '4280', 'name': '양구군'},
            {'code': '4281', 'name': '인제군'},
            {'code': '4282', 'name': '고성군'},
            {'code': '4283', 'name': '양양군'},
            
            # 충청북도
            {'code': '4311', 'name': '청주시'},
            {'code': '4313', 'name': '충주시'},
            {'code': '4315', 'name': '제천시'},
            {'code': '4372', 'name': '보은군'},
            {'code': '4373', 'name': '옥천군'},
            {'code': '43745', 'name': '증평군'},
            {'code': '4374', 'name': '영동군'},
            {'code': '4375', 'name': '진천군'},
            {'code': '4376', 'name': '괴산군'},
            {'code': '4377', 'name': '음성군'},
            {'code': '4380', 'name': '단양군'},
            
            # 충청남도
            {'code': '4413', 'name': '천안시'},
            {'code': '4415', 'name': '공주시'},
            {'code': '4418', 'name': '보령시'},
            {'code': '4420', 'name': '아산시'},
            {'code': '4421', 'name': '서산시'},
            {'code': '4423', 'name': '논산시'},
            {'code': '4425', 'name': '계룡시'},
            {'code': '4427', 'name': '당진시'},
            {'code': '4471', 'name': '금산군'},
            {'code': '4476', 'name': '부여군'},
            {'code': '4477', 'name': '서천군'},
            {'code': '4479', 'name': '청양군'},
            {'code': '4480', 'name': '홍성군'},
            {'code': '4481', 'name': '예산군'},
            {'code': '44825', 'name': '태안군'},
            
            # 전라북도
            {'code': '4511', 'name': '전주시'},
            {'code': '4513', 'name': '군산시'},
            {'code': '4514', 'name': '익산시'},
            {'code': '4518', 'name': '정읍시'},
            {'code': '4519', 'name': '남원시'},
            {'code': '4521', 'name': '김제시'},
            {'code': '4571', 'name': '완주군'},
            {'code': '4572', 'name': '진안군'},
            {'code': '4573', 'name': '무주군'},
            {'code': '4574', 'name': '장수군'},
            {'code': '4575', 'name': '임실군'},
            {'code': '4577', 'name': '순창군'},
            {'code': '4579', 'name': '고창군'},
            {'code': '4580', 'name': '부안군'},
            
            # 전라남도
            {'code': '4611', 'name': '목포시'},
            {'code': '4613', 'name': '여수시'},
            {'code': '4615', 'name': '순천시'},
            {'code': '4617', 'name': '나주시'},
            {'code': '4623', 'name': '광양시'},
            {'code': '4671', 'name': '담양군'},
            {'code': '4672', 'name': '곡성군'},
            {'code': '4673', 'name': '구례군'},
            {'code': '4677', 'name': '고흥군'},
            {'code': '4678', 'name': '보성군'},
            {'code': '4679', 'name': '화순군'},
            {'code': '4680', 'name': '장흥군'},
            {'code': '4681', 'name': '강진군'},
            {'code': '4682', 'name': '해남군'},
            {'code': '4683', 'name': '영암군'},
            {'code': '4684', 'name': '무안군'},
            {'code': '4686', 'name': '함평군'},
            {'code': '4687', 'name': '영광군'},
            {'code': '4688', 'name': '장성군'},
            {'code': '4689', 'name': '완도군'},
            {'code': '4690', 'name': '진도군'},
            {'code': '4691', 'name': '신안군'},
            
            # 경상북도
            {'code': '4711', 'name': '포항시'},
            {'code': '4713', 'name': '경주시'},
            {'code': '4715', 'name': '김천시'},
            {'code': '4717', 'name': '안동시'},
            {'code': '4719', 'name': '구미시'},
            {'code': '4721', 'name': '영주시'},
            {'code': '4723', 'name': '영천시'},
            {'code': '4725', 'name': '상주시'},
            {'code': '4728', 'name': '문경시'},
            {'code': '4729', 'name': '경산시'},
            {'code': '4773', 'name': '의성군'},
            {'code': '4775', 'name': '청송군'},
            {'code': '4776', 'name': '영양군'},
            {'code': '4777', 'name': '영덕군'},
            {'code': '4782', 'name': '청도군'},
            {'code': '4783', 'name': '고령군'},
            {'code': '4784', 'name': '성주군'},
            {'code': '4785', 'name': '칠곡군'},
            {'code': '4790', 'name': '예천군'},
            {'code': '4792', 'name': '봉화군'},
            {'code': '4793', 'name': '울진군'},
            {'code': '4794', 'name': '울릉군'},
            
            # 경상남도
            {'code': '4812', 'name': '창원시'},
            {'code': '4817', 'name': '진주시'},
            {'code': '4822', 'name': '통영시'},
            {'code': '4824', 'name': '사천시'},
            {'code': '4825', 'name': '김해시'},
            {'code': '4827', 'name': '밀양시'},
            {'code': '4831', 'name': '거제시'},
            {'code': '4833', 'name': '양산시'},
            {'code': '4872', 'name': '의령군'},
            {'code': '4873', 'name': '함안군'},
            {'code': '4874', 'name': '창녕군'},
            {'code': '4882', 'name': '고성군'},
            {'code': '4884', 'name': '남해군'},
            {'code': '4885', 'name': '하동군'},
            {'code': '4886', 'name': '산청군'},
            {'code': '4887', 'name': '함양군'},
            {'code': '4888', 'name': '거창군'},
            {'code': '4889', 'name': '합천군'},
            
            # 제주특별자치도
            {'code': '5000', 'name': '제주특별자치도'},
            
            # 기타
            {'code': '9999', 'name': '한국환경공단'}
        ]
        
        # Google Sheets 설정
        self.spreadsheet_id = '1-r-TPHcy0TBAMmnytN510pKV3npE0b5M-hqQQIm3ddA'
        self.service = None
        
    def init_google_sheets(self):
        """Google Sheets API 초기화"""
        try:
            # 서비스 계정 키 파일 경로
            SERVICE_ACCOUNT_FILE = 'youtube-search-api-447606-43654b5c40cc.json'
            
            if not os.path.exists(SERVICE_ACCOUNT_FILE):
                print("❌ 서비스 계정 키 파일을 찾을 수 없습니다.")
                return False
            
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
            
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            
            self.service = build('sheets', 'v4', credentials=credentials)
            print("✅ Google Sheets API 초기화 완료")
            return True
            
        except Exception as e:
            print(f"❌ Google Sheets API 초기화 실패: {e}")
            return False
    
    def get_session_cookies(self):
        """세션 쿠키 얻기"""
        try:
            # 메인 페이지 접속
            main_response = self.session.get(f"{self.base_url}/nportal/main.do")
            
            # 구매보조금 페이지 접속
            subsidy_url = f"{self.base_url}/nportal/buySupprt/initSubsidyPaymentCheckAction.do"
            subsidy_response = self.session.get(subsidy_url)
            
            return subsidy_response.status_code == 200
            
        except Exception as e:
            print(f"❌ 세션 초기화 실패: {e}")
            return False
    
    def get_local_car_detail(self, year="2025", local_cd="1100", car_type="11", local_nm="서울특별시"):
        """특정 지역의 차량별 보조금 상세 정보 가져오기"""
        try:
            # 먼저 목록 페이지 접속 (세션 유지를 위해)
            list_url = f"{self.base_url}/nportal/buySupprt/psPopupLocalCarPirce.do"
            list_data = {
                'year1': year,
                'car_type': car_type
            }
            self.session.post(list_url, data=list_data)
            
            # 상세 페이지 요청
            url = f"{self.base_url}/nportal/buySupprt/psPopupLocalCarModelPrice.do"
            
            data = {
                'year': year,
                'local_cd': local_cd,
                'car_type': car_type,
                'local_nm': local_nm
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': list_url,
                'Origin': self.base_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.post(url, data=data, headers=headers)
            
            if response.status_code == 200:
                return response.text
            else:
                return None
                
        except Exception as e:
            return None
    
    def parse_vehicle_data(self, html_content):
        """HTML에서 차량 데이터 파싱"""
        soup = BeautifulSoup(html_content, 'html.parser')
        vehicles = []
        
        table = soup.find('table', class_='table01')
        if not table:
            table = soup.find('table')
        
        if table:
            # 헤더 분석
            headers = []
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    for th in header_row.find_all(['th', 'td']):
                        headers.append(th.get_text(strip=True))
            
            # 데이터 행 처리
            tbody = table.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        
                        if row_data[0] and '자료가 없습니다' not in ''.join(row_data):
                            vehicle = self.map_vehicle_data(headers, row_data)
                            if vehicle.get('manufacturer') and vehicle.get('model'):
                                vehicles.append(vehicle)
        
        return vehicles
    
    def map_vehicle_data(self, headers, row_data):
        """헤더와 행 데이터를 매핑하여 차량 정보 생성"""
        vehicle = {}
        
        # 인덱스 찾기
        manufacturer_idx = 0
        model_idx = 1
        detail_idx = 2
        
        for i, h in enumerate(headers):
            if '제조사' in h:
                manufacturer_idx = i
            elif '차종' in h and '모델명' not in h:
                model_idx = i
            elif '모델명' in h:
                detail_idx = i
        
        # 데이터 매핑
        if manufacturer_idx < len(row_data):
            vehicle['manufacturer'] = row_data[manufacturer_idx]
        if model_idx < len(row_data):
            vehicle['model'] = row_data[model_idx]
        if detail_idx < len(row_data) and detail_idx != model_idx:
            vehicle['model_detail'] = row_data[detail_idx]
        
        # 보조금 정보
        for i, h in enumerate(headers):
            if i < len(row_data):
                if '국비' in h and '만원' in h:
                    vehicle['national_subsidy'] = row_data[i]
                elif '지방비' in h and '만원' in h:
                    vehicle['local_subsidy'] = row_data[i]
                elif ('보조금' in h or '합계' in h) and '만원' in h and '국비' not in h and '지방비' not in h:
                    vehicle['total_subsidy'] = row_data[i]
        
        return vehicle
    
    def create_or_update_sheet(self, sheet_title):
        """시트 생성 또는 확인"""
        try:
            # 현재 스프레드시트의 모든 시트 가져오기
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheets = spreadsheet.get('sheets', [])
            sheet_exists = False
            sheet_id = None
            
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_title:
                    sheet_exists = True
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            # 시트가 없으면 생성
            if not sheet_exists:
                request = {
                    'addSheet': {
                        'properties': {
                            'title': sheet_title
                        }
                    }
                }
                
                response = self.service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={'requests': [request]}
                ).execute()
                
                sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
                print(f"   ✅ 새 시트 생성: {sheet_title}")
            
            return sheet_id
            
        except Exception as e:
            print(f"   ❌ 시트 생성/확인 실패: {e}")
            return None
    
    def get_existing_data(self, sheet_title):
        """기존 데이터 가져오기"""
        try:
            # A1:Z1000 범위의 데이터 가져오기
            range_name = f"{sheet_title}!A1:Z1000"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return {}
            
            # 헤더 확인
            headers = values[0] if values else []
            
            # 기존 데이터를 딕셔너리로 변환 (키: 제조사+모델명+상세모델)
            existing_data = {}
            for row in values[1:]:  # 헤더 제외
                if len(row) >= 3:
                    key = f"{row[0]}_{row[1]}_{row[2] if len(row) > 2 else ''}"
                    existing_data[key] = {
                        'row': row,
                        'row_index': values.index(row) + 1  # 1-based index
                    }
            
            return existing_data
            
        except HttpError as e:
            if e.resp.status == 400:  # 시트가 없는 경우
                return {}
            else:
                print(f"   ❌ 기존 데이터 가져오기 실패: {e}")
                return {}
    
    def clear_sheet_data(self, sheet_title):
        """시트 데이터 모두 삭제"""
        try:
            # 전체 데이터 삭제 (A1:Z1000)
            clear_range = f"{sheet_title}!A1:Z1000"
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=clear_range
            ).execute()
            return True
        except Exception as e:
            print(f"   ⚠️ 시트 데이터 삭제 실패: {e}")
            return False
    
    def update_sheet_data(self, sheet_title, vehicles, clear_existing=True):
        """시트 데이터 업데이트"""
        try:
            # 시트 생성 또는 확인
            sheet_id = self.create_or_update_sheet(sheet_title)
            if not sheet_id:
                return False
            
            # 매일 실행 시 기존 데이터 삭제
            if clear_existing:
                print(f"   🧯 기존 데이터 삭제 중...")
                if not self.clear_sheet_data(sheet_title):
                    print(f"   ⚠️ 데이터 삭제 실패, 계속 진행")
            
            # 기존 데이터 가져오기 (clear_existing=False일 때만)
            existing_data = {} if clear_existing else self.get_existing_data(sheet_title)
            
            # 헤더 설정
            headers = [
                '제조사', '차종', '모델명', '국비(만원)', '지방비(만원)', 
                '총보조금(만원)', '최종수정시간'
            ]
            
            # 새 데이터 준비
            new_rows = []
            update_requests = []
            
            for vehicle in vehicles:
                key = f"{vehicle.get('manufacturer', '')}_{vehicle.get('model', '')}_{vehicle.get('model_detail', '')}"
                
                row = [
                    vehicle.get('manufacturer', ''),
                    vehicle.get('model', ''),
                    vehicle.get('model_detail', ''),
                    vehicle.get('national_subsidy', ''),
                    vehicle.get('local_subsidy', ''),
                    vehicle.get('total_subsidy', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
                
                if clear_existing:
                    # 전체 새로 입력하는 경우
                    new_rows.append(row)
                    print(f"      ➕ 신규: {vehicle.get('manufacturer')} {vehicle.get('model_detail')}")
                elif key in existing_data:
                    # 기존 데이터와 비교하여 변경사항이 있는 경우만 업데이트
                    existing_row = existing_data[key]['row']
                    if row[:6] != existing_row[:6]:  # 보조금 정보가 변경된 경우
                        row_index = existing_data[key]['row_index']
                        update_requests.append({
                            'range': f"{sheet_title}!A{row_index}:G{row_index}",
                            'values': [row]
                        })
                        print(f"      📝 업데이트: {vehicle.get('manufacturer')} {vehicle.get('model_detail')}")
                    # 처리된 기존 데이터 제거
                    del existing_data[key]
                else:
                    # 새로운 데이터
                    new_rows.append(row)
                    print(f"      ➕ 신규: {vehicle.get('manufacturer')} {vehicle.get('model_detail')}")
            
            # 데이터 입력 방식 결정
            if clear_existing or not self.get_existing_data(sheet_title):
                # 전체 새로 입력 (헤더 포함)
                values = [headers] + new_rows
                range_name = f"{sheet_title}!A1"
            else:
                # 기존 데이터에 추가
                if new_rows:
                    existing_values = self.get_existing_data(sheet_title)
                    last_row = len(existing_values) + 1
                    values = new_rows
                    range_name = f"{sheet_title}!A{last_row + 1}"
                else:
                    values = []
                    range_name = None
            
            # 새 데이터 추가
            if values and range_name:
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body={'values': values}
                ).execute()
            
            # 기존 데이터 업데이트
            if update_requests:
                self.service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body={
                        'valueInputOption': 'RAW',
                        'data': update_requests
                    }
                ).execute()
            
            # 시트 포맷팅
            self.format_sheet(sheet_id)
            
            return True
            
        except Exception as e:
            print(f"   ❌ 시트 업데이트 실패: {e}")
            return False
    
    def format_sheet(self, sheet_id):
        """시트 포맷팅"""
        try:
            requests = [
                # 헤더 행 포맷
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.2,
                                    'green': 0.5,
                                    'blue': 0.8
                                },
                                'textFormat': {
                                    'foregroundColor': {
                                        'red': 1.0,
                                        'green': 1.0,
                                        'blue': 1.0
                                    },
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                },
                # 열 너비 자동 조정
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 7
                        }
                    }
                }
            ]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
        except Exception as e:
            print(f"   ⚠️ 포맷팅 실패 (무시하고 계속): {e}")
    
    def check_sheet_exists(self, sheet_title):
        """시트 존재 여부 확인"""
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheets = spreadsheet.get('sheets', [])
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_title:
                    return True
            return False
        except:
            return False
    
    def crawl_all_regions(self, year="2025", car_type="11", test_mode=False, skip_existing=True):
        """모든 지역의 보조금 데이터 크롤링"""
        print(f"🚀 전기차 보조금 전체 지역 크롤링 시작 ({year}년)...")
        print(f"📍 총 {len(self.regions)}개 지역")
        
        # 세션 초기화
        if not self.get_session_cookies():
            print("❌ 세션 초기화 실패")
            return None
        
        # Google Sheets 초기화
        if not self.init_google_sheets():
            print("❌ Google Sheets 초기화 실패")
            return None
        
        all_data = {}
        regions_to_crawl = self.regions[:5] if test_mode else self.regions
        skipped_count = 0
        
        # 각 지역별 데이터 수집
        for i, region in enumerate(regions_to_crawl):
            local_cd = region['code']
            local_nm = region['name']
            sheet_title = f"{year} {local_nm}"
            
            # 이미 처리된 지역 건너뛰기
            if skip_existing and self.check_sheet_exists(sheet_title):
                print(f"\n⏭️ [{i+1}/{len(regions_to_crawl)}] {local_nm} ({local_cd}) - 이미 처리됨")
                skipped_count += 1
                continue
            
            print(f"\n🔍 [{i+1}/{len(regions_to_crawl)}] {local_nm} ({local_cd})")
            
            # 상세 데이터 가져오기
            detail_html = self.get_local_car_detail(year, local_cd, car_type, local_nm)
            
            if detail_html:
                # 데이터 파싱
                vehicles = self.parse_vehicle_data(detail_html)
                
                if vehicles:
                    all_data[local_nm] = vehicles
                    print(f"   ✅ {len(vehicles)}개 차량 데이터 수집")
                    
                    # Google Sheets에 업로드 (매일 실행 시 기존 데이터 삭제)
                    success = self.update_sheet_data(sheet_title, vehicles, clear_existing=True)
                    
                    if success:
                        print(f"   📊 Google Sheets 업로드 완료")
                    else:
                        print(f"   ⚠️ Google Sheets 업로드 실패")
                else:
                    print(f"   ⚠️ 데이터 없음")
            else:
                print(f"   ❌ 페이지 로드 실패")
            
            # 요청 간격 (테스트 모드가 아닐 때만)
            if not test_mode and i < len(regions_to_crawl) - 1:
                time.sleep(1)
        
        if skipped_count > 0:
            print(f"\n📌 {skipped_count}개 지역 건너뜀 (이미 처리됨)")
        
        return all_data
    
    def save_results(self, data, filename=None):
        """결과를 JSON 파일로 저장"""
        if filename is None:
            filename = f"ev_subsidy_all_regions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n📁 결과 저장 완료: {filename}")
    
    def run(self, test_mode=False):
        """실행"""
        start_time = datetime.now()
        
        data = self.crawl_all_regions("2025", "11", test_mode=test_mode)
        
        if data:
            total_regions = len(data)
            total_vehicles = sum(len(vehicles) for vehicles in data.values())
            
            print(f"\n{'='*50}")
            print(f"🎉 크롤링 완료!")
            print(f"총 {total_regions}개 지역, {total_vehicles}개 차량 데이터 수집")
            print(f"소요 시간: {datetime.now() - start_time}")
            print(f"Google Sheets URL: https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}")
            print(f"{'='*50}")
            
            # 로컬 백업 저장
            self.save_results(data)
            
            return data
        else:
            print("\n❌ 데이터 수집 실패")
            return None


if __name__ == "__main__":
    import sys
    
    # 명령줄 인자로 테스트 모드 제어
    test_mode = True  # 기본값: 테스트 모드
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'full':
            test_mode = False
            print("🔥 전체 실행 모드 (228개 지역)")
        else:
            print("🧪 테스트 모드 (5개 지역)")
    else:
        print("🧪 테스트 모드 (5개 지역)")
        print("💡 전체 실행: python ev_subsidy_crawler_full.py full")
    
    crawler = EVSubsidyCrawler()
    crawler.run(test_mode=test_mode)