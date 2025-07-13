# Google Sheets API 설정 가이드

## 문제 해결: API key not valid 오류

현재 발생한 오류: `HTTP 400: API key not valid. Please pass a valid API key.`

이 오류를 해결하려면 다음 단계를 따라주세요:

## 1단계: 새로운 API 키 생성

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 프로젝트 선택 또는 새 프로젝트 생성
3. 좌측 메뉴에서 "API 및 서비스" → "사용자 인증 정보" 클릭
4. "사용자 인증 정보 만들기" → "API 키" 선택
5. 생성된 API 키 복사

## 2단계: Google Sheets API 활성화

1. Google Cloud Console에서 "API 및 서비스" → "라이브러리" 클릭
2. "Google Sheets API" 검색
3. "Google Sheets API" 클릭 후 "사용" 버튼 클릭
4. API가 활성화될 때까지 잠시 대기

## 3단계: API 키 제한 설정 (선택사항, 보안 강화)

1. "API 및 서비스" → "사용자 인증 정보"로 이동
2. 생성한 API 키 클릭
3. "애플리케이션 제한사항"에서 "HTTP 리퍼러" 선택
4. 웹사이트 제한사항에 다음 추가:
   - `http://localhost/*`
   - `http://127.0.0.1/*`
   - 실제 도메인 (있는 경우)
5. "API 제한사항"에서 "키 제한" 선택
6. "Google Sheets API" 선택
7. "저장" 클릭

## 4단계: 스프레드시트 공개 설정

1. Google Sheets에서 해당 스프레드시트 열기
2. 우측 상단 "공유" 버튼 클릭
3. "링크 가져오기" 클릭
4. "제한됨"을 "링크가 있는 모든 사용자"로 변경
5. "뷰어" 권한 선택 (읽기 전용)
6. "완료" 클릭

## 5단계: 코드에 새 API 키 적용

```javascript
// 기존 API 키를 새로운 키로 교체
const API_KEY = '여기에_새로운_API_키_입력';
```

## 대안: 기존 데이터 사용

API 설정이 복잡하다면, 임시로 로컬 데이터를 사용할 수 있습니다:

1. `google_spreadsheets.py` 파일을 사용하여 데이터를 JSON으로 내보내기
2. JavaScript에서 직접 JSON 데이터 로드

## 확인 사항 체크리스트

- [ ] Google Cloud Console에서 프로젝트 생성됨
- [ ] Google Sheets API가 활성화됨
- [ ] 새로운 API 키가 생성됨
- [ ] 스프레드시트가 공개 설정됨
- [ ] 코드에 새 API 키가 적용됨

## 추가 디버깅

브라우저 개발자 도구(F12)에서 Console 탭을 확인하여:
1. 정확한 오류 메시지 확인
2. 네트워크 탭에서 API 요청 상태 확인
3. 요청 URL이 올바른지 확인

## 참고 링크

- [Google Sheets API 빠른 시작 가이드](https://developers.google.com/sheets/api/quickstart/js)
- [API 키 생성 가이드](https://cloud.google.com/docs/authentication/api-keys)
- [Google Cloud Console](https://console.cloud.google.com/)