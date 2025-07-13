import requests
from bs4 import BeautifulSoup
import json
import time
from typing import Dict, List


class RequestsEVCrawler:
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
    
    def get_session_cookies(self):
        """세션 쿠키 얻기"""
        try:
            # 1. 메인 페이지 접속
            print("📍 메인 페이지 접속 중...")
            main_response = self.session.get(f"{self.base_url}/nportal/main.do")
            print(f"   상태 코드: {main_response.status_code}")
            
            # 2. 구매보조금 지급현황 페이지 접속
            print("📍 구매보조금 지급현황 페이지 접속 중...")
            subsidy_url = f"{self.base_url}/nportal/buySupprt/initSubsidyPaymentCheckAction.do"
            subsidy_response = self.session.get(subsidy_url)
            print(f"   상태 코드: {subsidy_response.status_code}")
            
            return True
            
        except Exception as e:
            print(f"❌ 세션 초기화 실패: {e}")
            return False
    
    def get_local_car_price_list(self, year="2025", car_type="11"):
        """지자체 차종별 보조금 목록 페이지 가져오기"""
        try:
            # psPopupLocalCarPirce.do 페이지를 POST로 접속
            url = f"{self.base_url}/nportal/buySupprt/psPopupLocalCarPirce.do"
            
            # 폼 데이터 설정
            data = {
                'year1': year,
                'car_type': car_type  # 11: 승용
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f"{self.base_url}/nportal/buySupprt/initSubsidyPaymentCheckAction.do",
                'Origin': self.base_url
            }
            
            print(f"📍 지자체 보조금 목록 페이지 접속 중...")
            response = self.session.post(url, data=data, headers=headers)
            print(f"   상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                # 디버깅을 위해 HTML 저장
                with open('debug_list_page.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                return response.text
            
            return None
            
        except Exception as e:
            print(f"❌ 목록 페이지 접속 실패: {e}")
            return None
    
    def extract_regions_from_list(self, html_content):
        """목록 페이지에서 지역 정보 추출"""
        soup = BeautifulSoup(html_content, 'html.parser')
        regions = []
        
        # tbody에서 지역 정보 찾기
        tbody = soup.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 3:
                    # 첫 번째 셀: 지역명
                    local_name = cells[0].get_text(strip=True)
                    
                    # onclick 속성에서 지역 코드 추출
                    onclick_elem = row.find('a', onclick=True)
                    if onclick_elem:
                        onclick_str = onclick_elem.get('onclick', '')
                        # goLocalCarPirce('1100','11','서울특별시') 형태에서 추출
                        import re
                        match = re.search(r"goLocalCarPirce\('(\d+)'", onclick_str)
                        if match:
                            local_code = match.group(1)
                            regions.append({
                                'code': local_code,
                                'name': local_name
                            })
                            print(f"   발견: {local_name} ({local_code})")
        
        return regions
    
    def get_local_car_detail(self, year="2025", local_cd="1100", car_type="11", local_nm="서울특별시"):
        """특정 지역의 차량별 보조금 상세 정보 가져오기"""
        try:
            # psPopupLocalCarModelPrice.do로 POST 요청
            url = f"{self.base_url}/nportal/buySupprt/psPopupLocalCarModelPrice.do"
            
            data = {
                'year': year,
                'local_cd': local_cd,
                'car_type': car_type,
                'local_nm': local_nm
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': f"{self.base_url}/nportal/buySupprt/psPopupLocalCarPirce.do",
                'Origin': self.base_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            response = self.session.post(url, data=data, headers=headers)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"   ❌ 상세 페이지 응답 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"   ❌ 상세 페이지 요청 실패: {e}")
            return None
    
    def parse_vehicle_data(self, html_content):
        """HTML에서 차량 데이터 파싱"""
        soup = BeautifulSoup(html_content, 'html.parser')
        vehicles = []
        
        # 테이블 찾기
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
                        
                        # 빈 데이터나 "자료가 없습니다" 제외
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
    
    def crawl_all_regions(self, year="2025", car_type="11"):
        """모든 지역의 보조금 데이터 크롤링"""
        print("🚀 Requests 기반 전기차 보조금 크롤링 시작...")
        
        # 1. 세션 초기화
        if not self.get_session_cookies():
            return None
        
        # 2. 지역 목록 가져오기
        list_html = self.get_local_car_price_list(year, car_type)
        if not list_html:
            print("❌ 지역 목록을 가져올 수 없습니다")
            return None
        
        # 3. 지역 정보 추출
        regions = self.extract_regions_from_list(list_html)
        if not regions:
            print("⚠️ 지역 정보를 추출할 수 없습니다. 기본 지역 사용")
            regions = [
                {'code': '1100', 'name': '서울특별시'},
                {'code': '2600', 'name': '부산광역시'},
                {'code': '2700', 'name': '대구광역시'},
                {'code': '2800', 'name': '인천광역시'},
                {'code': '2900', 'name': '광주광역시'}
            ]
        
        print(f"\n📍 총 {len(regions)}개 지역 발견")
        
        all_data = {}
        
        # 4. 각 지역별 데이터 수집
        for i, region in enumerate(regions[:10]):  # 처음 10개 지역만
            local_cd = region['code']
            local_nm = region['name']
            
            print(f"\n🔍 [{i+1}/{min(len(regions), 10)}] {local_nm} ({local_cd}) 데이터 수집 중...")
            
            # 상세 데이터 가져오기
            detail_html = self.get_local_car_detail(year, local_cd, car_type, local_nm)
            
            if detail_html:
                # 데이터 파싱
                vehicles = self.parse_vehicle_data(detail_html)
                
                if vehicles:
                    all_data[local_nm] = vehicles
                    print(f"   ✅ {len(vehicles)}개 차량 데이터 수집 완료")
                    # 샘플 출력
                    for v in vehicles[:2]:
                        print(f"      - {v.get('manufacturer')} {v.get('model_detail', v.get('model'))}: {v.get('total_subsidy', 'N/A')}만원")
                else:
                    print(f"   ⚠️ 데이터 없음")
            else:
                print(f"   ❌ 페이지 로드 실패")
            
            # 요청 간격
            time.sleep(1)
        
        return all_data
    
    def save_results(self, data, filename="ev_subsidy_requests.json"):
        """결과 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n📁 결과 저장 완료: {filename}")
    
    def run(self):
        """실행"""
        data = self.crawl_all_regions("2025", "11")
        
        if data:
            total_count = sum(len(vehicles) for vehicles in data.values())
            print(f"\n🎉 크롤링 완료!")
            print(f"총 {len(data)}개 지역, {total_count}개 차량 데이터 수집")
            
            # 결과 저장
            self.save_results(data)
            
            return data
        else:
            print("\n❌ 데이터 수집 실패")
            return None


if __name__ == "__main__":
    crawler = RequestsEVCrawler()
    crawler.run()