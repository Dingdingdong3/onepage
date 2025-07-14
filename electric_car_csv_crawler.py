import requests
from bs4 import BeautifulSoup
import json
import time
import os
import pandas as pd
from typing import Dict, List
from datetime import datetime


class RequestsEVCrawler:
    def __init__(self, target_year=None):
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

        # 크롤링 대상 연도 설정 (기본값은 현재 연도)
        self.target_year = target_year if target_year else datetime.now().year

        # csv 폴더 생성
        self.csv_folder = "csv"
        if not os.path.exists(self.csv_folder):
            os.makedirs(self.csv_folder)
            print(f"📁 '{self.csv_folder}' 폴더를 생성했습니다.")

        # 기존 파일 정리
        self.cleanup_old_files()

    def cleanup_old_files(self):
        """기존 대상 연도 파일들 삭제"""
        try:
            # 대상 연도 파일명 패턴
            target_csv_pattern = f"{self.target_year}.csv"
            target_json_pattern = f"{self.target_year}.json"

            print(f"🧹 기존 {self.target_year}년 파일 정리 중...")

            deleted_files = []

            # csv 폴더 내 파일들 확인
            for filename in os.listdir(self.csv_folder):
                filepath = os.path.join(self.csv_folder, filename)

                # 대상 연도 CSV 파일 삭제
                if filename == target_csv_pattern:
                    os.remove(filepath)
                    deleted_files.append(filename)
                    print(f"   🗑️ 삭제: {filename}")

                # 대상 연도 JSON 파일 삭제
                elif filename == target_json_pattern:
                    os.remove(filepath)
                    deleted_files.append(filename)
                    print(f"   🗑️ 삭제: {filename}")

            if deleted_files:
                print(f"   ✅ 총 {len(deleted_files)}개 파일 정리 완료")
            else:
                print(f"   ℹ️ 삭제할 기존 {self.target_year}년 파일이 없습니다")

        except Exception as e:
            print(f"⚠️ 파일 정리 중 오류: {e}")

    def get_target_filename(self, file_type="csv"):
        """대상 연도 기준 파일명 생성"""
        if file_type == "csv":
            return f"{self.target_year}.csv"
        elif file_type == "json":
            return f"{self.target_year}.json"
        else:
            return f"{self.target_year}.csv"

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

    def get_all_regions(self):
        """전국 모든 지역 정보를 체계적으로 반환"""
        regions = []

        # 1. 서울특별시
        regions.extend([
            {'code': '1100', 'name': '서울특별시', 'category': '특별시'}
        ])

        # 2. 수도권 (경기도)
        gyeonggi_regions = [
            {'code': '4111', 'name': '수원시', 'category': '경기도'},
            {'code': '4113', 'name': '성남시', 'category': '경기도'},
            {'code': '4115', 'name': '의정부시', 'category': '경기도'},
            {'code': '4117', 'name': '안양시', 'category': '경기도'},
            {'code': '4119', 'name': '부천시', 'category': '경기도'},
            {'code': '4121', 'name': '광명시', 'category': '경기도'},
            {'code': '4122', 'name': '평택시', 'category': '경기도'},
            {'code': '4125', 'name': '동두천시', 'category': '경기도'},
            {'code': '4127', 'name': '안산시', 'category': '경기도'},
            {'code': '4128', 'name': '고양시', 'category': '경기도'},
            {'code': '4129', 'name': '과천시', 'category': '경기도'},
            {'code': '4131', 'name': '구리시', 'category': '경기도'},
            {'code': '4136', 'name': '남양주시', 'category': '경기도'},
            {'code': '4137', 'name': '오산시', 'category': '경기도'},
            {'code': '4139', 'name': '시흥시', 'category': '경기도'},
            {'code': '4141', 'name': '군포시', 'category': '경기도'},
            {'code': '4143', 'name': '의왕시', 'category': '경기도'},
            {'code': '4145', 'name': '하남시', 'category': '경기도'},
            {'code': '4146', 'name': '용인시', 'category': '경기도'},
            {'code': '4148', 'name': '파주시', 'category': '경기도'},
            {'code': '4150', 'name': '이천시', 'category': '경기도'},
            {'code': '4155', 'name': '안성시', 'category': '경기도'},
            {'code': '4157', 'name': '김포시', 'category': '경기도'},
            {'code': '4159', 'name': '화성시', 'category': '경기도'},
            {'code': '4161', 'name': '광주시', 'category': '경기도'},
            {'code': '4163', 'name': '양주시', 'category': '경기도'},
            {'code': '4165', 'name': '포천시', 'category': '경기도'},
            {'code': '4167', 'name': '여주시', 'category': '경기도'},
            {'code': '4180', 'name': '연천군', 'category': '경기도'},
            {'code': '4182', 'name': '가평군', 'category': '경기도'},
            {'code': '4183', 'name': '양평군', 'category': '경기도'}
        ]
        regions.extend(gyeonggi_regions)

        # 3. 인천광역시
        regions.extend([
            {'code': '2800', 'name': '인천광역시', 'category': '광역시'}
        ])

        # 4. 광역시들
        metro_cities = [
            {'code': '2600', 'name': '부산광역시', 'category': '광역시'},
            {'code': '2700', 'name': '대구광역시', 'category': '광역시'},
            {'code': '2900', 'name': '광주광역시', 'category': '광역시'},
            {'code': '3000', 'name': '대전광역시', 'category': '광역시'},
            {'code': '3100', 'name': '울산광역시', 'category': '광역시'}
        ]
        regions.extend(metro_cities)

        # 5. 세종특별자치시
        regions.extend([
            {'code': '3611', 'name': '세종특별자치시', 'category': '특별자치시'}
        ])

        # 6. 강원도
        gangwon_regions = [
            {'code': '4211', 'name': '춘천시', 'category': '강원도'},
            {'code': '4213', 'name': '원주시', 'category': '강원도'},
            {'code': '4215', 'name': '강릉시', 'category': '강원도'},
            {'code': '4217', 'name': '동해시', 'category': '강원도'},
            {'code': '4219', 'name': '태백시', 'category': '강원도'},
            {'code': '4221', 'name': '속초시', 'category': '강원도'},
            {'code': '4223', 'name': '삼척시', 'category': '강원도'},
            {'code': '4272', 'name': '홍천군', 'category': '강원도'},
            {'code': '4273', 'name': '횡성군', 'category': '강원도'},
            {'code': '4275', 'name': '영월군', 'category': '강원도'},
            {'code': '4276', 'name': '평창군', 'category': '강원도'},
            {'code': '4277', 'name': '정선군', 'category': '강원도'},
            {'code': '4278', 'name': '철원군', 'category': '강원도'},
            {'code': '4279', 'name': '화천군', 'category': '강원도'},
            {'code': '4280', 'name': '양구군', 'category': '강원도'},
            {'code': '4281', 'name': '인제군', 'category': '강원도'},
            {'code': '4282', 'name': '고성군', 'category': '강원도'},
            {'code': '4283', 'name': '양양군', 'category': '강원도'}
        ]
        regions.extend(gangwon_regions)

        # 7. 충청북도
        chungbuk_regions = [
            {'code': '4311', 'name': '청주시', 'category': '충청북도'},
            {'code': '4313', 'name': '충주시', 'category': '충청북도'},
            {'code': '4315', 'name': '제천시', 'category': '충청북도'},
            {'code': '4372', 'name': '보은군', 'category': '충청북도'},
            {'code': '4373', 'name': '옥천군', 'category': '충청북도'},
            {'code': '43745', 'name': '증평군', 'category': '충청북도'},
            {'code': '4374', 'name': '영동군', 'category': '충청북도'},
            {'code': '4375', 'name': '진천군', 'category': '충청북도'},
            {'code': '4376', 'name': '괴산군', 'category': '충청북도'},
            {'code': '4377', 'name': '음성군', 'category': '충청북도'},
            {'code': '4380', 'name': '단양군', 'category': '충청북도'}
        ]
        regions.extend(chungbuk_regions)

        # 8. 충청남도
        chungnam_regions = [
            {'code': '4413', 'name': '천안시', 'category': '충청남도'},
            {'code': '4415', 'name': '공주시', 'category': '충청남도'},
            {'code': '4418', 'name': '보령시', 'category': '충청남도'},
            {'code': '4420', 'name': '아산시', 'category': '충청남도'},
            {'code': '4421', 'name': '서산시', 'category': '충청남도'},
            {'code': '4423', 'name': '논산시', 'category': '충청남도'},
            {'code': '4425', 'name': '계룡시', 'category': '충청남도'},
            {'code': '4427', 'name': '당진시', 'category': '충청남도'},
            {'code': '4471', 'name': '금산군', 'category': '충청남도'},
            {'code': '4476', 'name': '부여군', 'category': '충청남도'},
            {'code': '4477', 'name': '서천군', 'category': '충청남도'},
            {'code': '4479', 'name': '청양군', 'category': '충청남도'},
            {'code': '4480', 'name': '홍성군', 'category': '충청남도'},
            {'code': '4481', 'name': '예산군', 'category': '충청남도'},
            {'code': '44825', 'name': '태안군', 'category': '충청남도'}
        ]
        regions.extend(chungnam_regions)

        # 9. 전라북도
        jeonbuk_regions = [
            {'code': '4511', 'name': '전주시', 'category': '전라북도'},
            {'code': '4513', 'name': '군산시', 'category': '전라북도'},
            {'code': '4514', 'name': '익산시', 'category': '전라북도'},
            {'code': '4518', 'name': '정읍시', 'category': '전라북도'},
            {'code': '4519', 'name': '남원시', 'category': '전라북도'},
            {'code': '4521', 'name': '김제시', 'category': '전라북도'},
            {'code': '4571', 'name': '완주군', 'category': '전라북도'},
            {'code': '4572', 'name': '진안군', 'category': '전라북도'},
            {'code': '4573', 'name': '무주군', 'category': '전라북도'},
            {'code': '4574', 'name': '장수군', 'category': '전라북도'},
            {'code': '4575', 'name': '임실군', 'category': '전라북도'},
            {'code': '4577', 'name': '순창군', 'category': '전라북도'},
            {'code': '4579', 'name': '고창군', 'category': '전라북도'},
            {'code': '4580', 'name': '부안군', 'category': '전라북도'}
        ]
        regions.extend(jeonbuk_regions)

        # 10. 전라남도
        jeonnam_regions = [
            {'code': '4611', 'name': '목포시', 'category': '전라남도'},
            {'code': '4613', 'name': '여수시', 'category': '전라남도'},
            {'code': '4615', 'name': '순천시', 'category': '전라남도'},
            {'code': '4617', 'name': '나주시', 'category': '전라남도'},
            {'code': '4623', 'name': '광양시', 'category': '전라남도'},
            {'code': '4671', 'name': '담양군', 'category': '전라남도'},
            {'code': '4672', 'name': '곡성군', 'category': '전라남도'},
            {'code': '4673', 'name': '구례군', 'category': '전라남도'},
            {'code': '4677', 'name': '고흥군', 'category': '전라남도'},
            {'code': '4678', 'name': '보성군', 'category': '전라남도'},
            {'code': '4679', 'name': '화순군', 'category': '전라남도'},
            {'code': '4680', 'name': '장흥군', 'category': '전라남도'},
            {'code': '4681', 'name': '강진군', 'category': '전라남도'},
            {'code': '4682', 'name': '해남군', 'category': '전라남도'},
            {'code': '4683', 'name': '영암군', 'category': '전라남도'},
            {'code': '4684', 'name': '무안군', 'category': '전라남도'},
            {'code': '4686', 'name': '함평군', 'category': '전라남도'},
            {'code': '4687', 'name': '영광군', 'category': '전라남도'},
            {'code': '4688', 'name': '장성군', 'category': '전라남도'},
            {'code': '4689', 'name': '완도군', 'category': '전라남도'},
            {'code': '4690', 'name': '진도군', 'category': '전라남도'},
            {'code': '4691', 'name': '신안군', 'category': '전라남도'}
        ]
        regions.extend(jeonnam_regions)

        # 11. 경상북도
        gyeongbuk_regions = [
            {'code': '4711', 'name': '포항시', 'category': '경상북도'},
            {'code': '4713', 'name': '경주시', 'category': '경상북도'},
            {'code': '4715', 'name': '김천시', 'category': '경상북도'},
            {'code': '4717', 'name': '안동시', 'category': '경상북도'},
            {'code': '4719', 'name': '구미시', 'category': '경상북도'},
            {'code': '4721', 'name': '영주시', 'category': '경상북도'},
            {'code': '4723', 'name': '영천시', 'category': '경상북도'},
            {'code': '4725', 'name': '상주시', 'category': '경상북도'},
            {'code': '4728', 'name': '문경시', 'category': '경상북도'},
            {'code': '4729', 'name': '경산시', 'category': '경상북도'},
            {'code': '4773', 'name': '의성군', 'category': '경상북도'},
            {'code': '4775', 'name': '청송군', 'category': '경상북도'},
            {'code': '4776', 'name': '영양군', 'category': '경상북도'},
            {'code': '4777', 'name': '영덕군', 'category': '경상북도'},
            {'code': '4782', 'name': '청도군', 'category': '경상북도'},
            {'code': '4783', 'name': '고령군', 'category': '경상북도'},
            {'code': '4784', 'name': '성주군', 'category': '경상북도'},
            {'code': '4785', 'name': '칠곡군', 'category': '경상북도'},
            {'code': '4790', 'name': '예천군', 'category': '경상북도'},
            {'code': '4792', 'name': '봉화군', 'category': '경상북도'},
            {'code': '4793', 'name': '울진군', 'category': '경상북도'},
            {'code': '4794', 'name': '울릉군', 'category': '경상북도'}
        ]
        regions.extend(gyeongbuk_regions)

        # 12. 경상남도
        gyeongnam_regions = [
            {'code': '4812', 'name': '창원시', 'category': '경상남도'},
            {'code': '4817', 'name': '진주시', 'category': '경상남도'},
            {'code': '4822', 'name': '통영시', 'category': '경상남도'},
            {'code': '4824', 'name': '사천시', 'category': '경상남도'},
            {'code': '4825', 'name': '김해시', 'category': '경상남도'},
            {'code': '4827', 'name': '밀양시', 'category': '경상남도'},
            {'code': '4831', 'name': '거제시', 'category': '경상남도'},
            {'code': '4833', 'name': '양산시', 'category': '경상남도'},
            {'code': '4872', 'name': '의령군', 'category': '경상남도'},
            {'code': '4873', 'name': '함안군', 'category': '경상남도'},
            {'code': '4874', 'name': '창녕군', 'category': '경상남도'},
            {'code': '4882', 'name': '고성군', 'category': '경상남도'},
            {'code': '4884', 'name': '남해군', 'category': '경상남도'},
            {'code': '4885', 'name': '하동군', 'category': '경상남도'},
            {'code': '4886', 'name': '산청군', 'category': '경상남도'},
            {'code': '4887', 'name': '함양군', 'category': '경상남도'},
            {'code': '4888', 'name': '거창군', 'category': '경상남도'},
            {'code': '4889', 'name': '합천군', 'category': '경상남도'}
        ]
        regions.extend(gyeongnam_regions)

        # 13. 제주특별자치도
        regions.extend([
            {'code': '5000', 'name': '제주특별자치도', 'category': '특별자치도'}
        ])

        # 14. 기타
        regions.extend([
            {'code': '9999', 'name': '한국환경공단', 'category': '기타'}
        ])

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

    def save_all_data_to_csv(self, all_data, filename=None):
        """모든 지역 데이터를 하나의 CSV 파일로 저장"""
        if not all_data:
            print("❌ 저장할 데이터가 없습니다.")
            return

        # 파일명이 지정되지 않으면 대상 연도로 생성
        if filename is None:
            filename = self.get_target_filename("csv")

        filepath = os.path.join(self.csv_folder, filename)
        all_vehicles = []

        try:
            # 지역 정보와 카테고리 매핑
            region_category_map = {}
            for region in self.get_all_regions():
                region_category_map[region['name']] = region['category']

            # 모든 지역의 데이터를 하나로 합치기
            for region_name, vehicles in all_data.items():
                for vehicle in vehicles:
                    # 각 차량 데이터에 지역 정보와 광역시도 정보 추가
                    vehicle_with_region = vehicle.copy()
                    vehicle_with_region['region'] = region_name
                    vehicle_with_region['category'] = region_category_map.get(region_name, '기타')
                    all_vehicles.append(vehicle_with_region)

            if not all_vehicles:
                print("❌ 통합할 차량 데이터가 없습니다.")
                return

            # DataFrame 생성
            df = pd.DataFrame(all_vehicles)

            # 크롤링 시점 정보 추가
            crawl_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            df['crawl_date'] = crawl_datetime
            df['data_year'] = self.target_year

            # 컬럼 순서 정리
            column_order = ['data_year', 'region', 'category', 'manufacturer', 'model', 'model_detail',
                            'national_subsidy', 'local_subsidy', 'total_subsidy', 'crawl_date']
            existing_columns = [col for col in column_order if col in df.columns]
            other_columns = [col for col in df.columns if col not in column_order]
            final_columns = existing_columns + other_columns

            df = df[final_columns]

            # 컬럼명 한국어로 변경
            column_mapping = {
                'data_year': '데이터연도',
                'region': '지역',
                'category': '광역시도',
                'manufacturer': '제조사',
                'model': '차종',
                'model_detail': '모델명',
                'national_subsidy': '국비보조금(만원)',
                'local_subsidy': '지방비보조금(만원)',
                'total_subsidy': '총보조금(만원)',
                'crawl_date': '수집일시'
            }

            df = df.rename(columns=column_mapping)

            # 의도한 순서로 정렬하기 위한 순서 매핑
            category_order = {
                '특별시': 1,
                '경기도': 2,
                '광역시': 3,
                '특별자치시': 4,
                '강원도': 5,
                '충청북도': 6,
                '충청남도': 7,
                '전라북도': 8,
                '전라남도': 9,
                '경상북도': 10,
                '경상남도': 11,
                '특별자치도': 12,
                '기타': 13
            }

            # 정렬용 컬럼 추가
            df['category_order'] = df['광역시도'].map(category_order).fillna(999)

            # 의도한 순서대로 정렬: 광역시도 순서 > 지역 > 제조사 > 차종
            df = df.sort_values(['category_order', '지역', '제조사', '차종'], na_position='last')

            # 정렬용 컬럼 제거
            df = df.drop('category_order', axis=1)

            # CSV 저장
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"\n📊 통합 CSV 저장 완료: {filename}")
            print(f"   - 데이터 연도: {self.target_year}년")
            print(f"   - 총 {len(all_data)}개 지역, {len(all_vehicles)}개 차량 데이터")
            print(f"   - 수집 시점: {crawl_datetime}")
            print(f"   - 파일 위치: {filepath}")
            print(f"   - 정렬 순서: 서울 → 경기도 → 광역시 → 기타 순")

            return filepath

        except Exception as e:
            print(f"❌ 통합 CSV 저장 실패: {e}")
            return None

    def crawl_all_regions(self, year=None, car_type="11"):
        """모든 지역의 보조금 데이터 크롤링"""
        # 연도가 지정되지 않으면 대상 연도 사용
        if year is None:
            year = str(self.target_year)

        print(f"🚀 {year}년 전국 전기차 보조금 크롤링 시작...")

        # 1. 세션 초기화
        if not self.get_session_cookies():
            return None

        # 2. 전체 지역 목록 가져오기 (내장된 지역 리스트 사용)
        regions = self.get_all_regions()
        print(f"\n📍 총 {len(regions)}개 지역 크롤링 시도 예정")

        # 지역 카테고리별 개수 출력
        category_counts = {}
        for region in regions:
            category = region['category']
            category_counts[category] = category_counts.get(category, 0) + 1

        print("\n📊 지역별 분포:")
        for category, count in category_counts.items():
            print(f"   {category}: {count}개 지역")

        all_data = {}
        success_count = 0
        fail_count = 0
        no_data_count = 0

        # 3. 각 지역별 데이터 수집
        for i, region in enumerate(regions):
            local_cd = region['code']
            local_nm = region['name']
            category = region['category']

            print(f"\n🔍 [{i + 1}/{len(regions)}] {category} > {local_nm} ({local_cd}) 크롤링 중...")

            # 상세 데이터 가져오기
            detail_html = self.get_local_car_detail(year, local_cd, car_type, local_nm)

            if detail_html:
                # 데이터 파싱
                vehicles = self.parse_vehicle_data(detail_html)

                if vehicles:
                    all_data[local_nm] = vehicles
                    success_count += 1
                    print(f"   ✅ {len(vehicles)}개 차량 데이터 수집 완료")

                    # 샘플 출력 (처음 2개만)
                    for j, v in enumerate(vehicles[:2]):
                        manufacturer = v.get('manufacturer', 'N/A')
                        model = v.get('model_detail', v.get('model', 'N/A'))
                        subsidy = v.get('total_subsidy', 'N/A')
                        print(f"      [{j + 1}] {manufacturer} {model}: {subsidy}만원")
                else:
                    print(f"   ⚠️ 데이터 없음 (해당 지역 보조금 정보 없음)")
                    no_data_count += 1
            else:
                print(f"   ❌ 페이지 로드 실패 (지역 존재하지 않거나 접근 불가)")
                fail_count += 1

            # 요청 간격 (서버 부하 방지)
            time.sleep(0.5)

            # 진행상황 중간 보고 (매 50개 지역마다)
            if (i + 1) % 50 == 0:
                print(f"\n📈 진행상황: {i + 1}/{len(regions)} 시도 완료")
                print(f"   ✅ 데이터 수집 성공: {success_count}개 지역")
                print(f"   ⚠️ 데이터 없음: {no_data_count}개 지역")
                print(f"   ❌ 접근 실패: {fail_count}개 지역")

        print(f"\n{'=' * 80}")
        print(f"🎯 크롤링 완료 요약")
        print(f"{'=' * 80}")
        print(f"📊 총 시도: {len(regions)}개 지역")
        print(f"✅ 데이터 수집 성공: {success_count}개 지역")
        print(f"⚠️ 데이터 없음: {no_data_count}개 지역")
        print(f"❌ 접근 실패: {fail_count}개 지역")
        if success_count > 0:
            print(f"📈 실제 데이터 보유 지역: {success_count}개")
            print(f"📊 평균 성공률: {success_count / (success_count + no_data_count + fail_count) * 100:.1f}%")

        return all_data

    def save_summary_json(self, data, filename=None):
        """전체 요약 JSON 파일 저장"""
        if filename is None:
            filename = self.get_target_filename("json")

        filepath = os.path.join(self.csv_folder, filename)

        # 메타데이터 추가
        summary_data = {
            "crawl_info": {
                "crawl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_year": self.target_year,
                "total_regions": len(data),
                "total_vehicles": sum(len(vehicles) for vehicles in data.values())
            },
            "data": data
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        print(f"📁 전체 요약 JSON 저장 완료: {filename}")

    def run(self):
        """실행"""
        print("=" * 70)
        print(f"🚗 {self.target_year}년 전국 전기차 보조금 크롤링 시작")
        print("=" * 70)

        data = self.crawl_all_regions()

        if data:
            total_count = sum(len(vehicles) for vehicles in data.values())
            print(f"\n🎉 데이터 수집 완료!")
            print(f"📊 실제 수집: {len(data)}개 지역, {total_count}개 차량 데이터")

            # 통합 CSV 파일로 저장
            csv_file = self.save_all_data_to_csv(data)

            # 요약 JSON도 함께 저장
            self.save_summary_json(data)

            # 결과 미리보기
            if csv_file:
                self.preview_csv_data(csv_file)

            return data
        else:
            print("\n❌ 수집된 데이터가 없습니다.")
            return None

    def preview_csv_data(self, csv_file):
        """CSV 파일 미리보기"""
        try:
            print(f"\n{'=' * 60}")
            print("📄 생성된 CSV 파일 미리보기")
            print(f"{'=' * 60}")

            df = pd.read_csv(csv_file)

            print(f"📋 총 행 수: {len(df)}")
            print(f"📋 총 열 수: {len(df.columns)}")
            print(f"📋 컬럼: {', '.join(df.columns.tolist())}")

            print(f"\n🏛️ 광역시도별 지역 수:")
            category_counts = df['광역시도'].value_counts()
            for category, count in category_counts.items():
                print(f"   {category}: {count}개 데이터")

            print(f"\n🏙️ 상위 10개 지역별 차량 수:")
            region_counts = df['지역'].value_counts()
            for region, count in region_counts.head(10).items():
                print(f"   {region}: {count}대")
            if len(region_counts) > 10:
                print(f"   ... 외 {len(region_counts) - 10}개 지역")

            print(f"\n🚙 제조사별 차량 수:")
            if '제조사' in df.columns:
                manufacturer_counts = df['제조사'].value_counts()
                for manufacturer, count in manufacturer_counts.head(5).items():
                    print(f"   {manufacturer}: {count}대")

            print(f"\n📋 상위 5개 데이터 샘플:")
            print(df.head().to_string(index=False))

            print(f"\n✅ CSV 파일 경로: {csv_file}")
            print(f"💡 서버에서 {self.get_current_filename('csv')} 파일을 사용하세요!")
            print(f"📅 파일은 매일 실행 시 자동으로 갱신됩니다.")

        except Exception as e:
            print(f"❌ CSV 미리보기 실패: {e}")


if __name__ == "__main__":
    crawler = RequestsEVCrawler()
    crawler.run()