import gspread
from google.oauth2.service_account import Credentials
import json

# JSON 파일 내용 확인
with open('/Users/cullen/Documents/eccc/youtube-search-api-447606-43654b5c40cc.json', 'r') as f:
    creds_data = json.load(f)
    print(f"서비스 계정 이메일: {creds_data['client_email']}")

# 인증 및 연결 테스트
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_file(
    '/Users/cullen/Documents/eccc/youtube-search-api-447606-43654b5c40cc.json',
    scopes=scope
)

gc = gspread.authorize(credentials)

# 스프레드시트 ID만 사용
spreadsheet_id = "1KqwyiVutE4_pCwNnAi5DZS0u7SbugLOCpCPDk3vI4AM"

try:
    sheet = gc.open_by_key(spreadsheet_id)
    print(f"✅ 스프레드시트 연결 성공: {sheet.title}")

    worksheet = sheet.sheet1

    # 방법 1: 단일 셀 업데이트 (올바른 형식)
    worksheet.update('A1', [['테스트 성공!']])

    # 또는 방법 2: 범위로 업데이트
    # worksheet.update('A1:A1', [['테스트 성공!']])

    # 또는 방법 3: 여러 데이터 입력
    # worksheet.update('A1:B2', [['테스트', '성공'], ['데이터', '입력']])

    print("✅ 데이터 입력 성공!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
