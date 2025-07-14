// 최종 통합 데이터 로더
// 모든 지역(광역시/특별시 포함) + 차량별 지자체 보조금 차등 적용

const FinalDataLoader = {
    // 설정
    config: {
        lightDataFile: 'ev_data_final_20250713.json',
        fullDataFile: 'ev_complete_data_20250713.json',
        cacheKey: 'ev_final_data',
        cacheDuration: 3600000 // 1시간
    },

    // 데이터 저장소
    data: {
        light: null,    // 기본 데이터
        full: null,     // 전체 데이터 (차량-지역별 보조금 포함)
        vehicleSubsidyMap: null  // 차량-지역별 보조금 매핑
    },

    // 초기화
    async init() {
        console.log('최종 데이터 로더 초기화...');
        
        try {
            // 1. 캐시 확인
            const cached = this.getFromCache();
            if (cached) {
                console.log('✅ 캐시된 데이터 사용');
                this.data.light = cached;
                return true;
            }

            // 2. 경량 데이터 로드
            const lightData = await this.loadLightData();
            if (lightData) {
                this.data.light = lightData;
                this.saveToCache(lightData);
                
                // 전체 데이터는 필요시 로드
                this.loadFullDataInBackground();
                
                return true;
            }
        } catch (error) {
            console.error('초기화 실패:', error);
        }

        return false;
    },

    // 경량 데이터 로드
    async loadLightData() {
        const response = await fetch(this.config.lightDataFile);
        if (!response.ok) {
            throw new Error(`경량 데이터 로드 실패: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`✅ 데이터 로드 완료:`);
        console.log(`   - 차량: ${data.vehicles.length}개`);
        console.log(`   - 지역: ${data.regions.length}개 (광역시/특별시 ${data.metadata.majorCities}개 포함)`);
        console.log(`   - 제조사: ${data.manufacturers.length}개`);
        
        return data;
    },

    // 전체 데이터 백그라운드 로드
    async loadFullDataInBackground() {
        try {
            const response = await fetch(this.config.fullDataFile);
            if (response.ok) {
                this.data.full = await response.json();
                this.data.vehicleSubsidyMap = this.data.full.vehicleSubsidyByRegion;
                console.log('✅ 차량별 지자체 보조금 데이터 로드 완료');
            }
        } catch (error) {
            console.warn('전체 데이터 로드 실패 (기본값 사용):', error);
        }
    },

    // 차량 목록 가져오기
    getVehicles() {
        return this.data.light?.vehicles || [];
    },

    // 제조사 목록 가져오기
    getManufacturers() {
        return this.data.light?.manufacturers || [];
    },

    // 지역 목록 가져오기 (광역시/특별시 우선)
    getRegions() {
        return this.data.light?.regions || [];
    },

    // 특정 차량의 지역별 보조금 가져오기
    getVehicleSubsidyByRegion(vehicleId, regionName) {
        // 1. 차량-지역별 상세 데이터가 있는 경우
        if (this.data.vehicleSubsidyMap && 
            this.data.vehicleSubsidyMap[regionName] && 
            this.data.vehicleSubsidyMap[regionName][vehicleId]) {
            return this.data.vehicleSubsidyMap[regionName][vehicleId];
        }
        
        // 2. 지역 평균값 사용
        const region = this.getRegions().find(r => r.region === regionName);
        return region ? region.avgSubsidy : 0;
    },

    // 제조사별 차량 필터링
    getVehiclesByManufacturer(manufacturer) {
        return this.getVehicles().filter(v => v.manufacturer === manufacturer);
    },

    // 차량 검색
    searchVehicles(keyword) {
        const lowerKeyword = keyword.toLowerCase();
        return this.getVehicles().filter(v => 
            v.manufacturer.toLowerCase().includes(lowerKeyword) ||
            v.model.toLowerCase().includes(lowerKeyword)
        );
    },

    // 보조금 계산 (차량가격 기준 + 차량별 지자체 보조금)
    calculateSubsidy(vehiclePrice, vehicle, regionName) {
        // 차량 정보 확인
        const nationalSubsidy = vehicle?.nationalSubsidy || 0;
        const vehicleId = vehicle?.id || `${vehicle?.manufacturer}_${vehicle?.model}`;
        
        // 차량별 지자체 보조금 가져오기
        const localSubsidy = this.getVehicleSubsidyByRegion(vehicleId, regionName);
        
        // 보조금 지원 기준 적용
        let subsidyRate = 1.0;
        
        if (vehiclePrice >= 8500) {
            subsidyRate = 0;  // 8,500만원 이상: 미지원
        } else if (vehiclePrice >= 5300) {
            subsidyRate = 0.5;  // 5,300만원 이상: 50% 지원
        }
        
        const finalNational = Math.floor(nationalSubsidy * subsidyRate);
        const finalLocal = Math.floor(localSubsidy * subsidyRate);
        
        return {
            nationalSubsidy: finalNational,
            localSubsidy: finalLocal,
            totalSubsidy: finalNational + finalLocal,
            subsidyRate: subsidyRate,
            originalLocal: localSubsidy  // 차량별 원래 지자체 보조금
        };
    },

    // 지역 타입 확인 (광역시/특별시 여부)
    isMajorCity(regionName) {
        const majorCities = [
            '서울특별시', '부산광역시', '대구광역시', '인천광역시',
            '광주광역시', '대전광역시', '울산광역시', '세종특별자치시',
            '경기도', '강원도', '충청북도', '충청남도',
            '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
        ];
        return majorCities.includes(regionName);
    },

    // 캐시 관리
    getFromCache() {
        try {
            const stored = localStorage.getItem(this.config.cacheKey);
            if (!stored) return null;
            
            const { data, timestamp } = JSON.parse(stored);
            const now = Date.now();
            
            if (now - timestamp < this.config.cacheDuration) {
                return data;
            }
        } catch (error) {
            console.error('캐시 읽기 오류:', error);
        }
        return null;
    },

    saveToCache(data) {
        try {
            const cacheData = {
                data: data,
                timestamp: Date.now()
            };
            localStorage.setItem(this.config.cacheKey, JSON.stringify(cacheData));
        } catch (error) {
            console.error('캐시 저장 오류:', error);
        }
    },

    clearCache() {
        localStorage.removeItem(this.config.cacheKey);
        this.data = { light: null, full: null, vehicleSubsidyMap: null };
    }
};

// 전역 함수
window.FinalDataLoader = FinalDataLoader;