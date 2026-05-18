# ==========================================
# kiwoom_api.py - 키움증권 OpenAPI+ 연결 및 데이터 수신
# ==========================================
# 역할: 키움 API를 통해 현재가, 분봉, 일봉 데이터를 수신
# 주의: Windows 32bit Python에서만 동작
# 주의: "분석 모드"에서는 실제 API 호출 없음 (목 데이터 사용)

import time
from abc import ABC
from logger import logger_instance
from config import MODE, API_REQUEST_DELAY


class KiwoomAPI:
    """키움증권 OpenAPI+ 연결 및 데이터 수신"""

    def __init__(self):
        """
        키움 API 초기화
        실제 구현은 Windows 환경에서만 가능
        """
        self.is_connected = False
        self.account_number = None
        self.all_stocks = {}  # 전체 종목 코드와 이름

        # 분석/백테스트 모드에서는 API 연결하지 않음
        if MODE in ["analysis", "backtest"]:
            logger_instance.info(f"[{MODE} 모드] 키움 API 연결 스킵")
            return

        # 실거래/모의 모드에서만 API 연결
        try:
            self._connect_to_api()
        except Exception as e:
            logger_instance.error(f"키움 API 연결 실패: {e}")

    def _connect_to_api(self):
        """
        키움 API 실제 연결 (Windows 32bit에서만)
        ⚠️ 아직 구현 중 - Windows 환경에서만 실행 가능
        """
        # PyQt5와 COM 객체 초기화는 나중에 구현
        # 1. QAxWidget 생성
        # 2. SetInputValue / CommRqData로 TR 요청
        # 3. OnReceiveTrData 콜백으로 응답 처리
        logger_instance.warning("Windows 환경에서 키움 API 연결 구현 필요")

    # ==========================================
    # 계좌 관련 함수
    # ==========================================

    def login(self, user_id, password):
        """
        키움증권 로그인

        Args:
            user_id (str): 키움 로그인 ID
            password (str): 키움 로그인 비밀번호

        Returns:
            bool: 로그인 성공 여부
        """
        if MODE in ["analysis", "backtest"]:
            logger_instance.info("[분석 모드] 로그인 스킵")
            self.is_connected = True
            return True

        try:
            # 실제 로그인 로직은 Windows에서만 구현
            logger_instance.info("키움증권 로그인 시도...")
            # 추후 구현
            return False
        except Exception as e:
            logger_instance.error(f"로그인 실패: {e}")
            return False

    def get_account_number(self):
        """
        보유 계좌 조회

        Returns:
            str: 계좌 번호 (예: "1234567890")
        """
        if MODE in ["analysis", "backtest"]:
            return "1234567890"  # 테스트용 샘플 계좌

        try:
            # 실제 구현: SetInputValue("ACCNO", ...) / CommRqData(...)
            pass
        except Exception as e:
            logger_instance.error(f"계좌 조회 실패: {e}")
        return None

    def get_account_balance(self):
        """
        현재 예수금 조회

        Returns:
            float: 예수금 (예: 1000000.0)
        """
        if MODE in ["analysis", "backtest"]:
            return 1000000.0  # 테스트용 샘플

        try:
            # 실제 구현: SetInputValue / CommRqData
            pass
        except Exception as e:
            logger_instance.error(f"예수금 조회 실패: {e}")
        return 0.0

    # ==========================================
    # 종목 정보 관련 함수
    # ==========================================

    def load_all_stocks(self):
        """
        전체 주식 종목 코드 및 이름 로드
        반환: {'005930': '삼성전자', '000660': 'SK하이닉스', ...}

        Returns:
            dict: 종목 코드와 이름의 딕셔너리
        """
        if MODE in ["analysis", "backtest"]:
            # 테스트용 샘플 데이터
            self.all_stocks = {
                '005930': '삼성전자',
                '000660': 'SK하이닉스',
                '068270': '셀트리온',
                '035720': '카카오',
                '207940': '삼성바이오로직스',
                '006400': '삼성SDI',
                '005380': '현대차',
                '051910': 'LG화학',
                '010950': '오스코텍',
                '003670': '포스코인터내셔널',
            }
            logger_instance.info(f"[샘플 데이터] 종목 {len(self.all_stocks)}개 로드")
            return self.all_stocks

        try:
            # 실제 구현: 키움 API에서 전체 종목 조회
            logger_instance.info("키움 API에서 전체 종목 로드 중...")
            # SetInputValue / CommRqData 사용
            pass
        except Exception as e:
            logger_instance.error(f"종목 로드 실패: {e}")
        return {}

    def get_stock_info(self, stock_code):
        """
        특정 종목의 정보 조회

        Args:
            stock_code (str): 종목 코드 (예: "005930")

        Returns:
            dict: {'name': 종목명, 'price': 현재가, 'volume': 거래량, ...}
        """
        time.sleep(API_REQUEST_DELAY)  # API 요청 간격 준수

        if MODE in ["analysis", "backtest"]:
            # 테스트용 샘플 데이터
            sample_data = {
                '005930': {'name': '삼성전자', 'price': 70000, 'volume': 5000000, 'market_cap': 430000000000000},
                '000660': {'name': 'SK하이닉스', 'price': 180000, 'volume': 3000000, 'market_cap': 180000000000000},
            }
            if stock_code in sample_data:
                return sample_data[stock_code]
            else:
                return {'name': '테스트종목', 'price': 25000, 'volume': 1000000}

        try:
            # 실제 구현: opt10001 (현재가 정보 요청)
            logger_instance.debug(f"종목 정보 조회: {stock_code}")
            # SetInputValue("종목코드", stock_code) / CommRqData(...)
            pass
        except Exception as e:
            logger_instance.error(f"종목 정보 조회 실패 ({stock_code}): {e}")
        return None

    # ==========================================
    # 가격 데이터 관련 함수
    # ==========================================

    def get_minute_candles(self, stock_code, minute=5, count=20):
        """
        분봉 데이터 조회 (예: 5분봉 최근 20개)

        Args:
            stock_code (str): 종목 코드
            minute (int): 분봉 타입 (1, 5, 15분 등)
            count (int): 조회 개수

        Returns:
            list: [{'time': '09:30', 'open': 70000, 'high': 70200, 'low': 69800, 'close': 70100, 'volume': 500000}, ...]
        """
        time.sleep(API_REQUEST_DELAY)

        if MODE in ["analysis", "backtest"]:
            # 테스트용 샘플 분봉 데이터
            logger_instance.debug(f"[샘플] {stock_code} {minute}분봉 {count}개 반환")
            return [
                {'time': '09:30', 'open': 23450, 'high': 23600, 'low': 23400, 'close': 23550, 'volume': 100000},
                {'time': '09:35', 'open': 23550, 'high': 23700, 'low': 23500, 'close': 23650, 'volume': 110000},
                {'time': '09:40', 'open': 23650, 'high': 23800, 'low': 23600, 'close': 23750, 'volume': 120000},
            ]

        try:
            # 실제 구현: opt10080 (분봉 조회)
            logger_instance.debug(f"{minute}분봉 조회: {stock_code}")
            # SetInputValue("종목코드", stock_code) / SetInputValue("틱기간", minute)
            pass
        except Exception as e:
            logger_instance.error(f"분봉 조회 실패 ({stock_code}): {e}")
        return []

    def get_daily_candles(self, stock_code, count=60):
        """
        일봉 데이터 조회 (최근 N일)

        Args:
            stock_code (str): 종목 코드
            count (int): 조회 일수

        Returns:
            list: [{'date': '2026-05-15', 'open': 70000, 'high': 70500, 'low': 69800, 'close': 70200, 'volume': 5000000}, ...]
        """
        time.sleep(API_REQUEST_DELAY)

        if MODE in ["analysis", "backtest"]:
            # 테스트용 샘플 일봉 데이터
            logger_instance.debug(f"[샘플] {stock_code} 일봉 {count}개 반환")
            return [
                {'date': '2026-05-15', 'open': 23400, 'high': 23600, 'low': 23300, 'close': 23500, 'volume': 3000000},
                {'date': '2026-05-14', 'open': 23300, 'high': 23500, 'low': 23100, 'close': 23400, 'volume': 2800000},
                {'date': '2026-05-13', 'open': 23200, 'high': 23400, 'low': 23000, 'close': 23300, 'volume': 3100000},
            ]

        try:
            # 실제 구현: opt10081 (일봉 조회)
            logger_instance.debug(f"일봉 조회: {stock_code}")
            # SetInputValue("종목코드", stock_code)
            pass
        except Exception as e:
            logger_instance.error(f"일봉 조회 실패 ({stock_code}): {e}")
        return []

    # ==========================================
    # 거래 관련 함수
    # ==========================================

    def place_order(self, stock_code, quantity, price, order_type="buy"):
        """
        매수/매도 주문

        Args:
            stock_code (str): 종목 코드
            quantity (int): 주문 수량
            price (float): 주문 가격
            order_type (str): "buy" 또는 "sell"

        Returns:
            str: 주문 번호 또는 None (실패 시)
        """
        if MODE == "analysis":
            logger_instance.warning("분석 모드: 주문 불가능")
            return None

        try:
            logger_instance.info(
                f"주문 요청: {order_type.upper()} {stock_code} {quantity}주 @ {price}원"
            )
            # 실제 구현: SetInputValue / CommRqData
            # 모의 모드 vs 실거래 분기 처리 필요
            pass
        except Exception as e:
            logger_instance.error(f"주문 실패: {e}")
        return None

    # ==========================================
    # 유틸리티 함수
    # ==========================================

    def is_market_open(self):
        """
        현재 시간이 장 시간인지 확인

        Returns:
            bool: 장 시간이면 True
        """
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        today_weekday = now.weekday()  # 0=월, 4=금, 5=토, 6=일

        # 토일요일 제외
        if today_weekday >= 5:
            return False

        # 09:00 ~ 15:30
        current_time_minutes = hour * 60 + minute
        market_open = 9 * 60  # 09:00
        market_close = 15 * 60 + 30  # 15:30

        return market_open <= current_time_minutes <= market_close

    def disconnect(self):
        """API 연결 종료"""
        if self.is_connected:
            logger_instance.info("키움 API 연결 종료")
            self.is_connected = False


# 프로그램 어디서나 이 API를 사용하기 위해 전역 인스턴스 생성
kiwoom_api = KiwoomAPI()

# ==========================================
# 사용 예시
# ==========================================
# from kiwoom_api import kiwoom_api
#
# # 로그인
# kiwoom_api.login("user_id", "password")
#
# # 전체 종목 로드
# all_stocks = kiwoom_api.load_all_stocks()
#
# # 특정 종목 정보 조회
# info = kiwoom_api.get_stock_info("005930")
#
# # 5분봉 조회
# candles = kiwoom_api.get_minute_candles("005930", minute=5, count=20)
#
# # 현재 장 시간인지 확인
# if kiwoom_api.is_market_open():
#     print("장 시간입니다")
