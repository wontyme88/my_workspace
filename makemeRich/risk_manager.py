# ==========================================
# risk_manager.py - 리스크 관리 및 매매 전 점검
# ==========================================
# 역할: 매수 전 안전성 확인, 4거래일 강제 청산, 손절 신호 감지
# 예: "예수금 부족" → 매수 중단
#    "4거래일 경과" → 강제 매도
#    "손절가 도달" → 손절 신호

from datetime import datetime, timedelta
from logger import logger_instance
from database import db_instance
from config import MAX_HOLD_DAYS, MAX_DAILY_LOSS_PERCENT, MAX_CONCURRENT_STOCKS


class RiskManager:
    """리스크 관리 및 매매 안전성 점검"""

    def __init__(self):
        """리스크 관리자 초기화"""
        pass

    # ==========================================
    # 매수 전 점검
    # ==========================================

    def can_buy_today(self):
        """
        오늘 매수 가능한지 확인
        (하루에 1종목만 거래)

        Returns:
            bool: 매수 가능하면 True
        """
        # 1. 진행 중인 거래 확인
        open_trades = db_instance.get_open_trades()
        if len(open_trades) >= MAX_CONCURRENT_STOCKS:
            logger_instance.warning(
                f"이미 {len(open_trades)}개 종목 보유 중 - 매수 불가"
            )
            return False

        # 2. 오늘 이미 거래했는지 확인
        today = datetime.now().strftime("%Y-%m-%d")
        # TODO: 오늘의 거래 기록 조회 (database.py 함수 필요)

        logger_instance.info("매수 조건 확인: OK ✓")
        return True

    def can_afford_buy(self, stock_price, quantity, current_balance):
        """
        충분한 예수금이 있는지 확인

        Args:
            stock_price (float): 주식 현재가
            quantity (int): 매수 수량
            current_balance (float): 현재 예수금

        Returns:
            tuple: (가능 여부, 필요 금액)
        """
        required_amount = stock_price * quantity

        if required_amount > current_balance:
            logger_instance.warning(
                f"예수금 부족: 필요 {required_amount:.0f}원, 보유 {current_balance:.0f}원"
            )
            return False, required_amount

        logger_instance.info(
            f"예수금 확인: OK ✓ ({current_balance:.0f}원 > {required_amount:.0f}원)"
        )
        return True, required_amount

    def check_daily_loss_limit(self, total_loss, current_balance):
        """
        일일 손실 한도 초과 확인

        Args:
            total_loss (float): 누적 손실
            current_balance (float): 현재 예수금

        Returns:
            bool: 한도 내면 True, 초과하면 False
        """
        # 원래 자금 추정 (현재 잔액 + 손실)
        initial_balance = current_balance + abs(total_loss)
        loss_percent = (abs(total_loss) / initial_balance) * 100

        if loss_percent > MAX_DAILY_LOSS_PERCENT:
            logger_instance.warning(
                f"일일 손실 한도 초과: {loss_percent:.1f}% > {MAX_DAILY_LOSS_PERCENT}%"
            )
            return False

        logger_instance.info(f"손실 한도 확인: OK ✓ ({loss_percent:.1f}% < {MAX_DAILY_LOSS_PERCENT}%)")
        return True

    # ==========================================
    # 보유 중 점검
    # ==========================================

    def check_holding_days(self, buy_date):
        """
        보유 기간 초과 확인 (4거래일 초과)

        Args:
            buy_date (str): 매수 날짜 (YYYY-MM-DD)

        Returns:
            tuple: (초과 여부, 보유 거래일 수)
        """
        try:
            buy_datetime = datetime.strptime(buy_date, "%Y-%m-%d")
            today = datetime.now()

            # 거래일 수 계산 (토일 제외)
            trading_days = 0
            current = buy_datetime
            while current < today:
                # 월~금만 카운트 (0=월, 4=금, 5=토, 6=일)
                if current.weekday() < 5:
                    trading_days += 1
                current += timedelta(days=1)

            if trading_days > MAX_HOLD_DAYS:
                logger_instance.warning(
                    f"보유 기간 초과: {trading_days}일 > {MAX_HOLD_DAYS}일 - 강제 매도 필요"
                )
                return True, trading_days

            logger_instance.debug(f"보유 기간: {trading_days}일 (허용: {MAX_HOLD_DAYS}일)")
            return False, trading_days

        except Exception as e:
            logger_instance.error(f"보유 기간 계산 실패: {e}")
            return False, 0

    def check_stop_loss(self, current_price, buy_price, stop_loss_price):
        """
        손절가 도달 확인

        Args:
            current_price (float): 현재 주가
            buy_price (float): 매수 단가
            stop_loss_price (float): 손절가

        Returns:
            tuple: (손절 필요 여부, 손실률)
        """
        loss_percent = ((current_price - buy_price) / buy_price) * 100

        if current_price <= stop_loss_price:
            logger_instance.warning(
                f"손절가 도달: {current_price}원 <= {stop_loss_price}원 ({loss_percent:.1f}%) - 매도 필요"
            )
            return True, loss_percent

        logger_instance.debug(f"손실률: {loss_percent:.1f}% (손절: {stop_loss_price}원)")
        return False, loss_percent

    def check_profit_target(self, current_price, target_sell_price):
        """
        목표가 도달 확인 (수익 실현)

        Args:
            current_price (float): 현재 주가
            target_sell_price (float): 목표 매도가

        Returns:
            tuple: (목표가 도달 여부, 수익률)
        """
        profit_percent = ((current_price - target_sell_price) / target_sell_price) * 100

        if current_price >= target_sell_price:
            logger_instance.info(
                f"목표가 도달: {current_price}원 >= {target_sell_price}원 ({profit_percent:.1f}%) - 매도 가능"
            )
            return True, profit_percent

        logger_instance.debug(f"목표까지: {target_sell_price - current_price:.0f}원 남음")
        return False, profit_percent

    # ==========================================
    # 일일 리포트
    # ==========================================

    def generate_daily_report(self, start_balance, end_balance, trades_today):
        """
        일일 수익/손실 리포트 생성

        Args:
            start_balance (float): 시작 예수금
            end_balance (float): 종료 예수금
            trades_today (list): 오늘의 거래 기록

        Returns:
            dict: {
                'date': '2026-05-16',
                'start_balance': 1000000,
                'profit_loss': 5000,
                'profit_percent': 0.5,
                'end_balance': 1005000,
                'trade_count': 1,
                'win_count': 1,
                'loss_count': 0,
                'win_rate': 100.0,
                'report_text': "..."
            }
        """
        today = datetime.now().strftime("%Y-%m-%d")
        profit_loss = end_balance - start_balance
        profit_percent = (profit_loss / start_balance) * 100 if start_balance > 0 else 0

        # 승/패 분석
        win_count = 0
        loss_count = 0
        for trade in trades_today:
            if trade.get('profit_loss', 0) > 0:
                win_count += 1
            elif trade.get('profit_loss', 0) < 0:
                loss_count += 1

        win_rate = (win_count / len(trades_today)) * 100 if trades_today else 0

        # 리포트 텍스트 생성
        report_text = f"""
{'='*50}
[{today}] 일일 거래 리포트
{'='*50}
시작 예수금:    {start_balance:>15,.0f}원
종료 예수금:    {end_balance:>15,.0f}원
일일 수익/손실: {profit_loss:>15,.0f}원 ({profit_percent:+.2f}%)

거래 통계:
├─ 거래 횟수: {len(trades_today)}건
├─ 승리: {win_count}건
├─ 패배: {loss_count}건
└─ 승률: {win_rate:.1f}%

{'='*50}
"""

        report = {
            'date': today,
            'start_balance': start_balance,
            'profit_loss': profit_loss,
            'profit_percent': profit_percent,
            'end_balance': end_balance,
            'trade_count': len(trades_today),
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': win_rate,
            'report_text': report_text
        }

        logger_instance.info(report_text)
        return report

    # ==========================================
    # 복리 처리
    # ==========================================

    def update_balance_for_compound_interest(self):
        """
        어제의 종료 예수금을 오늘의 시작 예수금으로 설정 (복리)

        Returns:
            float: 오늘 시작할 예수금
        """
        today = datetime.now().strftime("%Y-%m-%d")

        # 어제의 종료 예수금 조회
        yesterday_balance = db_instance.get_yesterday_balance()

        if yesterday_balance:
            logger_instance.info(f"복리 적용: 어제 종료 {yesterday_balance:,.0f}원 → 오늘 시작")

            # 오늘 데이터 생성 (아직 수익 없음)
            db_instance.insert_daily_balance(
                date=today,
                start_balance=yesterday_balance,
                profit_loss=0,
                end_balance=yesterday_balance
            )

            return yesterday_balance
        else:
            # 첫 거래일: 초기 자금으로 시작 (config.py에서 받음)
            from config import INITIAL_DEPOSIT
            logger_instance.info(f"첫 거래일: 초기 자금 {INITIAL_DEPOSIT:,.0f}원으로 시작")

            db_instance.insert_daily_balance(
                date=today,
                start_balance=INITIAL_DEPOSIT,
                profit_loss=0,
                end_balance=INITIAL_DEPOSIT
            )

            return INITIAL_DEPOSIT


# 프로그램 어디서나 이 리스크 관리자를 사용하기 위해 전역 인스턴스 생성
risk_manager = RiskManager()

# ==========================================
# 사용 예시
# ==========================================
# from risk_manager import risk_manager
#
# # 매수 가능한지 확인
# if risk_manager.can_buy_today():
#     # 예수금 확인
#     can_afford, required = risk_manager.can_afford_buy(25000, 40, 1000000)
#     if can_afford:
#         print("매수 진행!")
#
# # 보유 중 점검
# is_over, days = risk_manager.check_holding_days("2026-05-12")
# if is_over:
#     print(f"{days}일 경과 - 강제 매도 필요")
#
# # 목표가 도달 확인
# is_target, profit = risk_manager.check_profit_target(25150, 25175)
# if is_target:
#     print(f"목표가 도달! 수익률: {profit:.1f}%")
#
# # 일일 리포트
# report = risk_manager.generate_daily_report(1000000, 1005000, [])
# print(report['report_text'])
