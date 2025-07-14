#!/usr/bin/env python3
"""
Google Sheets 일일 업데이트 스크립트
API 할당량을 고려한 효율적인 데이터 수집
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from collections import defaultdict
import schedule

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sheets_updater.log'),
        logging.StreamHandler()
    ]
)

class GoogleSheetsOptimizedUpdater:
    def __init__(self):
        self.spreadsheet_id = os.getenv('GOOGLE_SPREADSHEET_ID')
        self.service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))
        self.request_delay_ms = int(os.getenv('REQUEST_DELAY_MS', 1000))
        
        # API 요청 카운터
        self.request_count = 0
        self.request_start_time = time.time()
        
        # 인증 설정
        self.setup_authentication()
        
    def setup_authentication(self):
        """Google Sheets 인증 설정"""
        try:
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            
            credentials = Credentials.from_service_account_file(
                self.service_account_file,
                scopes=scope
            )
            
            self.gc = gspread.authorize(credentials)
            self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            
            logging.info(f"✅ 스프레드시트 연결 성공: {self.spreadsheet.title}")
            
        except Exception as e:
            logging.error(f"❌ 인증 실패: {e}")
            raise
    
    def rate_limit(self):
        """API 요청 속도 제한"""
        self.request_count += 1
        
        # 1분이 지났으면 카운터 리셋
        current_time = time.time()
        if current_time - self.request_start_time >= 60:
            self.request_count = 1
            self.request_start_time = current_time
        
        # 분당 요청 제한 확인
        if self.request_count >= self.max_requests_per_minute:
            sleep_time = 60 - (current_time - self.request_start_time)
            if sleep_time > 0:
                logging.info(f"⏳ API 제한 대기: {sleep_time:.1f}초")
                time.sleep(sleep_time)
                self.request_count = 1
                self.request_start_time = time.time()
        
        # 요청 간 지연
        time.sleep(self.request_delay_ms / 1000)
    
    def get_all_sheets(self):
        """모든 시트 목록 가져오기"""
        self.rate_limit()
        sheets = self.spreadsheet.worksheets()
        return [sheet.title for sheet in sheets if sheet.title.startswith('2025')]
    
    def update_vehicle_data_batch(self, sheet_name, vehicles_data):
        """차량 데이터 일괄 업데이트 (API 호출 최소화)"""
        try:
            self.rate_limit()
            worksheet = self.spreadsheet.worksheet(sheet_name)
            
            # 헤더 확인
            headers = ['제조사', '차종', '차량명', '국고보조금', '지방비', '보조금계', '차량종류']
            
            # 데이터 준비 (헤더 포함)
            rows = [headers]
            for vehicle in vehicles_data:
                row = [
                    vehicle.get('manufacturer', ''),
                    vehicle.get('model', ''),
                    vehicle.get('model_detail', ''),
                    str(vehicle.get('national_subsidy', 0)),
                    str(vehicle.get('local_subsidy', 0)),
                    str(vehicle.get('total_subsidy', 0)),
                    vehicle.get('category', '')
                ]
                rows.append(row)
            
            # 시트 크기 조정
            worksheet.resize(rows=len(rows), cols=len(headers))
            
            # 일괄 업데이트 (단일 API 호출)
            self.rate_limit()
            worksheet.update(f'A1:G{len(rows)}', rows, value_input_option='RAW')
            
            logging.info(f"✅ {sheet_name}: {len(vehicles_data)}개 차량 데이터 업데이트 완료")
            
        except Exception as e:
            logging.error(f"❌ {sheet_name} 업데이트 실패: {e}")
    
    def create_summary_sheet(self):
        """요약 시트 생성/업데이트"""
        try:
            # 요약 시트 확인/생성
            try:
                summary = self.spreadsheet.worksheet('요약')
            except:
                self.rate_limit()
                summary = self.spreadsheet.add_worksheet(title='요약', rows=200, cols=10)
            
            # 지역별 통계 계산
            all_regions = self.get_all_sheets()
            summary_data = [['지역', '차량수', '평균 국고보조금', '평균 지방비', '최대 지방비', '최소 지방비', '업데이트 시간']]
            
            for region in all_regions[:10]:  # API 제한을 위해 처음 10개만
                try:
                    self.rate_limit()
                    worksheet = self.spreadsheet.worksheet(region)
                    values = worksheet.get_all_values()[1:]  # 헤더 제외
                    
                    if values:
                        national_subsidies = [int(row[3]) for row in values if row[3].isdigit()]
                        local_subsidies = [int(row[4]) for row in values if row[4].isdigit()]
                        
                        summary_row = [
                            region.replace('2025 ', ''),
                            len(values),
                            sum(national_subsidies) // len(national_subsidies) if national_subsidies else 0,
                            sum(local_subsidies) // len(local_subsidies) if local_subsidies else 0,
                            max(local_subsidies) if local_subsidies else 0,
                            min(local_subsidies) if local_subsidies else 0,
                            datetime.now().strftime('%Y-%m-%d %H:%M')
                        ]
                        summary_data.append(summary_row)
                    
                except Exception as e:
                    logging.warning(f"⚠️ {region} 통계 수집 실패: {e}")
            
            # 요약 데이터 업데이트
            self.rate_limit()
            summary.clear()
            summary.update('A1:G' + str(len(summary_data)), summary_data)
            
            logging.info("✅ 요약 시트 업데이트 완료")
            
        except Exception as e:
            logging.error(f"❌ 요약 시트 생성 실패: {e}")
    
    def daily_update(self):
        """일일 업데이트 작업"""
        logging.info("🔄 일일 업데이트 시작...")
        start_time = time.time()
        
        try:
            # 1. 기존 크롤링 데이터 로드
            with open('ev_subsidy_all_regions_20250712_191009.json', 'r', encoding='utf-8') as f:
                crawled_data = json.load(f)
            
            # 2. 지역별로 순차적으로 업데이트 (API 제한 고려)
            regions_to_update = list(crawled_data.keys())[:5]  # 하루에 5개 지역씩
            
            for region in regions_to_update:
                if region in crawled_data and crawled_data[region]:
                    sheet_name = f'2025 {region}'
                    
                    # 시트 존재 확인
                    try:
                        self.spreadsheet.worksheet(sheet_name)
                    except:
                        # 시트 생성
                        self.rate_limit()
                        self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
                    
                    # 데이터 업데이트
                    self.update_vehicle_data_batch(sheet_name, crawled_data[region])
                    
                    # 진행 상황 저장
                    self.save_progress(region)
            
            # 3. 요약 시트 업데이트
            self.create_summary_sheet()
            
            elapsed_time = time.time() - start_time
            logging.info(f"✅ 일일 업데이트 완료 (소요시간: {elapsed_time:.1f}초)")
            
        except Exception as e:
            logging.error(f"❌ 일일 업데이트 실패: {e}")
    
    def save_progress(self, last_updated_region):
        """진행 상황 저장"""
        progress = {
            'last_updated': datetime.now().isoformat(),
            'last_region': last_updated_region
        }
        
        with open('.update_progress.json', 'w') as f:
            json.dump(progress, f)
    
    def load_progress(self):
        """진행 상황 로드"""
        try:
            with open('.update_progress.json', 'r') as f:
                return json.load(f)
        except:
            return None

def main():
    """메인 실행 함수"""
    updater = GoogleSheetsOptimizedUpdater()
    
    # 즉시 실행 옵션
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--now':
        updater.daily_update()
        return
    
    # 스케줄 설정 (매일 새벽 2시)
    schedule.every().day.at("02:00").do(updater.daily_update)
    
    logging.info("📅 스케줄러 시작 - 매일 02:00 업데이트 예정")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 확인

if __name__ == "__main__":
    main()