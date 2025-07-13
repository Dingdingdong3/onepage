// 통합 데이터 로더
// 모든 지역의 차량 데이터와 지자체 보조금 정보를 제공

const ComprehensiveDataLoader = {
    // 설정
    config: {
        lightDataFile: 'ev_data_light_20250713.json',
        fullDataFile: 'ev_comprehensive_data_20250713.json',
        cacheKey: 'ev_comprehensive_data',
        cacheDuration: 3600000 // 1시간
    },

    // 캐시된 데이터
    cachedData: null,

    // 초기화
    async init() {
        console.log('통합 데이터 로더 초기화...');
        
        // 캐시 확인
        const cached = this.getFromCache();
        if (cached) {
            console.log('캐시된 데이터 사용');
            this.cachedData = cached;
            return true;
        }

        // 경량 데이터 파일 로드
        try {
            const data = await this.loadLightData();
            if (data) {
                this.cachedData = data;
                this.saveToCache(data);
                return true;
            }
        } catch (error) {
            console.error('데이터 로드 실패:', error);
        }

        return false;
    },

    // 경량 데이터 로드
    async loadLightData() {
        const response = await fetch(this.config.lightDataFile);
        if (!response.ok) {
            throw new Error(`데이터 파일 로드 실패: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`✅ ${data.vehicles.length}개 차량, ${data.regions.length}개 지역 데이터 로드 완료`);
        
        return data;
    },

    // 특정 지역의 상세 데이터 로드 (필요시)
    async loadRegionDetails(regionName) {
        if (!this.fullData) {
            const response = await fetch(this.config.fullDataFile);
            if (response.ok) {
                this.fullData = await response.json();
            }
        }
        
        return this.fullData?.regionDetails?.[regionName] || [];
    },

    // 차량 데이터 가져오기
    getVehicles() {
        return this.cachedData?.vehicles || [];
    },

    // 제조사 목록 가져오기
    getManufacturers() {
        return this.cachedData?.manufacturers || [];
    },

    // 지역별 보조금 정보 가져오기
    getRegions() {
        return this.cachedData?.regions || [];
    },

    // 제조사별 차량 필터링
    getVehiclesByManufacturer(manufacturer) {
        return this.getVehicles().filter(v => v.manufacturer === manufacturer);
    },

    // 특정 지역의 평균 지자체 보조금 가져오기
    getRegionSubsidy(regionName) {
        const region = this.getRegions().find(r => r.region === regionName);
        return region ? region.avgSubsidy : 0;
    },

    // 차량 검색
    searchVehicles(keyword) {
        const lowerKeyword = keyword.toLowerCase();
        return this.getVehicles().filter(v => 
            v.manufacturer.toLowerCase().includes(lowerKeyword) ||
            v.model.toLowerCase().includes(lowerKeyword)
        );
    },

    // 보조금 계산 (차량가격 기준 적용)
    calculateSubsidy(vehiclePrice, nationalSubsidy, localSubsidy) {
        // 보조금 지원 기준
        let subsidyRate = 1.0;
        
        if (vehiclePrice >= 8500) {
            // 8,500만원 이상: 미지원
            subsidyRate = 0;
        } else if (vehiclePrice >= 5300) {
            // 5,300만원 이상 ~ 8,500만원 미만: 50% 지원
            subsidyRate = 0.5;
        }
        // 5,300만원 미만: 전액 지원 (subsidyRate = 1.0)
        
        return {
            nationalSubsidy: Math.floor(nationalSubsidy * subsidyRate),
            localSubsidy: Math.floor(localSubsidy * subsidyRate),
            totalSubsidy: Math.floor((nationalSubsidy + localSubsidy) * subsidyRate),
            subsidyRate: subsidyRate
        };
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
        this.cachedData = null;
    }
};

// 메인 애플리케이션에서 사용할 함수
async function loadComprehensiveData() {
    const success = await ComprehensiveDataLoader.init();
    
    if (success) {
        const vehicles = ComprehensiveDataLoader.getVehicles();
        const regions = ComprehensiveDataLoader.getRegions();
        const manufacturers = ComprehensiveDataLoader.getManufacturers();
        
        console.log('📊 데이터 로드 완료:');
        console.log(`   - 차량: ${vehicles.length}개`);
        console.log(`   - 지역: ${regions.length}개`);
        console.log(`   - 제조사: ${manufacturers.length}개`);
        
        return {
            vehicles: vehicles,
            regions: regions,
            manufacturers: manufacturers,
            metadata: ComprehensiveDataLoader.cachedData.metadata
        };
    }
    
    return null;
}

// 전역 객체로 노출 (다른 스크립트에서 사용 가능)
window.ComprehensiveDataLoader = ComprehensiveDataLoader;