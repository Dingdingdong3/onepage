#!/opt/anaconda3/bin/python
# -*- coding: utf-8 -*-
"""
전기차 보조금 크롤러 빠른 설치 및 실행 스크립트
"""

import subprocess
import sys
import os


def install_package(package, description=""):
    """패키지 설치"""
    print(f"📦 {package} 설치 중... {description}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 설치 실패: {e}")
        return False


def check_import(module_name, package_name=None):
    """모듈 import 확인"""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False


def main():
    print("🚗 전기차 보조금 크롤러 빠른 설정")
    print("=" * 50)

    # 필수 라이브러리 확인
    required_packages = {
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'pandas': 'pandas'
    }

    print("🔍 필수 라이브러리 확인 중...")
    missing_packages = []

    for module, package in required_packages.items():
        if not check_import(module):
            missing_packages.append(package)
            print(f"❌ {package} 누락")
        else:
            print(f"✅ {package} 설치됨")

    # 누락된 필수 패키지 설치
    if missing_packages:
        print(f"\n📦 누락된 필수 패키지 설치 중...")
        for package in missing_packages:
            install_package(package)

    print("\n🚀 JavaScript 렌더링 라이브러리 설치 옵션:")
    print("1. requests-html (권장 - 간단함)")
    print("2. Playwright (고성능)")
    print("3. 설치하지 않음 (기본 requests만 사용)")

    choice = input("\n선택하세요 (1-3): ").strip()

    if choice == "1":
        print("\n🌐 requests-html 설치 중...")
        if install_package("requests-html"):
            print("✅ requests-html 설치 완료")
            print("💡 이제 JavaScript가 포함된 페이지도 크롤링할 수 있습니다!")

    elif choice == "2":
        print("\n🎭 Playwright 설치 중...")
        if install_package("playwright"):
            print("🔽 Playwright 브라우저 다운로드 중...")
            try:
                subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
                print("✅ Playwright 설치 완료")
                print("💡 고성능 브라우저 자동화가 활성화되었습니다!")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  브라우저 다운로드 실패: {e}")
                print("수동으로 실행해주세요: playwright install chromium")

    elif choice == "3":
        print("⚠️  기본 requests만 사용합니다.")
        print("JavaScript가 필요한 사이트에서는 제한적인 데이터만 수집됩니다.")

    # 크롤러 실행
    print("\n" + "=" * 50)
    run_crawler = input("지금 크롤러를 실행하시겠습니까? (y/n): ").strip().lower()

    if run_crawler in ['y', 'yes', '네', 'ㅇ']:
        print("\n🚀 전기차 보조금 크롤러 실행 중...")

        # 크롤러 import 및 실행
        try:
            # 현재 디렉토리에서 크롤러 모듈 import
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, current_dir)

            # 크롤러 파일이 있는지 확인
            crawler_file = os.path.join(current_dir, 'electric_car_subsidy_crawler.py')
            if not os.path.exists(crawler_file):
                crawler_file = os.path.join(current_dir, 'ev_crawler.py')

            if os.path.exists(crawler_file):
                print(f"📁 크롤러 파일 발견: {crawler_file}")

                # 크롤러 실행
                exec(open(crawler_file).read())

            else:
                print("❌ 크롤러 파일을 찾을 수 없습니다.")
                print("다음 파일 중 하나가 필요합니다:")
                print("- electric_car_subsidy_crawler.py")
                print("- ev_crawler.py")

        except Exception as e:
            print(f"❌ 크롤러 실행 중 오류: {e}")
            print("\n수동으로 실행해주세요:")
            print("python electric_car_subsidy_crawler.py")

    else:
        print("\n💡 크롤러 실행 방법:")
        print("python electric_car_subsidy_crawler.py")
        print("\n디버그 모드:")
        print("python electric_car_subsidy_crawler.py --debug")

    print("\n🎉 설정 완료!")


if __name__ == "__main__":
    main()