# ==========================================
# backtest.py - 백테스트 (과거 데이터로 전략 검증)
# ==========================================
# 역할: 과거 N개월 데이터로 우리의 매매 전략이 얼마나 잘 작동했는지 시뮬레이션
# 출력: 승률, 평균 수익, 최대 손실폭(MDD), 복리 그래프
#
# 예: "2026년 1월~3월 데이터로 백테스트하면 60% 승률, 월 +15% 수익"
#
# 실행 방법:
#   config.py에서 MODE = "backtest" 설정
#   python main.py

from datetime import datetime, timedelta
from logger import logger_instance
from database import db_instance
from config import (
    TARGET_PROFIT, STOP_LOSS_PERCENT, MAX_HOLD_DAYS,
    MIN_PRICE, MAX_PRICE, MIN_CONFIDENCE
)


class BacktestEngine:
    """백테스트 엔진"""

    def __init__(self, initial_balance=1000000, start_date=None, end_date=None):
        """
        백테스트 초기화

        Args:
            initial_balance (float): 초기 자금
            start_date (str): 테스트 시작 날짜 (YYYY-MM-DD), None이면 6개월 전
            end_date (str): 테스트 종료 날짜 (YYYY-MM-DD), None이면 오늘
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.trades = []  # 거래 기록
        self.daily_balances = []  # 일별 잔액

        # 날짜 범위 설정
        if end_date is None:
            self.end_date = datetime.now().strftime("%Y-%m-%d")
        else:
            self.end_date = end_date

        if start_date is None:
            # 기본값: 6개월 전
            start_datetime = datetime.strptime(self.end_date, "%Y-%m-%d") - timedelta(days=180)
            self.start_date = start_datetime.strftime("%Y-%m-%d")
        else:
            self.start_date = start_date

        logger_instance.info(
            f"백테스트 준비: {self.start_date} ~ {self.end_date}, 초기 자금 {initial_balance:,.0f}원"
        )

    def run(self):
        """
        백테스트 실행

        Returns:
            dict: {
                'initial_balance': 1000000,
                'final_balance': 1200000,
                'total_profit': 200000,
                'total_profit_percent': 20.0,
                'win_count': 12,
                'loss_count': 8,
                'win_rate': 60.0,
                'avg_profit': 16666.67,
                'max_loss': 50000,
                'max_drawdown': 5.0,
                'sharpe_ratio': 1.5
            }
        """
        logger_instance.info("백테스트 시작...")

        # TODO: 과거 데이터 조회 및 시뮬레이션
        # 1. DB에서 과거 가격 데이터 조회
        # 2. 날짜별로 반복:
        #    - stock_scanner로 조건 충족 종목 찾기
        #    - ai_predictor로 매수 신호 분석
        #    - 매수 시뮬레이션
        #    - 매도 신호 확인
        #    - 손익 계산

        logger_instance.warning("백테스트 상세 구현은 나중에 완성 예정")

        # 임시 샘플 결과
        result = {
            'initial_balance': self.initial_balance,
            'final_balance': self.initial_balance * 1.15,  # 15% 수익 가정
            'total_profit': self.initial_balance * 0.15,
            'total_profit_percent': 15.0,
            'win_count': 12,
            'loss_count': 8,
            'win_rate': 60.0,
            'avg_profit': 15000,
            'max_loss': 50000,
            'max_drawdown': 5.0,
            'sharpe_ratio': 1.5,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'trade_count': 20
        }

        self.current_balance = result['final_balance']

        return result

    def get_performance_report(self, result):
        """
        성과 리포트 생성

        Args:
            result (dict): 백테스트 결과

        Returns:
            str: 포맷된 리포트
        """
        report = f"""
{'='*60}
[백테스트 결과]
{'='*60}

테스트 기간:    {result['start_date']} ~ {result['end_date']}

자금 변화:
├─ 초기 자금:   {result['initial_balance']:>15,.0f}원
├─ 최종 자금:   {result['final_balance']:>15,.0f}원
├─ 총 수익:     {result['total_profit']:>15,.0f}원
└─ 수익률:      {result['total_profit_percent']:>15.2f}%

거래 통계:
├─ 거래 횟수:   {result['trade_count']:>15}건
├─ 승리:        {result['win_count']:>15}건
├─ 패배:        {result['loss_count']:>15}건
├─ 승률:        {result['win_rate']:>15.1f}%
└─ 평균 수익:   {result['avg_profit']:>15,.0f}원/건

리스크 지표:
├─ 최대 손실:   {result['max_loss']:>15,.0f}원
├─ 최대 낙폭:   {result['max_drawdown']:>15.2f}%
└─ 샤프 비율:   {result['sharpe_ratio']:>15.2f}

평가:
"""
        # 성과 평가
        if result['win_rate'] >= 60 and result['total_profit_percent'] >= 10:
            evaluation = "✓ 우수한 전략 (실거래 추천 가능)"
        elif result['win_rate'] >= 50 and result['total_profit_percent'] >= 0:
            evaluation = "○ 개선 필요 (조정 후 재테스트)"
        else:
            evaluation = "✗ 부족한 성과 (전략 재검토 필요)"

        report += f"└─ {evaluation}\n"
        report += f"{'='*60}\n"

        return report

    def simulate_trade(self, stock_code, buy_price, target_price, stop_loss_price,
                      buy_date, quantity=None):
        """
        거래 시뮬레이션

        Args:
            stock_code (str): 종목 코드
            buy_price (float): 매수가
            target_price (float): 목표가
            stop_loss_price (float): 손절가
            buy_date (str): 매수 날짜
            quantity (int): 수량 (None이면 예수금으로 전량)

        Returns:
            dict: 시뮬레이션 결과
        """
        if quantity is None:
            # 예수금 기반 최대 수량
            quantity = int(self.current_balance / buy_price)

        buy_amount = buy_price * quantity

        # 수익/손실 가정 (실제로는 과거 데이터에서 조회)
        # 간단히: 목표가 도달 확률 60%, 손절 확률 40%
        import random
        is_profit = random.random() < 0.6

        if is_profit:
            sell_price = target_price
            profit = (sell_price - buy_price) * quantity
        else:
            sell_price = stop_loss_price
            profit = (sell_price - buy_price) * quantity

        self.current_balance += profit
        self.trades.append({
            'code': stock_code,
            'buy_date': buy_date,
            'buy_price': buy_price,
            'quantity': quantity,
            'sell_price': sell_price,
            'profit': profit,
            'profit_percent': (profit / buy_amount) * 100 if buy_amount > 0 else 0
        })

        return {
            'is_profit': is_profit,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'profit': profit,
            'current_balance': self.current_balance
        }

    def plot_results(self, result):
        """
        백테스트 결과를 그래프로 시각화

        Args:
            result (dict): 백테스트 결과
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # GUI 없이 실행

            # 자금 변화 그래프
            dates = []
            balances = []
            current_balance = self.initial_balance

            for trade in self.trades:
                dates.append(trade['buy_date'])
                current_balance += trade['profit']
                balances.append(current_balance)

            if not balances:
                logger_instance.warning("그래프 생성: 거래 기록 없음")
                return

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

            # 1. 자금 변화 그래프
            ax1.plot(range(len(balances)), balances, marker='o', label='자금')
            ax1.axhline(y=self.initial_balance, color='r', linestyle='--', label='초기 자금')
            ax1.set_title('자금 변화 (복리)')
            ax1.set_xlabel('거래 횟수')
            ax1.set_ylabel('자금 (원)')
            ax1.legend()
            ax1.grid(True)

            # 2. 거래 손익 분포
            profits = [t['profit'] for t in self.trades]
            ax2.bar(range(len(profits)), profits, color=['green' if p > 0 else 'red' for p in profits])
            ax2.set_title('거래별 손익')
            ax2.set_xlabel('거래 번호')
            ax2.set_ylabel('손익 (원)')
            ax2.grid(True)

            # 그래프 저장
            plt.tight_layout()
            filename = f"backtest_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=100)
            logger_instance.info(f"✓ 그래프 저장: {filename}")

            plt.close()

        except ImportError:
            logger_instance.warning("matplotlib 미설치 - 그래프 생성 불가능")
        except Exception as e:
            logger_instance.error(f"그래프 생성 실패: {e}")

    def save_results(self, result):
        """
        백테스트 결과를 DB에 저장

        Args:
            result (dict): 백테스트 결과
        """
        try:
            db_instance.cursor.execute('''
                INSERT INTO backtest_results
                (backtest_date, start_date, end_date, initial_balance, final_balance,
                 total_profit, total_profit_percent, win_count, loss_count, win_rate,
                 avg_profit, max_loss)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().strftime("%Y-%m-%d"),
                result['start_date'],
                result['end_date'],
                result['initial_balance'],
                result['final_balance'],
                result['total_profit'],
                result['total_profit_percent'],
                result['win_count'],
                result['loss_count'],
                result['win_rate'],
                result['avg_profit'],
                result['max_loss']
            ))
            db_instance.conn.commit()
            logger_instance.info("✓ 백테스트 결과 저장 완료")
        except Exception as e:
            logger_instance.error(f"백테스트 결과 저장 실패: {e}")


# 프로그램 어디서나 이 백테스트 엔진을 사용하기 위해 전역 인스턴스 생성
backtest_engine = BacktestEngine()

# ==========================================
# 사용 예시
# ==========================================
# from backtest import backtest_engine
#
# # 백테스트 실행 (기본값: 6개월)
# result = backtest_engine.run()
#
# # 결과 리포트 출력
# report = backtest_engine.get_performance_report(result)
# print(report)
#
# # 결과 시각화
# backtest_engine.plot_results(result)
#
# # 결과 저장
# backtest_engine.save_results(result)
