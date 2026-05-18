# ==========================================
# logger.py - 프로그램 전체에서 사용할 로깅 모듈
# ==========================================
# 역할: 프로그램 실행 중의 모든 정보를 파일과 콘솔에 동시에 저장
# 예: "[2026-05-16 09:15:00] 스캔 완료: 조건 충족 종목 12개"

import logging
import os
from datetime import datetime


class Logger:
    """프로그램 전체에서 사용할 통합 로거"""

    def __init__(self, log_dir="logs"):
        """
        로거 초기화

        Args:
            log_dir (str): 로그 파일을 저장할 디렉토리 경로
        """
        # 로그 디렉토리 생성 (없으면 자동 생성)
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 오늘 날짜를 이용해 로그 파일명 생성 (예: logs/2026-05-16.log)
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(log_dir, f"{today}.log")

        # Python의 기본 logger 객체 설정
        self.logger = logging.getLogger("MakeMeRich")
        self.logger.setLevel(logging.DEBUG)  # 모든 로그 레벨 기록

        # 이미 handler가 있으면 중복 방지
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 로그 포맷: [시간] 레벨 - 메시지
        # 예: [2026-05-16 09:15:00] INFO - 스캔 완료
        log_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 파일에 로그 저장 (UTF-8 인코딩)
        file_handler = logging.FileHandler(
            self.log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        self.logger.addHandler(file_handler)

        # 콘솔(화면)에도 로그 출력
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(log_format)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """일반 정보 로그 (초록색)"""
        self.logger.info(message)

    def warning(self, message):
        """경고 로그 (노란색)"""
        self.logger.warning(message)

    def error(self, message):
        """오류 로그 (빨간색)"""
        self.logger.error(message)

    def debug(self, message):
        """디버그 로그 (개발 시 상세 정보)"""
        self.logger.debug(message)


# 프로그램 어디서나 이 logger를 사용하기 위해 전역 인스턴스 생성
logger_instance = Logger()


# ==========================================
# 사용 예시
# ==========================================
# 다른 파일에서:
# from logger import logger_instance
# logger_instance.info("스캔 완료: 조건 충족 종목 12개")
# logger_instance.error("API 연결 실패")
