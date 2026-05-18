# ==========================================
# trader.py - 매매 실행 (분석/주문 분기)
# ==========================================
# 역할: 예측 결과를 바탕으로 주문 실행 (또는 분석 모드에서는 추천만 출력)
# 모드별 동작:
#   - analysis: 주문 없이 추천 정보만 출력 ← 첫 번째 버전
#   - backtest: 백테스트 엔진에서 처리
#   - paper: 모의투자 주문
#   - live: 실거래 주문

from datetime import datetime
from logger import logger_instance
from kiwoom_api import kiwoom_api
from database import db_instance
from risk_manager import risk_manager
from config import MODE


class Trader:
    """매매 실행"""

    def __init__(self):
        """트레이더 초기화"""
        pass

    # ==========================================
    # 분석 모드 (주문 없음)
    # ==========================================

    def execute_analysis_mode(self, prediction, current_balance):
        """
        분석 모드: 주문 없이 추천 정보만 출력 및 저장

        Args:
            prediction (dict): ai_predictor에서 반환한 예측 정보
            current_balance (float): 현재 예수금

        Returns:
            dict: 실행 결과
        """
        if not prediction:
            return {'success': False, 'message': '예측 정보 없음'}

        stock_code = prediction['stock_code']
        stock_name = prediction['stock_name']
        recommended_buy_price = prediction['recommended_buy_price']
        target_sell_price = prediction['target_sell_price']
        stop_loss_price = prediction['stop_loss_price']
        confidence = prediction['confidence']
        buy_time_start = prediction['buy_time_start']
        buy_time_end = prediction['buy_time_end']
        rsi_value = prediction.get('rsi_value')
        macd_value = prediction.get('macd_value')

        # 예상 매수 수량 계산 (현재 예수금 기반)
        expected_quantity = int(current_balance / recommended_buy_price)
        expected_buy_amount = expected_quantity * recommended_buy_price

        logger_instance.info(f"\n{'='*60}")
        logger_instance.info(f"[분석 모드] 매수 추천")
        logger_instance.info(f"{'='*60}")
        logger_instance.info(f"종목명:          {stock_name}({stock_code})")
        logger_instance.info(f"추천 매수 시간:  {buy_time_start} ~ {buy_time_end}")
        logger_instance.info(f"추천 매수가:     {recommended_buy_price:,.0f}원")
        logger_instance.info(f"목표 매도가:     {target_sell_price:,.0f}원 (+ {target_sell_price - recommended_buy_price:,.0f}원)")
        logger_instance.info(f"손절가:          {stop_loss_price:,.0f}원 (- {recommended_buy_price - stop_loss_price:,.0f}원)")
        logger_instance.info(f"신뢰도:          {confidence:.1f}%")
        logger_instance.info(f"\n[예상 거래]")
        logger_instance.info(f"현재 예수금:     {current_balance:,.0f}원")
        logger_instance.info(f"예상 매수 수량:  {expected_quantity:,}주")
        logger_instance.info(f"예상 투자 금액:  {expected_buy_amount:,.0f}원")
        logger_instance.info(f"남은 예수금:     {current_balance - expected_buy_amount:,.0f}원")
        logger_instance.info(f"\n[기술 지표]")
        logger_instance.info(f"RSI:            {rsi_value:.1f}")
        logger_instance.info(f"MACD:           {macd_value:.2f}")
        logger_instance.info(f"이유:           {prediction.get('reason', '?')}")
        logger_instance.info(f"{'='*60}\n")

        # DB에 추천 종목 저장
        today = datetime.now().strftime("%Y-%m-%d")
        db_instance.insert_daily_pick(
            date=today,
            stock_code=stock_code,
            stock_name=stock_name,
            current_price=prediction['current_price'],
            recommended_buy_price=recommended_buy_price,
            target_sell_price=target_sell_price,
            stop_loss_price=stop_loss_price,
            confidence=confidence,
            buy_time_start=buy_time_start,
            buy_time_end=buy_time_end,
            expected_quantity=expected_quantity,
            rsi_value=rsi_value,
            macd_value=macd_value
        )

        return {
            'success': True,
            'message': '분석 완료',
            'stock_code': stock_code,
            'stock_name': stock_name,
            'expected_quantity': expected_quantity,
            'expected_buy_amount': expected_buy_amount
        }

    # ==========================================
    # 매도/청산 (분석 모드에서도 사용)
    # ==========================================

    def execute_analysis_sell(self, trade_id, current_price, sell_quantity, sell_time):
        """
        분석 모드에서의 매도 기록

        Args:
            trade_id (int): 거래 ID
            current_price (float): 매도 현재가
            sell_quantity (int): 매도 수량
            sell_time (str): 매도 시간

        Returns:
            dict: 매도 결과
        """
        try:
            # DB에 매도 기록
            db_instance.close_trade(trade_id, current_price, sell_quantity, sell_time)

            logger_instance.info(
                f"매도 기록 저장: {sell_quantity}주 @ {current_price:,.0f}원"
            )

            return {
                'success': True,
                'message': '매도 기록 저장 완료',
                'sell_price': current_price,
                'sell_quantity': sell_quantity
            }

        except Exception as e:
            logger_instance.error(f"매도 기록 저장 실패: {e}")
            return {'success': False, 'message': str(e)}

    # ==========================================
    # 실거래 모드 - 자동 매수
    # ==========================================

    def execute_live_buy(self, stock_code, stock_name, quantity, price):
        """
        실거래 모드: 키움 실거래 서버에 자동 매수 주문 (완전 자동!)

        Args:
            stock_code (str): 종목 코드
            stock_name (str): 종목명
            quantity (int): 수량
            price (float): 지정가

        Returns:
            dict: 주문 결과
        """
        if MODE != "live":
            logger_instance.warning("실거래 모드가 아닙니다")
            return {'success': False}

        try:
            # 🤖 자동 주문 실행
            logger_instance.warning(f"\n{'='*60}")
            logger_instance.warning(f"🤖 [자동 매수 주문 발송]")
            logger_instance.warning(f"{'='*60}")
            logger_instance.warning(f"종목: {stock_name}({stock_code})")
            logger_instance.warning(f"수량: {quantity:,}주")
            logger_instance.warning(f"가격: {price:,.0f}원 (지정가)")
            logger_instance.warning(f"총액: {quantity * price:,.0f}원")
            logger_instance.warning(f"{'='*60}\n")

            # 키움 API로 실제 주문
            order_id = kiwoom_api.place_order(
                stock_code=stock_code,
                quantity=quantity,
                price=price,
                order_type="buy"
            )

            if order_id:
                logger_instance.info(f"✅ 매수 주문 완료! (주문번호: {order_id})")

                # DB에 매수 기록
                today = datetime.now().strftime("%Y-%m-%d")
                buy_time = datetime.now().strftime("%H:%M:%S")
                trade_id = db_instance.insert_trade(
                    date=today,
                    stock_code=stock_code,
                    stock_name=stock_name,
                    buy_price=price,
                    buy_quantity=quantity,
                    buy_time=buy_time
                )

                return {
                    'success': True,
                    'order_id': order_id,
                    'trade_id': trade_id,
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'price': price
                }
            else:
                logger_instance.error("❌ 매수 주문 실패")
                return {'success': False}

        except Exception as e:
            logger_instance.error(f"❌ 실거래 매수 실패: {e}")
            return {'success': False}

    def execute_live_sell(self, trade_id, stock_code, stock_name, quantity, price, reason="목표가"):
        """
        실거래 모드: 키움 실거래 서버에 자동 매도 주문 (완전 자동!)

        Args:
            trade_id (int): 거래 ID
            stock_code (str): 종목 코드
            stock_name (str): 종목명
            quantity (int): 수량
            price (float): 지정가
            reason (str): 매도 이유 ("목표가", "손절", "강제청산")

        Returns:
            dict: 주문 결과
        """
        if MODE != "live":
            logger_instance.warning("실거래 모드가 아닙니다")
            return {'success': False}

        try:
            # 🤖 자동 매도 주문 실행
            logger_instance.warning(f"\n{'='*60}")
            logger_instance.warning(f"🤖 [자동 매도 주문 발송] ({reason})")
            logger_instance.warning(f"{'='*60}")
            logger_instance.warning(f"종목: {stock_name}({stock_code})")
            logger_instance.warning(f"수량: {quantity:,}주")
            logger_instance.warning(f"가격: {price:,.0f}원 (지정가)")
            logger_instance.warning(f"총액: {quantity * price:,.0f}원")
            logger_instance.warning(f"{'='*60}\n")

            # 키움 API로 실제 주문
            order_id = kiwoom_api.place_order(
                stock_code=stock_code,
                quantity=quantity,
                price=price,
                order_type="sell"
            )

            if order_id:
                logger_instance.info(f"✅ 매도 주문 완료! (주문번호: {order_id})")

                # DB에 매도 기록
                sell_time = datetime.now().strftime("%H:%M:%S")
                db_instance.close_trade(trade_id, price, quantity, sell_time)

                return {
                    'success': True,
                    'order_id': order_id,
                    'stock_code': stock_code,
                    'quantity': quantity,
                    'price': price
                }
            else:
                logger_instance.error("❌ 매도 주문 실패")
                return {'success': False}

        except Exception as e:
            logger_instance.error(f"❌ 실거래 매도 실패: {e}")
            return {'success': False}

    # ==========================================
    # 전체 매매 플로우
    # ==========================================

    def execute_trade_for_stock(self, stock_info, current_balance):
        """
        종목에 대한 전체 매매 실행 (모드별로 분기)

        Args:
            stock_info (dict): stock_scanner에서 반환한 종목 정보
            current_balance (float): 현재 예수금

        Returns:
            dict: 실행 결과
        """
        stock_code = stock_info['code']
        stock_name = stock_info['name']
        current_price = stock_info['price']

        # ai_predictor에서 예측 받기
        from ai_predictor import predictor
        prediction = predictor.predict_stock(stock_code, stock_name, current_price)

        if not prediction:
            return {'success': False, 'message': '예측 신뢰도 부족'}

        # 모드별 실행
        if MODE == "analysis":
            return self.execute_analysis_mode(prediction, current_balance)
        elif MODE == "backtest":
            logger_instance.warning("백테스트는 backtest.py에서 처리")
            return {'success': False}
        elif MODE == "live":
            # 🤖 완전 자동: 자동 매수 실행
            recommended_buy_price = prediction['recommended_buy_price']
            expected_quantity = int(current_balance / recommended_buy_price)

            logger_instance.info(f"\n{'='*60}")
            logger_instance.info(f"[자동 거래 실행]")
            logger_instance.info(f"{'='*60}")
            logger_instance.info(f"종목: {stock_name}({stock_code})")
            logger_instance.info(f"현재 예수금: {current_balance:,.0f}원")
            logger_instance.info(f"예상 매수 수량: {expected_quantity:,}주")
            logger_instance.info(f"추천 매수가: {recommended_buy_price:,.0f}원")
            logger_instance.info(f"목표 매도가: {prediction['target_sell_price']:,.0f}원")
            logger_instance.info(f"손절가: {prediction['stop_loss_price']:,.0f}원")
            logger_instance.info(f"신뢰도: {prediction['confidence']}%")
            logger_instance.info(f"{'='*60}\n")

            # 예수금 확인
            can_afford, required = risk_manager.can_afford_buy(
                recommended_buy_price,
                expected_quantity,
                current_balance
            )

            if not can_afford:
                logger_instance.error("❌ 예수금 부족 - 매수 불가능")
                return {'success': False, 'message': '예수금 부족'}

            # 🔴 자동 매수 주문!
            buy_result = self.execute_live_buy(
                stock_code=stock_code,
                stock_name=stock_name,
                quantity=expected_quantity,
                price=recommended_buy_price
            )

            return buy_result
        else:
            logger_instance.error(f"알 수 없는 모드: {MODE}")
            return {'success': False}

    def execute_sell_if_conditions_met(self, trade_id, current_price, target_price, buy_price,
                                       stop_loss_price, buy_date, buy_quantity):
        """
        보유 중인 주식의 매도 조건 확인 및 매도 실행

        Args:
            trade_id (int): 거래 ID
            current_price (float): 현재 주가
            target_price (float): 목표 매도가
            buy_price (float): 매수 단가 (손절 손실률 계산용)
            stop_loss_price (float): 손절가
            buy_date (str): 매수 날짜
            buy_quantity (int): 매수 수량

        Returns:
            dict: 실행 결과
        """
        from risk_manager import risk_manager

        now = datetime.now()
        sell_time = now.strftime("%H:%M:%S")

        # 1. 목표가 도달 확인
        is_target, profit = risk_manager.check_profit_target(current_price, target_price)
        if is_target:
            logger_instance.info(f"목표가 도달! 매도 진행 ({profit:.1f}%)")

            if MODE == "live":
                # 🤖 자동 매도 (실거래)
                # DB에서 종목 정보 조회
                db_instance.cursor.execute(
                    "SELECT stock_code, stock_name FROM trades WHERE id = ?",
                    (trade_id,)
                )
                row = db_instance.cursor.fetchone()
                if row:
                    stock_code, stock_name = row
                    return self.execute_live_sell(
                        trade_id, stock_code, stock_name, buy_quantity,
                        current_price, reason="목표가 도달"
                    )
            else:
                # 분석 모드
                return self.execute_analysis_sell(trade_id, current_price, buy_quantity, sell_time)

        # 2. 손절가 도달 확인
        is_stop_loss, loss = risk_manager.check_stop_loss(current_price, buy_price, stop_loss_price)
        if is_stop_loss:
            logger_instance.warning(f"손절가 도달! 강제 매도 ({loss:.1f}%)")

            if MODE == "live":
                # 🤖 자동 손절 (실거래)
                db_instance.cursor.execute(
                    "SELECT stock_code, stock_name FROM trades WHERE id = ?",
                    (trade_id,)
                )
                row = db_instance.cursor.fetchone()
                if row:
                    stock_code, stock_name = row
                    return self.execute_live_sell(
                        trade_id, stock_code, stock_name, buy_quantity,
                        current_price, reason="손절"
                    )
            else:
                # 분석 모드
                return self.execute_analysis_sell(trade_id, current_price, buy_quantity, sell_time)

        # 3. 보유 기간 초과 확인
        is_over, days = risk_manager.check_holding_days(buy_date)
        if is_over:
            logger_instance.warning(f"보유 기간 초과({days}일)! 시장가 매도")

            if MODE == "live":
                # 🤖 자동 강제 청산 (실거래)
                db_instance.cursor.execute(
                    "SELECT stock_code, stock_name FROM trades WHERE id = ?",
                    (trade_id,)
                )
                row = db_instance.cursor.fetchone()
                if row:
                    stock_code, stock_name = row
                    return self.execute_live_sell(
                        trade_id, stock_code, stock_name, buy_quantity,
                        current_price, reason="4거래일 강제 청산"
                    )
            else:
                # 분석 모드
                return self.execute_analysis_sell(trade_id, current_price, buy_quantity, sell_time)

        return {
            'success': False,
            'message': '매도 조건 미충족',
            'profit': (current_price - target_price)
        }


# 프로그램 어디서나 이 트레이더를 사용하기 위해 전역 인스턴스 생성
trader = Trader()

# ==========================================
# 사용 예시
# ==========================================
# from trader import trader
# from config import MODE
#
# # 분석 모드: 주문 없이 추천만 출력
# if MODE == "analysis":
#     stock_info = {'code': '068270', 'name': '셀트리온', 'price': 25000}
#     result = trader.execute_trade_for_stock(stock_info, 1000000)
#     if result['success']:
#         print(f"매수 추천: {result['expected_quantity']}주")
#
# # 매도 조건 확인
# result = trader.execute_sell_if_conditions_met(
#     trade_id=1,
#     current_price=25150,
#     target_price=25175,
#     buy_price=25000,
#     stop_loss_price=24200,
#     buy_date="2026-05-16",
#     buy_quantity=40
# )
