// 최적화된 데이터 로더
// API 요청을 최소화하고 로컬 캐싱을 활용

const OptimizedDataLoader = {
    // 캐시 설정
    cache: {
        data: null,
        timestamp: null,
        duration: 3600000 // 1시간 캐시
    },

    // 로컬 스토리지 키
    STORAGE_KEY: 'ev_calculator_data',

    // JSON 파일에서 데이터 로드
    async loadFromJSON() {
        try {
            const response = await fetch('ev_subsidy_data_20250713.json');
            if (!response.ok) {
                throw new Error('JSON 파일 로드 실패');
            }
            const data = await response.json();
            
            // 로컬 스토리지에 저장
            this.saveToCache(data);
            
            return data;
        } catch (error) {
            console.error('JSON 로드 실패:', error);
            return null;
        }
    },

    // Google Sheets API를 통한 데이터 로드 (제한적 사용)
    async loadFromAPI() {
        // 캐시 확인
        const cached = this.getFromCache();
        if (cached) {
            console.log('캐시된 데이터 사용');
            return cached;
        }

        try {
            // API 요청을 하나로 통합
            const sheetName = '2025 서울특별시';
            const range = `${sheetName}!A:G`;
            const url = `https://sheets.googleapis.com/v4/spreadsheets/${this.config.spreadsheetId}/values/${encodeURIComponent(range)}?key=${this.config.apiKey}`;
            
            const response = await fetch(url);
            
            if (response.status === 429) {
                console.warn('API 할당량 초과. 로컬 데이터 사용');
                return await this.loadFromJSON();
            }
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            const data = this.parseSheetData(result.values);
            
            // 캐시에 저장
            this.saveToCache(data);
            
            return data;
        } catch (error) {
            console.error('API 로드 실패:', error);
            return await this.loadFromJSON();
        }
    },

    // 시트 데이터 파싱
    parseSheetData(rows) {
        if (!rows || rows.length < 2) return null;
        
        const vehicles = [];
        // 헤더 제외하고 파싱
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            if (row[0] && row[2] && row[3]) {
                vehicles.push({
                    manufacturer: row[0].trim(),
                    model: row[2].trim(),
                    nationalSubsidy: parseInt(row[3]) || 0,
                    localSubsidy: parseInt(row[4]) || 0
                });
            }
        }
        
        // 제조사 목록 생성
        const manufacturers = [...new Set(vehicles.map(v => v.manufacturer))].sort();
        
        return {
            vehicles,
            manufacturers,
            regions: this.getDefaultRegions()
        };
    },

    // 기본 지역 데이터
    getDefaultRegions() {
        return [
            { region: "서울특별시", avgSubsidy: 400 },
            { region: "부산광역시", avgSubsidy: 300 },
            { region: "대구광역시", avgSubsidy: 350 },
            { region: "인천광역시", avgSubsidy: 350 },
            { region: "광주광역시", avgSubsidy: 380 },
            { region: "대전광역시", avgSubsidy: 360 },
            { region: "울산광역시", avgSubsidy: 350 },
            { region: "세종특별자치시", avgSubsidy: 400 },
            { region: "경기도", avgSubsidy: 300 },
            { region: "강원도", avgSubsidy: 450 },
            { region: "충청북도", avgSubsidy: 400 },
            { region: "충청남도", avgSubsidy: 400 },
            { region: "전라북도", avgSubsidy: 420 },
            { region: "전라남도", avgSubsidy: 450 },
            { region: "경상북도", avgSubsidy: 400 },
            { region: "경상남도", avgSubsidy: 380 },
            { region: "제주특별자치도", avgSubsidy: 600 }
        ];
    },

    // 캐시에서 데이터 가져오기
    getFromCache() {
        try {
            const stored = localStorage.getItem(this.STORAGE_KEY);
            if (!stored) return null;
            
            const { data, timestamp } = JSON.parse(stored);
            const now = Date.now();
            
            // 캐시 유효성 확인
            if (now - timestamp < this.cache.duration) {
                return data;
            }
            
            return null;
        } catch (error) {
            console.error('캐시 읽기 실패:', error);
            return null;
        }
    },

    // 캐시에 데이터 저장
    saveToCache(data) {
        try {
            const cacheData = {
                data: data,
                timestamp: Date.now()
            };
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(cacheData));
            console.log('데이터가 캐시에 저장됨');
        } catch (error) {
            console.error('캐시 저장 실패:', error);
        }
    },

    // 캐시 삭제
    clearCache() {
        localStorage.removeItem(this.STORAGE_KEY);
        console.log('캐시가 삭제됨');
    },

    // API 설정
    config: {
        apiKey: 'AIzaSyC2WdvJ29WTuvjkuCBGDwwiIMmmKll59ws',
        spreadsheetId: '1-r-TPHcy0TBAMmnytN510pKV3npE0b5M-hqQQIm3ddA'
    }
};

// 메인 로드 함수
async function loadOptimizedData() {
    console.log('최적화된 데이터 로드 시작...');
    
    // 1. 먼저 캐시 확인
    const cached = OptimizedDataLoader.getFromCache();
    if (cached) {
        console.log('캐시된 데이터 사용');
        return cached;
    }
    
    // 2. JSON 파일 시도
    const jsonData = await OptimizedDataLoader.loadFromJSON();
    if (jsonData) {
        console.log('JSON 파일에서 데이터 로드 성공');
        return jsonData;
    }
    
    // 3. API 시도 (마지막 수단)
    console.log('API에서 데이터 로드 시도...');
    return await OptimizedDataLoader.loadFromAPI();
}