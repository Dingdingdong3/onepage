#!/usr/bin/env python3
"""
전기차 데이터 크롤링 및 GitHub 자동 업데이트 스크립트
매일 실행하여 최신 데이터를 수집하고 GitHub에 푸시합니다.
"""

import subprocess
import os
import sys
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_crawler():
    """전기차 데이터 크롤러 실행"""
    try:
        logging.info("🚀 전기차 데이터 크롤링 시작...")
        
        # 크롤러 실행
        result = subprocess.run(
            [sys.executable, "electric_car_csv_crawler.py"],
            capture_output=True,
            text=True,
            check=True
        )
        
        logging.info("✅ 크롤링 완료!")
        logging.info(f"출력: {result.stdout}")
        
        if result.stderr:
            logging.warning(f"경고: {result.stderr}")
            
        return True
        
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ 크롤링 실패: {e}")
        logging.error(f"에러 출력: {e.stderr}")
        return False

def git_add_and_commit():
    """변경된 CSV 파일을 Git에 추가하고 커밋"""
    try:
        # Git 상태 확인
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if not status.stdout.strip():
            logging.info("📝 변경사항이 없습니다.")
            return False
        
        # CSV 파일 추가
        logging.info("📁 CSV 파일을 Git에 추가 중...")
        subprocess.run(["git", "add", "csv/*.csv"], shell=True, check=True)
        subprocess.run(["git", "add", "csv/*.json"], shell=True, check=True)
        
        # 커밋 메시지 생성
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Update electric vehicle data - {current_time}\n\nAutomated data update by crawler"
        
        # 커밋
        logging.info("💾 변경사항 커밋 중...")
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            check=True
        )
        
        logging.info("✅ 커밋 완료!")
        return True
        
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Git 작업 실패: {e}")
        return False

def git_push():
    """GitHub에 푸시"""
    try:
        logging.info("🚀 GitHub에 푸시 중...")
        
        # 현재 브랜치 확인
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        # 푸시
        subprocess.run(
            ["git", "push", "origin", branch],
            check=True
        )
        
        logging.info(f"✅ '{branch}' 브랜치에 푸시 완료!")
        return True
        
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ 푸시 실패: {e}")
        
        # 강제 푸시가 필요한 경우 (주의: 신중하게 사용)
        # logging.warning("⚠️ 강제 푸시를 시도합니다...")
        # subprocess.run(["git", "push", "-f", "origin", branch], check=True)
        
        return False

def main():
    """메인 실행 함수"""
    logging.info("=" * 50)
    logging.info("🤖 전기차 데이터 자동 업데이트 시작")
    logging.info(f"실행 시간: {datetime.now()}")
    logging.info("=" * 50)
    
    # 작업 디렉토리 확인
    current_dir = os.getcwd()
    logging.info(f"현재 디렉토리: {current_dir}")
    
    # 1. 크롤러 실행
    if not run_crawler():
        logging.error("크롤링 실패로 인해 프로세스를 종료합니다.")
        sys.exit(1)
    
    # 2. Git 커밋
    if git_add_and_commit():
        # 3. GitHub 푸시
        git_push()
    
    logging.info("=" * 50)
    logging.info("✅ 자동 업데이트 완료!")
    logging.info("=" * 50)

if __name__ == "__main__":
    main()