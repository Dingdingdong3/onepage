# 전기차 데이터 크롤러 자동화 설정

## 개요
이 문서는 전기차 데이터를 매일 자동으로 수집하고 GitHub에 업데이트하는 방법을 설명합니다.

## 자동화 방법

### 1. GitHub Actions (권장)
`.github/workflows/daily-crawler.yml` 파일이 이미 설정되어 있습니다.
- **실행 시간**: 매일 오후 6시 5분 (한국 시간)
- **자동 실행**: GitHub에서 자동으로 실행됩니다
- **수동 실행**: GitHub Actions 탭에서 "Daily Electric Vehicle Data Update" 워크플로우를 수동으로 실행할 수 있습니다

### 2. 로컬 Cron 설정 (macOS/Linux)

#### Cron 작업 추가:
```bash
crontab -e
```

다음 줄을 추가하세요:
```bash
# 매일 오후 6시 5분에 실행
5 18 * * * cd /Users/cullen/Documents/eccc && /usr/bin/python3 run_crawler_and_push.py >> crawler_automation.log 2>&1
```

#### Cron 작업 확인:
```bash
crontab -l
```

### 3. 수동 실행
```bash
python run_crawler_and_push.py
```

## 로그 확인
- **로컬 실행 로그**: `crawler_automation.log`
- **GitHub Actions 로그**: GitHub 저장소의 Actions 탭에서 확인

## 문제 해결

### Git 권한 문제
GitHub Actions가 push할 수 있도록 다음을 확인하세요:
1. Settings → Actions → General
2. Workflow permissions에서 "Read and write permissions" 선택

### 로컬 실행 시 권한 문제
```bash
# Git 자격 증명 저장
git config credential.helper store

# 첫 실행 시 GitHub 사용자명과 Personal Access Token 입력
```

## 데이터 구조
- 크롤링된 데이터는 `csv/` 폴더에 저장됩니다
- 파일명 형식: `{년도}.csv`, `{년도}.json`
- 기존 파일은 자동으로 덮어쓰기됩니다

## 주의사항
- 크롤러는 현재 연도의 데이터만 수집합니다
- 과거 연도 데이터는 보존됩니다
- 너무 자주 실행하면 서버에 부담을 줄 수 있으니 주의하세요