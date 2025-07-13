#!/usr/bin/env python3
"""
Google Sheets 데이터를 JSON으로 내보내기
API 할당량 문제를 해결하기 위한 로컬 데이터 생성
"""

import json
from datetime import datetime

# Google Sheets에서 수동으로 복사한 데이터
# (API 제한으로 인해 하드코딩)
VEHICLE_DATA = {
    "서울특별시": [
        {"manufacturer": "현대자동차", "model": "아이오닉6 롱레인지 2WD 18인치", "nationalSubsidy": 686, "localSubsidy": 400},
        {"manufacturer": "현대자동차", "model": "아이오닉5 2WD 롱레인지 19인치", "nationalSubsidy": 659, "localSubsidy": 400},
        {"manufacturer": "현대자동차", "model": "코나 일렉트릭 2WD 롱레인지 17인치", "nationalSubsidy": 623, "localSubsidy": 400},
        {"manufacturer": "기아", "model": "EV6 롱레인지 2WD 19인치", "nationalSubsidy": 655, "localSubsidy": 400},
        {"manufacturer": "기아", "model": "EV3 롱레인지 2WD 17인치", "nationalSubsidy": 565, "localSubsidy": 400},
        {"manufacturer": "기아", "model": "EV9 2WD 스탠다드", "nationalSubsidy": 300, "localSubsidy": 400},
        {"manufacturer": "제네시스", "model": "GV60 스탠다드 2WD", "nationalSubsidy": 544, "localSubsidy": 400},
        {"manufacturer": "제네시스", "model": "GV70 일렉트리파이드", "nationalSubsidy": 285, "localSubsidy": 400},
        {"manufacturer": "제네시스", "model": "일렉트리파이드 G80", "nationalSubsidy": 211, "localSubsidy": 400},
        {"manufacturer": "BMW", "model": "i4 eDrive40", "nationalSubsidy": 189, "localSubsidy": 400},
        {"manufacturer": "BMW", "model": "iX xDrive40", "nationalSubsidy": 165, "localSubsidy": 400},
        {"manufacturer": "BMW", "model": "i5 eDrive40", "nationalSubsidy": 152, "localSubsidy": 400},
        {"manufacturer": "테슬라", "model": "Model 3 Long Range", "nationalSubsidy": 202, "localSubsidy": 400},
        {"manufacturer": "테슬라", "model": "Model Y Long Range", "nationalSubsidy": 169, "localSubsidy": 400},
        {"manufacturer": "메르세데스-벤츠", "model": "EQE 350+", "nationalSubsidy": 163, "localSubsidy": 400},
        {"manufacturer": "메르세데스-벤츠", "model": "EQA 250", "nationalSubsidy": 314, "localSubsidy": 400},
        {"manufacturer": "폭스바겐", "model": "ID.4 Pro", "nationalSubsidy": 423, "localSubsidy": 400},
        {"manufacturer": "볼보", "model": "XC40 Recharge", "nationalSubsidy": 314, "localSubsidy": 400},
        {"manufacturer": "볼보", "model": "C40 Recharge", "nationalSubsidy": 298, "localSubsidy": 400},
        {"manufacturer": "폴스타", "model": "2 Long Range Single Motor", "nationalSubsidy": 359, "localSubsidy": 400},
        {"manufacturer": "아우디", "model": "e-tron GT", "nationalSubsidy": 123, "localSubsidy": 400},
        {"manufacturer": "아우디", "model": "Q4 e-tron", "nationalSubsidy": 291, "localSubsidy": 400},
        {"manufacturer": "포르쉐", "model": "Taycan 4S", "nationalSubsidy": 100, "localSubsidy": 400},
        {"manufacturer": "현대자동차", "model": "아이오닉6 스탠다드 2WD", "nationalSubsidy": 630, "localSubsidy": 400},
        {"manufacturer": "현대자동차", "model": "아이오닉5 2WD 스탠다드", "nationalSubsidy": 604, "localSubsidy": 400},
        {"manufacturer": "기아", "model": "EV6 스탠다드 2WD", "nationalSubsidy": 601, "localSubsidy": 400},
        {"manufacturer": "쉐보레", "model": "볼트 EUV", "nationalSubsidy": 423, "localSubsidy": 400},
        {"manufacturer": "닛산", "model": "리프", "nationalSubsidy": 485, "localSubsidy": 400},
        {"manufacturer": "푸조", "model": "e-2008", "nationalSubsidy": 384, "localSubsidy": 400},
        {"manufacturer": "르노", "model": "메간 E-Tech", "nationalSubsidy": 415, "localSubsidy": 400}
    ]
}

# 지역별 평균 보조금 데이터
REGION_SUBSIDIES = [
    {"region": "서울특별시", "avgSubsidy": 400, "maxSubsidy": 400},
    {"region": "부산광역시", "avgSubsidy": 300, "maxSubsidy": 350},
    {"region": "대구광역시", "avgSubsidy": 350, "maxSubsidy": 400},
    {"region": "인천광역시", "avgSubsidy": 350, "maxSubsidy": 400},
    {"region": "광주광역시", "avgSubsidy": 380, "maxSubsidy": 450},
    {"region": "대전광역시", "avgSubsidy": 360, "maxSubsidy": 400},
    {"region": "울산광역시", "avgSubsidy": 350, "maxSubsidy": 400},
    {"region": "세종특별자치시", "avgSubsidy": 400, "maxSubsidy": 450},
    {"region": "경기도", "avgSubsidy": 300, "maxSubsidy": 400},
    {"region": "강원도", "avgSubsidy": 450, "maxSubsidy": 500},
    {"region": "충청북도", "avgSubsidy": 400, "maxSubsidy": 450},
    {"region": "충청남도", "avgSubsidy": 400, "maxSubsidy": 450},
    {"region": "전라북도", "avgSubsidy": 420, "maxSubsidy": 500},
    {"region": "전라남도", "avgSubsidy": 450, "maxSubsidy": 500},
    {"region": "경상북도", "avgSubsidy": 400, "maxSubsidy": 450},
    {"region": "경상남도", "avgSubsidy": 380, "maxSubsidy": 450},
    {"region": "제주특별자치도", "avgSubsidy": 600, "maxSubsidy": 600}
]

def export_to_json():
    """데이터를 JSON 파일로 내보내기"""
    
    # 전체 데이터 구조
    data = {
        "metadata": {
            "lastUpdated": datetime.now().isoformat(),
            "source": "환경부 전기차 보조금 데이터",
            "year": 2025
        },
        "vehicles": VEHICLE_DATA["서울특별시"],
        "regions": REGION_SUBSIDIES,
        "manufacturers": sorted(list(set(v["manufacturer"] for v in VEHICLE_DATA["서울특별시"])))
    }
    
    # JSON 파일로 저장
    filename = f"ev_subsidy_data_{datetime.now().strftime('%Y%m%d')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 데이터를 {filename} 파일로 내보냈습니다.")
    print(f"   - 차량 수: {len(data['vehicles'])}개")
    print(f"   - 제조사 수: {len(data['manufacturers'])}개")
    print(f"   - 지역 수: {len(data['regions'])}개")
    
    # 간단한 통계 출력
    print("\n📊 보조금 통계:")
    subsidies = [v["nationalSubsidy"] for v in data["vehicles"]]
    print(f"   - 최대 국고보조금: {max(subsidies)}만원")
    print(f"   - 최소 국고보조금: {min(subsidies)}만원")
    print(f"   - 평균 국고보조금: {sum(subsidies) // len(subsidies)}만원")

if __name__ == "__main__":
    export_to_json()