# ==========================================
# main.py - 자동매매 프로그램 진입점
# ==========================================
# 역할: 전체 프로그램의 흐름 제어 및 각 모듈 통합
# 실행 방법:
#   python main.py
#
# 동작 순서:
#   1. 모드 및 초기 자금 설정 (config.py)
#   2. 복리 자동 적용 (어제의 종료 예수금 → 오늘의 시작 예수금)
#   3. 종목 스캔 (stock_scanner.py)
#   4. 매수 추천 분석 (ai_predictor.py)
#   5. 리스크 점검 (risk_manager.py)
#   6. 매매 실행 또는 추천 출력 (trader.py)

import sys

# 모든 모듈 import
from logger import logger_instance
from config import MODE, INITIAL_DEPOSIT
from database import db_instance
from kiwoom_api import kiwoom_api
from stock_scanner import scanner
from ai_predictor import predictor
from risk_manager import risk_manager
from trader import trader


class AutoTrader:
    """자동매매 프로그램 메인 클래스"""

    def __init__(self):
        """프로그램 초기화"""
        logger_instance.info("자동매매 프로그램 시작...")
        logger_instance.info(f"실행 모드: {MODE}")

        self.today_balance = None
        self.recommendations = []

    def setup_initial_balance(self):
        """
        초기 자금 설정 및 복리 적용

        Returns:
            float: 오늘의 시작 예수금
        """
        logger_instance.info("\n[Step 1] 자금 설정")
        logger_instance.info("-" * 60)

        # 어제의 종료 예수금 조회 (복리 적용)
        yesterday_balance = risk_manager.update_balance_for_compound_interest()

        if yesterday_balance:
            self.today_balance = yesterday_balance
            logger_instance.info(f"✓ 복리 적용: {self.today_balance:,.0f}원")
        else:
            self.today_balance = INITIAL_DEPOSIT
            logger_instance.info(f"✓ 초기 자금: {self.today_balance:,.0f}원")

        return self.today_balance

    def scan_stocks(self):
        """
        투자 조건에 맞는 종목 스캔

        Returns:
            list: 조건 만족 종목 리스트
        """
        logger_instance.info("\n[Step 2] 종목 스캔")
        logger_instance.info("-" * 60)

        filtered_stocks = scanner.scan_stocks()

        if filtered_stocks:
            logger_instance.info(f"✓ 조건 충족 종목: {len(filtered_stocks)}개")
            for stock in filtered_stocks[:5]:  # 상위 5개만 표시
                logger_instance.info(
                    f"  - {stock['name']}({stock['code']}): {stock['price']:,.0f}원"
                )
            if len(filtered_stocks) > 5:
                logger_instance.info(f"  ... 외 {len(filtered_stocks) - 5}개")
        else:
            logger_instance.warning("✗ 조건 충족 종목 없음")

        return filtered_stocks

    def analyze_stocks(self, filtered_stocks):
        """
        조건 충족 종목을 분석하여 매수 추천 생성

        Args:
            filtered_stocks (list): 스캔된 종목 리스트

        Returns:
            list: 매수 추천 리스트
        """
        logger_instance.info("\n[Step 3] 개별 종목 분석")
        logger_instance.info("-" * 60)

        recommendations = []

        for stock in filtered_stocks:
            # ai_predictor에서 분석
            prediction = predictor.predict_stock(
                stock['code'],
                stock['name'],
                stock['price']
            )

            if prediction:
                recommendations.append(prediction)

        if recommendations:
            logger_instance.info(f"✓ 매수 추천 종목: {len(recommendations)}개")
        else:
            logger_instance.warning("✗ 신뢰도 충족 추천 종목 없음")

        self.recommendations = recommendations
        return recommendations

    def check_risks(self):
        """
        리스크 관리: 매수 전 안전성 확인

        Returns:
            bool: 거래 가능 여부
        """
        logger_instance.info("\n[Step 4] 리스크 점검")
        logger_instance.info("-" * 60)

        # 1. 매수 가능 여부
        if not risk_manager.can_buy_today():
            logger_instance.warning("✗ 오늘 매수 불가능")
            return False

        # 2. 일일 손실 한도
        # TODO: 누적 손실 조회 필요
        logger_instance.info("✓ 리스크 점검 완료")
        return True

    def execute_trades(self):
        """
        매수 추천을 바탕으로 거래 실행 (또는 분석 모드에서는 추천만 출력)

        Returns:
            list: 실행 결과
        """
        logger_instance.info("\n[Step 5] 거래 실행")
        logger_instance.info("-" * 60)

        if not self.recommendations:
            logger_instance.warning("✗ 실행할 추천 없음")
            return []

        execution_results = []

        # 첫 번째 추천 종목만 처리 (하루 1종목)
        recommendation = self.recommendations[0]
        stock_info = {
            'code': recommendation['stock_code'],
            'name': recommendation['stock_name'],
            'price': recommendation['current_price']
        }

        # trader에서 실행
        result = trader.execute_trade_for_stock(stock_info, self.today_balance)

        if result['success']:
            logger_instance.info(f"✓ 거래 실행 완료")
            execution_results.append(result)
        else:
            logger_instance.warning(f"✗ 거래 실행 실패: {result.get('message', '?')}")

        return execution_results

    def monitor_and_sell(self):
        """
        보유 중인 종목을 모니터링하고 매도 조건 확인 (자동 매도)

        실거래 모드에서만 작동:
        - 목표가 도달 → 자동 매도
        - 손절가 도달 → 자동 손절
        - 4거래일 경과 → 강제 매도
        """
        if MODE != "live":
            return

        logger_instance.info("\n[Step 6] 보유 종목 모니터링 & 자동 매도")
        logger_instance.info("-" * 60)

        # 진행 중인 거래 조회
        open_trades = db_instance.get_open_trades()

        if not open_trades:
            logger_instance.info("보유 종목 없음")
            return

        logger_instance.info(f"보유 종목: {len(open_trades)}개 모니터링 중...\n")

        for trade in open_trades:
            trade_id, buy_date, stock_code, stock_name, buy_price, buy_quantity = trade

            # 현재가 조회
            try:
                current_price = kiwoom_api.get_stock_info(stock_code)['price']
            except:
                logger_instance.warning(f"현재가 조회 실패: {stock_code}")
                continue

            # 매도 조건 확인
            result = trader.execute_sell_if_conditions_met(
                trade_id=trade_id,
                current_price=current_price,
                target_price=buy_price + 175,  # 목표: 한 주당 +175원
                buy_price=buy_price,
                stop_loss_price=buy_price * 0.97,  # 손절: -3%
                buy_date=buy_date,
                buy_quantity=buy_quantity
            )

            if result['success']:
                logger_instance.info(f"✓ {stock_name} 매도 완료")
            else:
                logger_instance.debug(f"○ {stock_name} 보유 중...")

    def generate_report(self, execution_results):
        """
        오늘의 실행 결과 최종 리포트

        Args:
            execution_results (list): 거래 실행 결과
        """
        logger_instance.info("\n[최종 리포트]")
        logger_instance.info("=" * 60)
        logger_instance.info(f"실행 모드:       {MODE}")
        logger_instance.info(f"오늘 시작 예수금: {self.today_balance:,.0f}원")
        logger_instance.info(f"종목 스캔 결과:  {len(self.recommendations)}개 추천")
        logger_instance.info(f"거래 실행:       {len(execution_results)}건")
        logger_instance.info("=" * 60)

        if self.recommendations:
            logger_instance.info("\n[오늘의 추천]")
            for i, rec in enumerate(self.recommendations[:3], 1):  # 상위 3개만
                logger_instance.info(
                    f"{i}. {rec['stock_name']}({rec['stock_code']})"
                )
                logger_instance.info(
                    f"   추천가: {rec['recommended_buy_price']:,.0f}원 → "
                    f"목표: {rec['target_sell_price']:,.0f}원 "
                    f"(신뢰도: {rec['confidence']}%)"
                )

    def run(self):
        """
        프로그램 전체 실행

        Returns:
            int: 종료 코드 (0 = 정상, 1 = 오류)
        """
        try:
            # Step 1: 자금 설정
            self.setup_initial_balance()

            # Step 2: 종목 스캔
            filtered_stocks = self.scan_stocks()

            if not filtered_stocks:
                logger_instance.warning("조건 충족 종목이 없어 분석을 종료합니다.")
                return 0

            # Step 3: 개별 종목 분석
            self.analyze_stocks(filtered_stocks)

            if not self.recommendations:
                logger_instance.warning("신뢰도 충족 종목이 없어 거래를 진행하지 않습니다.")
                return 0

            # Step 4: 리스크 점검
            if not self.check_risks():
                return 1

            # Step 5: 거래 실행 (또는 분석 모드에서는 추천 출력)
            execution_results = self.execute_trades()

            # Step 6: 보유 종목 모니터링 & 자동 매도 (실거래 모드만)
            self.monitor_and_sell()

            # Step 7: 최종 리포트
            self.generate_report(execution_results)

            logger_instance.info("\n✓ 프로그램 정상 종료")
            return 0

        except KeyboardInterrupt:
            logger_instance.warning("\n사용자가 프로그램을 중단했습니다")
            return 1
        except Exception as e:
            logger_instance.error(f"프로그램 오류: {e}")
            return 1
        finally:
            # 데이터베이스 종료
            db_instance.close()
            logger_instance.info("리소스 정리 완료")


def print_usage():
    """사용법 출력"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║        키움증권 OpenAPI+ 자동매매 프로그램 (makemeRich)        ║
╚════════════════════════════════════════════════════════════════╝

사용법:
  python main.py

설정 방법:
  1. config.py에서 MODE를 선택하세요
     - "analysis"  : 분석만 (주문 없음) ← 추천
     - "backtest"  : 백테스트
     - "paper"     : 모의투자
     - "live"      : 실거래

  2. config.py에서 INITIAL_DEPOSIT을 설정하세요 (초기 자금)

주의사항:
  ⚠️  Windows 32bit Python 필수
  ⚠️  첫 실행 시 분석 모드(MODE="analysis")로 시작 권장
  ⚠️  백테스트 후 모의투자, 최종적으로 실거래 진행

로그 파일:
  - logs/ 폴더에 날짜별로 저장됩니다
  - 예: logs/2026-05-16.log

더 많은 정보:
  - plan 파일: /Users/hwangchaewon/.claude/plans/openapi-swirling-sonnet.md
  - 코드 주석을 참고하세요
""")


# ==========================================
# 프로그램 진입점
# ==========================================
if __name__ == "__main__":
    # 사용법 출력
    print_usage()

    # 프로그램 실행
    auto_trader = AutoTrader()
    exit_code = auto_trader.run()

    sys.exit(exit_code)

# ==========================================
# 추가 기능 (나중에 구현 예정)
# ==========================================
# 1. 커맨드라인 인자 처리
#    python main.py --mode paper --initial 5000000
#
# 2. 모니터링 및 정기 실행
#    - 매일 09:00에 자동 실행
#    - 보유 종목 매도 여부 확인 (15:30)
#
# 3. 웹 대시보드
#    - 오늘의 추천 종목 확인
#    - 일별 수익/손실 그래프
#    - 거래 기록 조회