#!/usr/bin/env python3
"""
전체 지역 데이터 처리 - 광역시/특별시 포함
차량별 지자체 보조금 차등 적용
"""

import json
from datetime import datetime
from collections import defaultdict

# 광역시/특별시 기본 데이터 (크롤링 데이터에 없는 경우 사용)
MAJOR_CITIES_DEFAULT = {
    "서울특별시": {
        "avgSubsidy": 400,
        "maxSubsidy": 450,
        "minSubsidy": 350,
        "description": "수도권"
    },
    "부산광역시": {
        "avgSubsidy": 300,
        "maxSubsidy": 350,
        "minSubsidy": 250,
        "description": "경남권"
    },
    "대구광역시": {
        "avgSubsidy": 350,
        "maxSubsidy": 400,
        "minSubsidy": 300,
        "description": "경북권"
    },
    "인천광역시": {
        "avgSubsidy": 350,
        "maxSubsidy": 400,
        "minSubsidy": 300,
        "description": "수도권"
    },
    "광주광역시": {
        "avgSubsidy": 380,
        "maxSubsidy": 450,
        "minSubsidy": 330,
        "description": "전남권"
    },
    "대전광역시": {
        "avgSubsidy": 360,
        "maxSubsidy": 400,
        "minSubsidy": 320,
        "description": "충청권"
    },
    "울산광역시": {
        "avgSubsidy": 350,
        "maxSubsidy": 400,
        "minSubsidy": 300,
        "description": "경남권"
    },
    "세종특별자치시": {
        "avgSubsidy": 400,
        "maxSubsidy": 450,
        "minSubsidy": 350,
        "description": "충청권"
    },
    "경기도": {
        "avgSubsidy": 300,
        "maxSubsidy": 400,
        "minSubsidy": 200,
        "description": "수도권"
    },
    "강원도": {
        "avgSubsidy": 450,
        "maxSubsidy": 500,
        "minSubsidy": 400,
        "description": "강원권"
    },
    "충청북도": {
        "avgSubsidy": 400,
        "maxSubsidy": 450,
        "minSubsidy": 350,
        "description": "충청권"
    },
    "충청남도": {
        "avgSubsidy": 400,
        "maxSubsidy": 450,
        "minSubsidy": 350,
        "description": "충청권"
    },
    "전라북도": {
        "avgSubsidy": 420,
        "maxSubsidy": 500,
        "minSubsidy": 350,
        "description": "전북권"
    },
    "전라남도": {
        "avgSubsidy": 450,
        "maxSubsidy": 500,
        "minSubsidy": 400,
        "description": "전남권"
    },
    "경상북도": {
        "avgSubsidy": 400,
        "maxSubsidy": 450,
        "minSubsidy": 350,
        "description": "경북권"
    },
    "경상남도": {
        "avgSubsidy": 380,
        "maxSubsidy": 450,
        "minSubsidy": 330,
        "description": "경남권"
    }
}

def load_existing_data():
    """기존 크롤링 데이터 로드"""
    with open('ev_subsidy_all_regions_20250712_191009.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_region_category(region_name):
    """지역명에서 상위 지역 카테고리 추출"""
    if region_name.endswith('시') or region_name.endswith('군'):
        # 시/군의 경우 도 단위로 분류
        region_mapping = {
            '가평군': '경기도', '양주시': '경기도', '양평군': '경기도', 
            '여주시': '경기도', '연천군': '경기도', '포천시': '경기도',
            '천안시': '충청남도', '아산시': '충청남도', '서산시': '충청남도',
            '당진시': '충청남도', '보령시': '충청남도',
            '청주시': '충청북도', '충주시': '충청북도', '제천시': '충청북도',
            '춘천시': '강원도', '원주시': '강원도', '강릉시': '강원도',
            '창원시': '경상남도', '진주시': '경상남도', '김해시': '경상남도',
            '포항시': '경상북도', '경주시': '경상북도', '구미시': '경상북도',
            '전주시': '전라북도', '익산시': '전라북도', '군산시': '전라북도',
            '여수시': '전라남도', '순천시': '전라남도', '목포시': '전라남도',
        }
        
        for city, province in region_mapping.items():
            if city in region_name:
                return province
                
    return region_name

def process_vehicle_subsidy_by_region():
    """지역-차량별 보조금 매핑 생성"""
    raw_data = load_existing_data()
    
    # 결과 저장용 구조
    result = {
        'metadata': {
            'lastUpdated': datetime.now().isoformat(),
            'source': '환경부 전기차 보조금 데이터',
            'year': 2025
        },
        'vehicles': {},  # 차량별 정보
        'regions': {},   # 지역별 정보
        'vehicleSubsidyByRegion': defaultdict(dict)  # 지역-차량별 보조금 매핑
    }
    
    # 1. 광역시/특별시 기본 데이터 추가
    for city, data in MAJOR_CITIES_DEFAULT.items():
        result['regions'][city] = {
            'region': city,
            'avgSubsidy': data['avgSubsidy'],
            'maxSubsidy': data['maxSubsidy'],
            'minSubsidy': data['minSubsidy'],
            'description': data['description'],
            'vehicleCount': 0,
            'hasDetailData': False
        }
    
    # 2. 크롤링 데이터 처리
    all_manufacturers = set()
    
    for region, vehicles in raw_data.items():
        if not vehicles:
            continue
            
        local_subsidies = []
        vehicle_subsidies = {}
        
        for vehicle in vehicles:
            try:
                # 데이터 파싱
                manufacturer = vehicle['manufacturer']
                model = vehicle['model_detail']
                national_str = vehicle['national_subsidy'].replace(',', '')
                local_str = vehicle['local_subsidy'].replace(',', '')
                
                national = int(float(national_str))
                local = int(float(local_str))
                
                # 차량 ID 생성
                vehicle_id = f"{manufacturer}_{model}"
                
                # 차량 정보 저장
                if vehicle_id not in result['vehicles']:
                    result['vehicles'][vehicle_id] = {
                        'id': vehicle_id,
                        'manufacturer': manufacturer,
                        'model': model,
                        'category': vehicle['model'],
                        'nationalSubsidy': national
                    }
                
                # 지역-차량별 보조금 저장
                result['vehicleSubsidyByRegion'][region][vehicle_id] = local
                vehicle_subsidies[vehicle_id] = local
                
                # 제조사 추가
                all_manufacturers.add(manufacturer)
                
                # 지자체 보조금 수집
                if local > 0:
                    local_subsidies.append(local)
                    
            except Exception as e:
                print(f"데이터 처리 오류 ({region} - {vehicle.get('model_detail', 'Unknown')}): {e}")
                continue
        
        # 지역 정보 업데이트
        if local_subsidies:
            # 상위 지역 카테고리 확인
            parent_region = get_region_category(region)
            
            region_data = {
                'region': region,
                'avgSubsidy': sum(local_subsidies) // len(local_subsidies),
                'maxSubsidy': max(local_subsidies),
                'minSubsidy': min(local_subsidies),
                'vehicleCount': len(vehicles),
                'hasDetailData': True,
                'parentRegion': parent_region
            }
            
            result['regions'][region] = region_data
    
    # 3. 차량 리스트 생성
    vehicles_list = sorted(result['vehicles'].values(), 
                          key=lambda x: (x['manufacturer'], x['model']))
    
    # 4. 지역 리스트 생성 (광역시/특별시 우선, 평균 보조금 순)
    regions_list = sorted(result['regions'].values(), 
                         key=lambda x: (not x['region'] in MAJOR_CITIES_DEFAULT, 
                                      -x['avgSubsidy']))
    
    # 5. 최종 결과 구조화
    final_result = {
        'metadata': {
            **result['metadata'],
            'totalVehicles': len(vehicles_list),
            'totalManufacturers': len(all_manufacturers),
            'totalRegions': len(regions_list),
            'majorCities': len([r for r in regions_list if r['region'] in MAJOR_CITIES_DEFAULT])
        },
        'vehicles': vehicles_list,
        'manufacturers': sorted(list(all_manufacturers)),
        'regions': regions_list,
        'vehicleSubsidyByRegion': dict(result['vehicleSubsidyByRegion'])
    }
    
    return final_result

def save_processed_data():
    """처리된 데이터 저장"""
    data = process_vehicle_subsidy_by_region()
    
    # 통계 출력
    print("📊 데이터 처리 완료:")
    print(f"   - 총 차량 모델: {data['metadata']['totalVehicles']}개")
    print(f"   - 제조사: {data['metadata']['totalManufacturers']}개")
    print(f"   - 총 지역: {data['metadata']['totalRegions']}개")
    print(f"   - 광역시/특별시: {data['metadata']['majorCities']}개")
    
    # 지역별 통계
    print("\n📍 주요 지역 보조금:")
    for region in data['regions'][:10]:
        detail = "(상세데이터)" if region.get('hasDetailData', False) else "(기본값)"
        print(f"   - {region['region']}: 평균 {region['avgSubsidy']}만원 {detail}")
    
    # 전체 데이터 저장
    filename = f"ev_complete_data_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 전체 데이터: {filename}")
    
    # 웹용 경량 버전 (vehicleSubsidyByRegion 제외)
    light_data = {
        'metadata': data['metadata'],
        'vehicles': data['vehicles'],
        'manufacturers': data['manufacturers'],
        'regions': data['regions']
    }
    
    light_filename = f"ev_data_final_{datetime.now().strftime('%Y%m%d')}.json"
    with open(light_filename, 'w', encoding='utf-8') as f:
        json.dump(light_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 경량 버전: {light_filename}")

if __name__ == "__main__":
    save_processed_data()