// Google Sheets API 모듈
// 제조사와 모델명 데이터를 가져오는 기능

const GoogleSheetsModule = {
    // 설정
    config: {
        apiKey: 'AIzaSyC2WdvJ29WTuvjkuCBGDwwiIMmmKll59ws',
        spreadsheetId: '1-r-TPHcy0TBAMmnytN510pKV3npE0b5M-hqQQIm3ddA',
        baseUrl: 'https://sheets.googleapis.com/v4/spreadsheets'
    },

    // 초기화
    init: function() {
        console.log('Google Sheets 모듈 초기화');
        return this.testConnection();
    },

    // API 연결 테스트
    testConnection: async function() {
        try {
            const url = `${this.config.baseUrl}/${this.config.spreadsheetId}?key=${this.config.apiKey}`;
            const response = await fetch(url);
            
            if (response.ok) {
                console.log('✅ API 연결 성공');
                return true;
            } else {
                const error = await response.json();
                console.error('❌ API 연결 실패:', error);
                return false;
            }
        } catch (error) {
            console.error('❌ 네트워크 오류:', error);
            return false;
        }
    },

    // 시트 목록 가져오기
    getSheetsList: async function() {
        try {
            const url = `${this.config.baseUrl}/${this.config.spreadsheetId}?key=${this.config.apiKey}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            const sheets = data.sheets || [];
            
            return sheets.map(sheet => ({
                name: sheet.properties.title,
                id: sheet.properties.sheetId
            }));
        } catch (error) {
            console.error('시트 목록 가져오기 실패:', error);
            return [];
        }
    },

    // 특정 범위의 데이터 가져오기
    getRange: async function(range) {
        try {
            const encodedRange = encodeURIComponent(range);
            const url = `${this.config.baseUrl}/${this.config.spreadsheetId}/values/${encodedRange}?key=${this.config.apiKey}`;
            
            const response = await fetch(url);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            return data.values || [];
        } catch (error) {
            console.error(`범위 '${range}' 데이터 가져오기 실패:`, error);
            return [];
        }
    },

    // 차량 데이터 가져오기 (제조사, 모델명, 보조금)
    getVehicleData: async function(sheetName = '2025 서울특별시') {
        try {
            console.log(`${sheetName} 시트에서 차량 데이터 로드 중...`);
            
            // A열(제조사), C열(모델명), D열(국고보조금), E열(지자체보조금) 가져오기
            const range = `${sheetName}!A:G`;
            const rows = await this.getRange(range);
            
            if (rows.length < 2) {
                console.warn('데이터가 없습니다');
                return [];
            }
            
            // 헤더 확인
            const headers = rows[0];
            console.log('헤더:', headers);
            
            // 데이터 파싱 (헤더 제외)
            const vehicles = [];
            for (let i = 1; i < rows.length; i++) {
                const row = rows[i];
                
                // 필수 데이터가 있는 행만 처리
                if (row[0] && row[2] && row[3]) {
                    vehicles.push({
                        manufacturer: row[0].trim(),
                        model: row[2].trim(),
                        nationalSubsidy: parseInt(row[3]) || 0,
                        localSubsidy: parseInt(row[4]) || 0,
                        region: sheetName.replace('2025 ', '')
                    });
                }
            }
            
            console.log(`✅ ${vehicles.length}개의 차량 데이터 로드 완료`);
            return vehicles;
            
        } catch (error) {
            console.error('차량 데이터 가져오기 실패:', error);
            return [];
        }
    },

    // 모든 지역의 차량 데이터 가져오기
    getAllRegionsData: async function() {
        try {
            // 먼저 시트 목록 가져오기
            const sheets = await this.getSheetsList();
            const regionSheets = sheets.filter(sheet => sheet.name.startsWith('2025 '));
            
            console.log(`${regionSheets.length}개 지역 발견`);
            
            const allData = {
                vehicles: [],
                regionSummary: []
            };
            
            // 각 지역별로 데이터 가져오기
            for (const sheet of regionSheets) {
                const vehicles = await this.getVehicleData(sheet.name);
                
                if (vehicles.length > 0) {
                    // 서울특별시 데이터만 차량 목록에 추가
                    if (sheet.name === '2025 서울특별시') {
                        allData.vehicles = vehicles;
                    }
                    
                    // 지역별 평균 보조금 계산
                    const localSubsidies = vehicles
                        .map(v => v.localSubsidy)
                        .filter(s => s > 0);
                    
                    if (localSubsidies.length > 0) {
                        const avgSubsidy = Math.round(
                            localSubsidies.reduce((sum, val) => sum + val, 0) / localSubsidies.length
                        );
                        
                        allData.regionSummary.push({
                            region: sheet.name.replace('2025 ', ''),
                            avgSubsidy: avgSubsidy,
                            vehicleCount: vehicles.length
                        });
                    }
                }
            }
            
            return allData;
            
        } catch (error) {
            console.error('전체 지역 데이터 가져오기 실패:', error);
            return { vehicles: [], regionSummary: [] };
        }
    },

    // 제조사별로 차량 그룹화
    groupByManufacturer: function(vehicles) {
        const grouped = {};
        
        vehicles.forEach(vehicle => {
            if (!grouped[vehicle.manufacturer]) {
                grouped[vehicle.manufacturer] = [];
            }
            grouped[vehicle.manufacturer].push(vehicle);
        });
        
        return grouped;
    },

    // 제조사 목록 가져오기
    getManufacturers: function(vehicles) {
        const manufacturers = [...new Set(vehicles.map(v => v.manufacturer))];
        return manufacturers.sort();
    }
};

// 기본 데이터 (API 실패 시 사용)
const DEFAULT_VEHICLE_DATA = [
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
];

const DEFAULT_REGION_DATA = [
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
];

// 모듈 내보내기 (다른 파일에서 사용할 수 있도록)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GoogleSheetsModule;
}