#!/usr/bin/env python3
"""
전체 지역의 차량 및 지자체 보조금 데이터 처리
Google Sheets의 지방비(지자체 보조금) 데이터 통합
"""

import json
from datetime import datetime
from collections import defaultdict

def load_existing_json():
    """기존 크롤링된 JSON 데이터 로드"""
    with open('ev_subsidy_all_regions_20250712_191009.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def process_all_regions_data():
    """모든 지역의 데이터를 처리하여 통합된 구조로 변환"""
    
    # 기존 데이터 로드
    raw_data = load_existing_json()
    
    # 전체 차량 목록 (중복 제거)
    all_vehicles = {}
    
    # 지역별 보조금 정보
    region_subsidies = {}
    
    # 제조사별 모델 정리
    manufacturer_models = defaultdict(set)
    
    # 각 지역 데이터 처리
    for region, vehicles in raw_data.items():
        if not vehicles:
            continue
            
        # 지역별 지자체 보조금 평균 계산
        local_subsidies = []
        
        for vehicle in vehicles:
            # 차량 정보 정리
            manufacturer = vehicle['manufacturer']
            model_detail = vehicle['model_detail']
            # 콤마와 소수점 처리
            national_str = vehicle['national_subsidy'].replace(',', '')
            local_str = vehicle['local_subsidy'].replace(',', '')
            
            national = int(float(national_str))
            local = int(float(local_str))  # 지방비 = 지자체 보조금
            
            # 차량 고유 ID 생성
            vehicle_id = f"{manufacturer}_{model_detail}"
            
            # 전체 차량 목록에 추가 (중복 제거)
            if vehicle_id not in all_vehicles:
                all_vehicles[vehicle_id] = {
                    'manufacturer': manufacturer,
                    'model': model_detail,
                    'nationalSubsidy': national,
                    'category': vehicle['model']
                }
            
            # 제조사별 모델 추가
            manufacturer_models[manufacturer].add(model_detail)
            
            # 지자체 보조금 수집
            if local > 0:
                local_subsidies.append(local)
        
        # 지역별 평균 지자체 보조금 계산
        if local_subsidies:
            avg_subsidy = sum(local_subsidies) // len(local_subsidies)
            max_subsidy = max(local_subsidies)
            min_subsidy = min(local_subsidies)
            
            region_subsidies[region] = {
                'region': region,
                'avgSubsidy': avg_subsidy,
                'maxSubsidy': max_subsidy,
                'minSubsidy': min_subsidy,
                'vehicleCount': len(vehicles)
            }
    
    # 차량 목록을 리스트로 변환하고 정렬
    vehicles_list = sorted(all_vehicles.values(), 
                          key=lambda x: (x['manufacturer'], x['model']))
    
    # 제조사 목록 정렬
    manufacturers = sorted(manufacturer_models.keys())
    
    # 지역 목록 정렬
    regions_list = sorted(region_subsidies.values(), 
                         key=lambda x: x['avgSubsidy'], 
                         reverse=True)
    
    # 전체 데이터 구조
    comprehensive_data = {
        'metadata': {
            'lastUpdated': datetime.now().isoformat(),
            'source': '환경부 전기차 보조금 데이터 (ev.or.kr)',
            'year': 2025,
            'totalVehicles': len(vehicles_list),
            'totalManufacturers': len(manufacturers),
            'totalRegions': len(regions_list)
        },
        'vehicles': vehicles_list,
        'manufacturers': manufacturers,
        'regions': regions_list,
        'regionDetails': raw_data  # 원본 데이터도 포함
    }
    
    return comprehensive_data

def generate_optimized_data():
    """최적화된 데이터 생성"""
    
    # 전체 데이터 처리
    data = process_all_regions_data()
    
    # 통계 정보 출력
    print("📊 데이터 처리 완료:")
    print(f"   - 총 차량 모델: {data['metadata']['totalVehicles']}개")
    print(f"   - 제조사: {data['metadata']['totalManufacturers']}개")
    print(f"   - 지역: {data['metadata']['totalRegions']}개")
    
    # 지자체 보조금 상위 5개 지역
    print("\n💰 지자체 보조금 상위 5개 지역:")
    for i, region in enumerate(data['regions'][:5]):
        print(f"   {i+1}. {region['region']}: 평균 {region['avgSubsidy']}만원 (최대 {region['maxSubsidy']}만원)")
    
    # 제조사별 차량 수
    print("\n🚗 제조사별 차량 모델 수:")
    manufacturer_count = defaultdict(int)
    for vehicle in data['vehicles']:
        manufacturer_count[vehicle['manufacturer']] += 1
    
    for manufacturer, count in sorted(manufacturer_count.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {manufacturer}: {count}개 모델")
    
    # 파일 저장
    filename = f"ev_comprehensive_data_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 데이터를 {filename} 파일로 저장했습니다.")
    
    # 경량화된 버전도 생성 (regionDetails 제외)
    light_data = {
        'metadata': data['metadata'],
        'vehicles': data['vehicles'],
        'manufacturers': data['manufacturers'],
        'regions': data['regions']
    }
    
    light_filename = f"ev_data_light_{datetime.now().strftime('%Y%m%d')}.json"
    with open(light_filename, 'w', encoding='utf-8') as f:
        json.dump(light_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 경량 버전을 {light_filename} 파일로 저장했습니다.")

if __name__ == "__main__":
    generate_optimized_data()