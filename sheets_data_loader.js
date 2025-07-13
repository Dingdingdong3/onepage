// Google Sheets 데이터 로더 모듈
// API 키 없이 사용할 수 있는 대안 방법 포함

class SheetsDataLoader {
    constructor(spreadsheetId, apiKey) {
        this.spreadsheetId = spreadsheetId;
        this.apiKey = apiKey;
        this.baseUrl = 'https://sheets.googleapis.com/v4/spreadsheets';
    }

    // API 키 유효성 검사
    async validateApiKey() {
        try {
            const url = `${this.baseUrl}/${this.spreadsheetId}?key=${this.apiKey}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || `HTTP ${response.status}`);
            }
            
            return true;
        } catch (error) {
            console.error('API 키 검증 실패:', error);
            return false;
        }
    }

    // 스프레드시트 메타데이터 가져오기
    async getSpreadsheetMetadata() {
        const url = `${this.baseUrl}/${this.spreadsheetId}?key=${this.apiKey}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`스프레드시트 메타데이터 로드 실패: ${response.status}`);
        }
        
        return await response.json();
    }

    // 특정 범위의 데이터 가져오기
    async getRange(range) {
        const encodedRange = encodeURIComponent(range);
        const url = `${this.baseUrl}/${this.spreadsheetId}/values/${encodedRange}?key=${this.apiKey}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`데이터 로드 실패: ${response.status}`);
        }
        
        const data = await response.json();
        return data.values || [];
    }

    // 차량 데이터 파싱
    parseVehicleData(rows) {
        if (rows.length < 2) return [];
        
        // 헤더 제외하고 데이터 파싱
        return rows.slice(1)
            .filter(row => row[0] && row[2] && row[3]) // 제조사, 모델명, 국고보조금 필수
            .map(row => ({
                manufacturer: row[0].trim(),
                model: row[2].trim(),
                nationalSubsidy: parseInt(row[3]) || 0,
                localSubsidy: parseInt(row[4]) || 0
            }));
    }

    // 제조사별로 그룹화
    groupByManufacturer(vehicles) {
        return vehicles.reduce((acc, vehicle) => {
            if (!acc[vehicle.manufacturer]) {
                acc[vehicle.manufacturer] = [];
            }
            acc[vehicle.manufacturer].push(vehicle);
            return acc;
        }, {});
    }
}

// 기본 데이터 (API 실패 시 사용)
const FALLBACK_DATA = {
    vehicles: [
        { manufacturer: '현대자동차', model: '아이오닉6 롱레인지 2WD 18인치', nationalSubsidy: 686, localSubsidy: 400 },
        { manufacturer: '현대자동차', model: '아이오닉5 2WD 롱레인지 19인치', nationalSubsidy: 659, localSubsidy: 400 },
        { manufacturer: '현대자동차', model: '코나 일렉트릭 2WD 롱레인지 17인치', nationalSubsidy: 623, localSubsidy: 400 },
        { manufacturer: '기아', model: 'EV6 롱레인지 2WD 19인치', nationalSubsidy: 655, localSubsidy: 400 },
        { manufacturer: '기아', model: 'EV3 롱레인지 2WD 17인치', nationalSubsidy: 565, localSubsidy: 400 },
        { manufacturer: '기아', model: 'EV9 2WD 스탠다드', nationalSubsidy: 300, localSubsidy: 400 },
        { manufacturer: '제네시스', model: 'GV60 스탠다드 2WD', nationalSubsidy: 544, localSubsidy: 400 },
        { manufacturer: '제네시스', model: 'GV70 일렉트리파이드', nationalSubsidy: 285, localSubsidy: 400 },
        { manufacturer: 'BMW', model: 'i4 eDrive40', nationalSubsidy: 189, localSubsidy: 400 },
        { manufacturer: 'BMW', model: 'iX xDrive40', nationalSubsidy: 165, localSubsidy: 400 },
        { manufacturer: '테슬라', model: 'Model 3 Long Range', nationalSubsidy: 202, localSubsidy: 400 },
        { manufacturer: '테슬라', model: 'Model Y Long Range', nationalSubsidy: 169, localSubsidy: 400 },
        { manufacturer: '메르세데스-벤츠', model: 'EQE 350+', nationalSubsidy: 163, localSubsidy: 400 },
        { manufacturer: '폭스바겐', model: 'ID.4 Pro', nationalSubsidy: 423, localSubsidy: 400 },
        { manufacturer: '볼보', model: 'XC40 Recharge', nationalSubsidy: 314, localSubsidy: 400 },
        { manufacturer: '폴스타', model: '2 Long Range Single Motor', nationalSubsidy: 359, localSubsidy: 400 }
    ],
    regions: [
        { region: '서울특별시', avgSubsidy: 400 },
        { region: '부산광역시', avgSubsidy: 300 },
        { region: '대구광역시', avgSubsidy: 350 },
        { region: '인천광역시', avgSubsidy: 350 },
        { region: '광주광역시', avgSubsidy: 380 },
        { region: '대전광역시', avgSubsidy: 360 },
        { region: '울산광역시', avgSubsidy: 350 },
        { region: '세종특별자치시', avgSubsidy: 400 },
        { region: '경기도', avgSubsidy: 300 },
        { region: '강원도', avgSubsidy: 450 },
        { region: '충청북도', avgSubsidy: 400 },
        { region: '충청남도', avgSubsidy: 400 },
        { region: '전라북도', avgSubsidy: 420 },
        { region: '전라남도', avgSubsidy: 450 },
        { region: '경상북도', avgSubsidy: 400 },
        { region: '경상남도', avgSubsidy: 380 },
        { region: '제주특별자치도', avgSubsidy: 600 }
    ]
};

// 데이터 로더 헬퍼 함수
async function loadVehicleData(spreadsheetId, apiKey) {
    const loader = new SheetsDataLoader(spreadsheetId, apiKey);
    
    try {
        // API 키 검증
        const isValid = await loader.validateApiKey();
        if (!isValid) {
            console.warn('API 키가 유효하지 않습니다. 기본 데이터를 사용합니다.');
            return FALLBACK_DATA;
        }
        
        // 서울특별시 데이터 로드
        const seoulData = await loader.getRange('2025 서울특별시!A:G');
        const vehicles = loader.parseVehicleData(seoulData);
        
        // 지역별 보조금 데이터는 FALLBACK_DATA 사용
        return {
            vehicles: vehicles.length > 0 ? vehicles : FALLBACK_DATA.vehicles,
            regions: FALLBACK_DATA.regions
        };
        
    } catch (error) {
        console.error('데이터 로드 실패:', error);
        return FALLBACK_DATA;
    }
}

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SheetsDataLoader, FALLBACK_DATA, loadVehicleData };
}