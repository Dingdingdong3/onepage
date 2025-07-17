// 지역별 보조금 데이터 관리
class RegionSubsidyManager {
    constructor() {
        this.subsidyData = null;
        this.vehicleData = null;
        this.year = 2025;
    }

    // 데이터 초기화
    async initialize() {
        try {
            const response = await fetch(`/csv/${this.year}.csv`);
            const csvText = await response.text();
            this.parseCSV(csvText);
            return true;
        } catch (error) {
            console.error('보조금 데이터 로드 실패:', error);
            return false;
        }
    }

    // CSV 파싱
    parseCSV(csvText) {
        const lines = csvText.split('\n');
        const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
        
        const data = [];
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            const values = [];
            let current = '';
            let inQuotes = false;
            
            for (let j = 0; j < line.length; j++) {
                const char = line[j];
                
                if (char === '"') {
                    inQuotes = !inQuotes;
                } else if (char === ',' && !inQuotes) {
                    values.push(current.trim());
                    current = '';
                } else {
                    current += char;
                }
            }
            values.push(current.trim());
            
            if (values.length >= headers.length) {
                const row = {};
                headers.forEach((header, index) => {
                    row[header] = values[index];
                });
                data.push(row);
            }
        }
        
        this.subsidyData = this.processSubsidyData(data);
        this.vehicleData = this.processVehicleData(data);
    }

    // 지역별 보조금 데이터 처리
    processSubsidyData(data) {
        const subsidyMap = new Map();
        
        data.forEach(row => {
            const region = row['지역'];
            if (!region) return;
            
            if (!subsidyMap.has(region)) {
                subsidyMap.set(region, {
                    region: region,
                    vehicles: new Map(),
                    averageSubsidy: 0,
                    maxSubsidy: 0,
                    minSubsidy: Infinity
                });
            }
            
            const regionData = subsidyMap.get(region);
            const vehicleName = row['모델명'] || row['차종'];
            const nationalSubsidy = parseInt(row['국비보조금(만원)']) || 0;
            const localSubsidy = parseInt(row['지방비보조금(만원)']) || 0;
            
            if (vehicleName) {
                regionData.vehicles.set(vehicleName, {
                    nationalSubsidy,
                    localSubsidy,
                    totalSubsidy: nationalSubsidy + localSubsidy
                });
                
                regionData.maxSubsidy = Math.max(regionData.maxSubsidy, localSubsidy);
                regionData.minSubsidy = Math.min(regionData.minSubsidy, localSubsidy);
            }
        });
        
        // 평균 보조금 계산
        subsidyMap.forEach(regionData => {
            const subsidies = Array.from(regionData.vehicles.values());
            regionData.averageSubsidy = Math.round(
                subsidies.reduce((sum, v) => sum + v.localSubsidy, 0) / subsidies.length
            );
        });
        
        return subsidyMap;
    }

    // 차량별 보조금 데이터 처리
    processVehicleData(data) {
        const vehicleMap = new Map();
        
        data.forEach(row => {
            const vehicleName = row['모델명'] || row['차종'];
            const manufacturer = row['제조사'];
            
            if (!vehicleName || !manufacturer) return;
            
            if (!vehicleMap.has(vehicleName)) {
                vehicleMap.set(vehicleName, {
                    name: vehicleName,
                    manufacturer: manufacturer,
                    regions: new Map(),
                    nationalSubsidy: parseInt(row['국비보조금(만원)']) || 0
                });
            }
            
            const vehicleData = vehicleMap.get(vehicleName);
            const region = row['지역'];
            const localSubsidy = parseInt(row['지방비보조금(만원)']) || 0;
            
            if (region) {
                vehicleData.regions.set(region, localSubsidy);
            }
        });
        
        return vehicleMap;
    }

    // 지역별 보조금 조회
    getRegionSubsidy(region) {
        return this.subsidyData.get(region);
    }

    // 차량별 보조금 조회
    getVehicleSubsidy(vehicleName) {
        return this.vehicleData.get(vehicleName);
    }

    // 모든 지역 목록 조회
    getAllRegions() {
        return Array.from(this.subsidyData.keys());
    }

    // 모든 차량 목록 조회
    getAllVehicles() {
        return Array.from(this.vehicleData.keys());
    }

    // 보조금 계산
    calculateSubsidy(vehicle, region, price) {
        const vehicleData = this.getVehicleSubsidy(vehicle);
        if (!vehicleData) return null;
        
        const regionData = vehicleData.regions.get(region);
        if (regionData === undefined) return null;
        
        // 보조금 지원 기준 적용
        let subsidyRate = 1;
        if (price >= 8500) {
            subsidyRate = 0;
        } else if (price >= 5300) {
            subsidyRate = 0.5;
        }
        
        const nationalSubsidy = Math.floor(vehicleData.nationalSubsidy * subsidyRate);
        const localSubsidy = Math.floor(regionData * subsidyRate);
        
        // 취득세 계산 (승용차 7% 기준)
        const baseTax = Math.floor(price * 0.07);
        const taxReduction = Math.min(140, baseTax); // 최대 140만원 감면
        const finalTax = Math.max(0, baseTax - taxReduction);
        
        return {
            nationalSubsidy,
            localSubsidy,
            totalSubsidy: nationalSubsidy + localSubsidy,
            tax: finalTax,
            finalPrice: price + finalTax - (nationalSubsidy + localSubsidy)
        };
    }
}

// 글로벌 인스턴스 생성
const regionSubsidyManager = new RegionSubsidyManager();

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', async function() {
    await regionSubsidyManager.initialize();
});