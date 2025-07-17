// 차량 URL 매핑 데이터
const vehicleUrlMapping = {
    // 현대 차량
    "코나 Electric": "kona-electric",
    "아이오닉 5": "ioniq5",
    "아이오닉 6": "ioniq6",
    "NEXO": "nexo",
    "더 뉴 아이오닉 5": "new-ioniq5",
    "더 뉴 아이오닉 6": "new-ioniq6",
    "캐스퍼 Electric": "casper-electric",
    "아이오닉 7": "ioniq7",
    
    // 기아 차량
    "EV6": "ev6",
    "더뉴EV6": "new-ev6",
    "EV9": "ev9",
    "EV3": "ev3",
    "EV4": "ev4",
    "The all-new Kia Niro EV": "niro-ev",
    "레이 EV": "ray-ev",
    
    // 테슬라 차량
    "Model 3": "model3",
    "Model Y": "model-y",
    "Model S": "model-s",
    "Model X": "model-x",
    
    // 제네시스 차량
    "Electrified G80": "g80-electrified",
    "Electrified GV70": "gv70-electrified",
    "GV60": "gv60",
    
    // BMW 차량
    "i4": "i4",
    "iX": "ix",
    "i3": "i3",
    "i7": "i7",
    "iX1": "ix1",
    "iX2": "ix2",
    "MINI Cooper SE": "mini-cooper-se",
    "MINI Countryman SE": "mini-countryman-se",
    "MINI Aceman": "mini-aceman",
    
    // 메르세데스-벤츠 차량
    "EQA": "eqa",
    "EQB": "eqb",
    "EQC": "eqc",
    "EQE": "eqe",
    "EQS": "eqs",
    "EQV": "eqv",
    
    // 아우디 차량
    "Q4 e-tron": "q4-etron",
    "Q8 e-tron": "q8-etron",
    "e-tron GT": "etron-gt",
    
    // 폭스바겐 차량
    "ID.4": "id4",
    "ID.5": "id5",
    "ID.6": "id6",
    "ID.7": "id7",
    "ID.Buzz": "id-buzz",
    
    // 볼보 차량
    "XC40 Recharge": "xc40-recharge",
    "C40 Recharge": "c40-recharge",
    "EX30": "ex30",
    "EX90": "ex90",
    
    // 기타 차량
    "BYD ATTO 3": "byd-atto3",
    "토레스 EVX": "torres-evx",
    "코란도 EV": "korando-ev",
    "CEVO-C SE": "cevo-c-se"
};

// 차량명을 URL로 변환하는 함수
function getVehicleUrl(vehicleName) {
    // 정확한 매칭 우선
    if (vehicleUrlMapping[vehicleName]) {
        return vehicleUrlMapping[vehicleName];
    }
    
    // 부분 매칭
    for (const [key, value] of Object.entries(vehicleUrlMapping)) {
        if (vehicleName.includes(key) || key.includes(vehicleName)) {
            return value;
        }
    }
    
    // 자동 변환 (최후 수단)
    return vehicleName
        .toLowerCase()
        .replace(/[^a-z0-9가-힣]/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
}

// URL에서 차량명 추출
function getVehicleFromUrl(url) {
    const urlPath = url.split('/').pop();
    
    for (const [vehicleName, urlSlug] of Object.entries(vehicleUrlMapping)) {
        if (urlSlug === urlPath) {
            return vehicleName;
        }
    }
    
    return null;
}

// 차량별 SEO 메타 데이터
const vehicleSeoData = {
    "ioniq5": {
        title: "현대 아이오닉 5 보조금 및 취득세 계산기",
        description: "현대 아이오닉 5의 국고보조금, 지자체보조금, 취득세를 실시간으로 계산하세요. 최신 보조금 정보로 정확한 구매 비용을 확인하세요.",
        keywords: "현대 아이오닉 5, 아이오닉 5 보조금, 아이오닉 5 취득세, 현대 전기차"
    },
    "ev6": {
        title: "기아 EV6 보조금 및 취득세 계산기",
        description: "기아 EV6의 국고보조금, 지자체보조금, 취득세를 실시간으로 계산하세요. 최신 보조금 정보로 정확한 구매 비용을 확인하세요.",
        keywords: "기아 EV6, EV6 보조금, EV6 취득세, 기아 전기차"
    },
    "model-y": {
        title: "테슬라 모델 Y 보조금 및 취득세 계산기",
        description: "테슬라 모델 Y의 국고보조금, 지자체보조금, 취득세를 실시간으로 계산하세요. 최신 보조금 정보로 정확한 구매 비용을 확인하세요.",
        keywords: "테슬라 모델 Y, 모델 Y 보조금, 모델 Y 취득세, 테슬라 전기차"
    },
    "ev9": {
        title: "기아 EV9 보조금 및 취득세 계산기",
        description: "기아 EV9의 국고보조금, 지자체보조금, 취득세를 실시간으로 계산하세요. 최신 보조금 정보로 정확한 구매 비용을 확인하세요.",
        keywords: "기아 EV9, EV9 보조금, EV9 취득세, 기아 전기차"
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        vehicleUrlMapping,
        getVehicleUrl,
        getVehicleFromUrl,
        vehicleSeoData
    };
}