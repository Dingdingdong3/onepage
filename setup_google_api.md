# Google Sheets API 설정 가이드

## 1. Google Cloud Console에서 API 키 생성

1. Google Cloud Console (https://console.cloud.google.com) 접속
2. 프로젝트 선택 또는 새 프로젝트 생성
3. "API 및 서비스" > "라이브러리" 이동
4. "Google Sheets API" 검색 후 활성화
5. "API 및 서비스" > "사용자 인증 정보" 이동
6. "+ 사용자 인증 정보 만들기" > "API 키" 선택
7. 생성된 API 키 복사

## 2. API 키 제한 설정 (보안)

1. 생성된 API 키 클릭
2. "애플리케이션 제한사항"에서 "HTTP 리퍼러" 선택
3. 웹사이트 URL 패턴 추가 (예: `https://yourdomain.com/*`)
4. "API 제한사항"에서 "키 제한" 선택
5. "Google Sheets API" 선택
6. 저장

## 3. 스프레드시트 공개 설정

1. Google Sheets에서 해당 스프레드시트 열기
2. 우측 상단 "공유" 버튼 클릭
3. "링크가 있는 모든 사용자" 선택
4. 권한을 "뷰어"로 설정
5. "링크 복사" (스프레드시트 ID 확인용)

## 4. 웹페이지에서 API 키 적용

index_new.html 파일에서 다음 부분을 수정:

```javascript
const API_KEY = 'YOUR_API_KEY_HERE'; // 실제 API 키로 교체
```

## 5. 실제 Google Sheets 연동 코드

API 키가 설정되면 다음 함수들이 실제 Google Sheets에서 데이터를 가져옵니다:

```javascript
// 실제 Google Sheets에서 지자체 목록 가져오기
async function loadRegionsFromSheets() {
    const response = await fetch(`https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_ID}?key=${API_KEY}`);
    const data = await response.json();
    const sheets = data.sheets;
    
    allRegions = sheets
        .map(sheet => sheet.properties.title)
        .filter(title => title.startsWith('2025 '))
        .map(title => title.replace('2025 ', ''))
        .sort();
}

// 실제 Google Sheets에서 차량 데이터 가져오기
async function fetchRegionDataFromSheets(region) {
    const range = `${encodeURIComponent(`2025 ${region}`)}!A:G`;
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_ID}/values/${range}?key=${API_KEY}`;
    const response = await fetch(url);
    const data = await response.json();
    
    if (!data.values || data.values.length < 2) {
        return [];
    }
    
    const headers = data.values[0];
    const rows = data.values.slice(1);
    
    return rows.map(row => ({
        manufacturer: row[0] || '',
        model: row[2] || '',
        nationalSubsidy: parseInt(row[3]) || 0,
        localSubsidy: parseInt(row[4]) || 0,
        totalSubsidy: parseInt(row[5]) || 0
    }));
}
```

## 6. API 키 없이 작동하는 방법

현재 index_new.html은 API 키 없이도 시뮬레이션 데이터로 작동합니다. 
실제 운영 시에는 위의 API 키 설정이 필요합니다.

## 7. 보안 고려사항

- API 키는 클라이언트 사이드에 노출되므로 적절한 제한 설정 필요
- 더 높은 보안을 위해서는 백엔드 서버를 통한 API 호출 권장
- 정기적인 API 키 갱신 고려