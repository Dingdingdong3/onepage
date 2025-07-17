// 지역 정보 관리
const RegionManager = {
    // 지역 순서 정의 (수도권 -> 광역시 -> 도 순)
    regionOrder: {
        // 수도권
        '서울특별시': 1,
        '경기도': 2,
        '인천광역시': 3,
        // 광역시
        '부산광역시': 11,
        '대구광역시': 12,
        '광주광역시': 13,
        '대전광역시': 14,
        '울산광역시': 15,
        '세종특별자치시': 16,
        // 도
        '강원도': 21,
        '충청북도': 22,
        '충청남도': 23,
        '전라북도': 24,
        '전라남도': 25,
        '경상북도': 26,
        '경상남도': 27,
        '제주특별자치도': 28
    },

    // 지역 그룹 정의
    regionGroups: {
        '수도권': ['서울특별시', '경기도', '인천광역시'],
        '광역시': ['부산광역시', '대구광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시'],
        '도': ['강원도', '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도']
    },

    // 지역 데이터 정렬
    sortRegions(regions) {
        return regions.sort((a, b) => {
            const orderA = this.regionOrder[a] || 50;
            const orderB = this.regionOrder[b] || 50;
            if (orderA !== orderB) return orderA - orderB;
            return a.localeCompare(b);
        });
    },

    // 지역 그룹별 데이터 가져오기
    getRegionsByGroup(group) {
        return this.regionGroups[group] || [];
    },

    // 모든 지역 정렬된 순서로 가져오기
    getAllRegions() {
        return this.sortRegions(Object.keys(this.regionOrder));
    },

    // 지역이 속한 그룹 찾기
    getRegionGroup(region) {
        for (const [group, regions] of Object.entries(this.regionGroups)) {
            if (regions.includes(region)) return group;
        }
        return null;
    }
};

// 브라우저 환경에서 사용할 수 있도록 전역 객체에 추가
if (typeof window !== 'undefined') {
    window.RegionManager = RegionManager;
}