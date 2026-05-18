# ==========================================
# stock_scanner.py - 투자 조건에 맞는 종목 스캔
# ==========================================
# 역할: 전체 주식에서 가격 1만~5만 원, 거래량 충분 등의 조건을 만족하는 종목 찾기
# 예: 005930(삼성전자, 70000원) → 범위 초과 제외
#    068270(셀트리온, 25000원) → 조건 만족! ✓

from logger import logger_instance
from kiwoom_api import kiwoom_api
from config import (
    MIN_PRICE, MAX_PRICE, MIN_VOLUME,
    EXCLUDE_ETF, EXCLUDE_PREFERRED_STOCK
)


class StockScanner:
    """투자 조건에 맞는 종목을 찾는 스캐너"""

    def __init__(self):
        """스캐너 초기화"""
        self.filtered_stocks = []  # 조건을 만족하는 종목 리스트

    def scan_stocks(self):
        """
        조건에 맞는 종목 스캔

        Returns:
            list: 조건 만족 종목 리스트
                [
                    {'code': '068270', 'name': '셀트리온', 'price': 25000, 'volume': 1500000},
                    {'code': '035720', 'name': '카카오', 'price': 32000, 'volume': 2000000},
                    ...
                ]
        """
        logger_instance.info("종목 스캔 시작...")

        # 1단계: 전체 종목 코드 로드
        all_stocks = kiwoom_api.load_all_stocks()
        if not all_stocks:
            logger_instance.error("종목 로드 실패")
            return []

        logger_instance.info(f"전체 종목: {len(all_stocks)}개")

        # 2단계: 각 종목을 하나씩 검사
        self.filtered_stocks = []
        for stock_code, stock_name in all_stocks.items():
            # 조건 검사
            if self._check_stock_conditions(stock_code, stock_name):
                self.filtered_stocks.append({
                    'code': stock_code,
                    'name': stock_name,
                    'price': self._get_current_price(stock_code),
                    'volume': self._get_current_volume(stock_code),
                })

        logger_instance.info(f"조건 만족 종목: {len(self.filtered_stocks)}개")
        return self.filtered_stocks

    def _check_stock_conditions(self, stock_code, stock_name):
        """
        종목이 투자 조건을 만족하는지 검사

        Args:
            stock_code (str): 종목 코드
            stock_name (str): 종목명

        Returns:
            bool: 조건 만족하면 True
        """

        # 조건 1: ETF 제외
        if EXCLUDE_ETF and self._is_etf(stock_code, stock_name):
            logger_instance.debug(f"제외: {stock_name} (ETF)")
            return False

        # 조건 2: 우선주 제외 (보통주가 아님)
        if EXCLUDE_PREFERRED_STOCK and self._is_preferred_stock(stock_code, stock_name):
            logger_instance.debug(f"제외: {stock_name} (우선주)")
            return False

        # 조건 3: 현재가 범위 (1만~5만 원)
        current_price = self._get_current_price(stock_code)
        if not (MIN_PRICE <= current_price <= MAX_PRICE):
            logger_instance.debug(f"제외: {stock_name} ({current_price}원) - 가격 범위 초과")
            return False

        # 조건 4: 거래량 (일정 이상)
        current_volume = self._get_current_volume(stock_code)
        if current_volume < MIN_VOLUME:
            logger_instance.debug(f"제외: {stock_name} ({current_volume}주) - 거래량 부족")
            return False

        # 모든 조건 만족!
        logger_instance.debug(f"포함: {stock_name} ({current_price}원, {current_volume}주)")
        return True

    def _is_etf(self, stock_code, stock_name):
        """
        ETF인지 확인

        Args:
            stock_code (str): 종목 코드
            stock_name (str): 종목명

        Returns:
            bool: ETF이면 True
        """
        # 간단한 방법: 종목명에 "ETF" 포함 여부
        # 실제로는 키움 API의 "상품 구분" 정보를 확인해야 함
        if "ETF" in stock_name.upper():
            return True

        # 특정 코드 범위도 ETF인지 확인 가능
        # 예: 130000~139999번 (투자 회사 ETF)
        code_int = int(stock_code)
        if 130000 <= code_int <= 139999:
            return True

        return False

    def _is_preferred_stock(self, stock_code, stock_name):
        """
        우선주인지 확인

        Args:
            stock_code (str): 종목 코드
            stock_name (str): 종목명

        Returns:
            bool: 우선주이면 True
        """
        # 간단한 방법: 종목명에 "우B", "우", "우선" 포함 여부
        if any(x in stock_name for x in ["우B", "우A", "우", "우선"]):
            return True

        # 특정 코드 범위도 우선주 (실제로는 거래소 분류를 확인해야 함)
        code_int = int(stock_code)

        # 삼성전자 우선주 (005935), LG전자 우선주 (066575) 등
        preferred_codes = [5935, 66575, 11570, 11580, 51910]
        if code_int in preferred_codes:
            return True

        return False

    def _get_current_price(self, stock_code):
        """
        종목 현재가 조회

        Args:
            stock_code (str): 종목 코드

        Returns:
            float: 현재가
        """
        try:
            info = kiwoom_api.get_stock_info(stock_code)
            if info and 'price' in info:
                return info['price']
        except Exception as e:
            logger_instance.debug(f"현재가 조회 실패 ({stock_code}): {e}")

        return 0.0

    def _get_current_volume(self, stock_code):
        """
        종목 거래량 조회

        Args:
            stock_code (str): 종목 코드

        Returns:
            int: 거래량
        """
        try:
            info = kiwoom_api.get_stock_info(stock_code)
            if info and 'volume' in info:
                return info['volume']
        except Exception as e:
            logger_instance.debug(f"거래량 조회 실패 ({stock_code}): {e}")

        return 0

    def get_filtered_stocks(self):
        """
        마지막 스캔 결과 반환

        Returns:
            list: 조건 만족 종목 리스트
        """
        return self.filtered_stocks

    def filter_by_price_range(self, min_price, max_price):
        """
        가격 범위로 추가 필터링

        Args:
            min_price (float): 최소 가격
            max_price (float): 최대 가격

        Returns:
            list: 필터링된 종목
        """
        filtered = [
            s for s in self.filtered_stocks
            if min_price <= s['price'] <= max_price
        ]
        logger_instance.info(f"가격 범위 필터링: {len(filtered)}개")
        return filtered

    def filter_by_volume(self, min_volume):
        """
        거래량으로 추가 필터링

        Args:
            min_volume (int): 최소 거래량

        Returns:
            list: 필터링된 종목
        """
        filtered = [
            s for s in self.filtered_stocks
            if s['volume'] >= min_volume
        ]
        logger_instance.info(f"거래량 필터링: {len(filtered)}개")
        return filtered


# 프로그램 어디서나 이 스캐너를 사용하기 위해 전역 인스턴스 생성
scanner = StockScanner()

# ==========================================
# 사용 예시
# ==========================================
# from stock_scanner import scanner
#
# # 종목 스캔 (모든 조건 적용)
# filtered_stocks = scanner.scan_stocks()
#
# # 결과 출력
# for stock in filtered_stocks:
#     print(f"{stock['name']}({stock['code']}) - {stock['price']}원, {stock['volume']}주")
#
# # 추가 필터링
# high_volume_stocks = scanner.filter_by_volume(min_volume=2000000)
