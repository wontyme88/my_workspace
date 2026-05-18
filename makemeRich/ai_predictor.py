# ==========================================
# ai_predictor.py - 매수 타이밍 및 목표가 예측 엔진
# ==========================================
# 역할: 기술 지표 분석을 통해 "어느 시간에, 어느 가격에 매수하면 좋을지" 예측
# 지표: RSI, MACD, 볼린저밴드, 거래량 급등
# 1단계: 규칙 기반 분석 (Rule-based)
# 2단계: 머신러닝 모델 (나중에 추가)

import statistics
from logger import logger_instance
from kiwoom_api import kiwoom_api
from config import (
    TARGET_PROFIT_MIN, TARGET_PROFIT_MAX, STOP_LOSS_PERCENT,
    RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    BB_PERIOD, BB_STD_DEV, MIN_CONFIDENCE
)


class AIPredictor:
    """기술 지표를 기반으로 매수 타이밍 및 목표가 예측"""

    def __init__(self):
        """예측기 초기화"""
        pass

    def predict_stock(self, stock_code, stock_name, current_price):
        """
        특정 종목의 매수 타이밍과 목표가 예측

        Args:
            stock_code (str): 종목 코드
            stock_name (str): 종목명
            current_price (float): 현재가

        Returns:
            dict: {
                'stock_code': '068270',
                'stock_name': '셀트리온',
                'current_price': 25000,
                'recommended_buy_price': 24950,
                'target_sell_price': 25150,  # +200원
                'stop_loss_price': 24200,    # -3%
                'buy_time_start': '09:30',
                'buy_time_end': '10:30',
                'expected_quantity': 40,
                'confidence': 72.5,
                'rsi_value': 35.2,
                'macd_value': 0.15,
                'reason': 'RSI 과매도 + MACD 상향'
            } 또는 None (신뢰도 부족 시)
        """

        logger_instance.info(f"분석 중: {stock_name}({stock_code})")

        # 1단계: 분봉 데이터 조회
        candles = kiwoom_api.get_minute_candles(stock_code, minute=5, count=20)
        if not candles:
            logger_instance.warning(f"분봉 데이터 없음: {stock_code}")
            return None

        # 2단계: 기술 지표 계산
        rsi_value = self._calculate_rsi(candles)
        macd_value = self._calculate_macd(candles)
        bb_signal = self._calculate_bollinger_bands(candles)
        volume_signal = self._analyze_volume_surge(candles)

        # 3단계: 신호 점수 계산
        signals = []
        reasons = []

        # RSI 신호 (30 이하 = 과매도 = 매수 신호)
        rsi_score = 0
        if rsi_value < RSI_OVERSOLD:
            rsi_score = 30  # 강한 매수 신호
            reasons.append(f"RSI {rsi_value:.1f} (과매도)")
        elif rsi_value < RSI_OVERSOLD + 10:
            rsi_score = 15  # 약한 매수 신호
            reasons.append(f"RSI {rsi_value:.1f} (약한 과매도)")
        signals.append(rsi_score)

        # MACD 신호 (양수 & 상향 = 매수 신호)
        macd_score = 0
        if macd_value > 0.1:
            macd_score = 20
            reasons.append("MACD 상향")
        elif macd_value > 0:
            macd_score = 10
            reasons.append("MACD 약한 상향")
        signals.append(macd_score)

        # 볼린저밴드 신호 (하단 터치 = 매수 신호)
        bb_score = 0
        if bb_signal == "buy":
            bb_score = 25
            reasons.append("BB 하단 접촉")
        elif bb_signal == "strong_buy":
            bb_score = 35
            reasons.append("BB 하단 돌파")
        signals.append(bb_score)

        # 거래량 신호 (거래량 급증 = 매수 신호)
        volume_score = 0
        if volume_signal:
            volume_score = 15
            reasons.append("거래량 급증")
        signals.append(volume_score)

        # 4단계: 신뢰도 계산 (0~100)
        confidence = min(sum(signals), 100)

        # 신뢰도 부족하면 None 반환
        if confidence < MIN_CONFIDENCE:
            logger_instance.info(
                f"[{stock_name}] 신뢰도 부족 ({confidence:.1f}%) - 추천 제외"
            )
            return None

        # 5단계: 목표가 및 손절가 계산
        # 목표: 한 주당 150~200원 상승 (예: 25,000→25,175~25,200원)
        recommended_buy_price = current_price - 50  # 현재가보다 50원 낮게 설정 (확률 높임)
        target_profit = (TARGET_PROFIT_MIN + TARGET_PROFIT_MAX) / 2  # 한 주당 175원 목표
        target_sell_price = recommended_buy_price + target_profit
        stop_loss_price = recommended_buy_price * (1 - STOP_LOSS_PERCENT / 100)

        # 6단계: 예상 매수 수량 (임시, 나중에 trader.py에서 계산)
        expected_quantity = 0  # trader.py에서 예수금 기반으로 계산

        prediction = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'current_price': current_price,
            'recommended_buy_price': round(recommended_buy_price),
            'target_sell_price': round(target_sell_price),
            'stop_loss_price': round(stop_loss_price),
            'buy_time_start': '09:30',
            'buy_time_end': '10:30',
            'expected_quantity': expected_quantity,
            'confidence': round(confidence, 1),
            'rsi_value': round(rsi_value, 1),
            'macd_value': round(macd_value, 2),
            'reason': ' + '.join(reasons)
        }

        logger_instance.info(
            f"[{stock_name}] 매수 추천! 신뢰도 {confidence:.1f}% - {', '.join(reasons)}"
        )

        return prediction

    def _calculate_rsi(self, candles):
        """
        RSI (상대강도지수) 계산
        30 이하 = 과매도 (사야 할 때)
        70 이상 = 과매수 (팔아야 할 때)

        Args:
            candles (list): 분봉 데이터

        Returns:
            float: RSI 값 (0~100)
        """
        if len(candles) < RSI_PERIOD + 1:
            return 50  # 데이터 부족하면 중립값

        try:
            # 종가(close) 추출
            prices = [c['close'] for c in candles[-RSI_PERIOD-1:]]

            # 상승분과 하강분 계산
            gains = []
            losses = []
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))

            # 평균 상승분과 평균 하강분
            avg_gain = statistics.mean(gains) if gains else 0
            avg_loss = statistics.mean(losses) if losses else 0

            # RSI 계산: RSI = 100 * (평균 상승분 / (평균 상승분 + 평균 하강분))
            if avg_loss == 0:
                return 100 if avg_gain > 0 else 50

            rs = avg_gain / avg_loss
            rsi = 100 * (rs / (1 + rs))

            logger_instance.debug(f"RSI 계산 완료: {rsi:.1f}")
            return rsi

        except Exception as e:
            logger_instance.error(f"RSI 계산 실패: {e}")
            return 50

    def _calculate_macd(self, candles):
        """
        MACD (이동평균수렴발산) 계산
        양수 = 상향 (매수 신호)
        음수 = 하향 (매도 신호)

        Args:
            candles (list): 분봉 데이터

        Returns:
            float: MACD 값
        """
        if len(candles) < MACD_SLOW:
            return 0  # 데이터 부족

        try:
            prices = [c['close'] for c in candles[-MACD_SLOW:]]

            # EMA (지수이동평균) 계산
            ema_fast = self._calculate_ema(prices, MACD_FAST)
            ema_slow = self._calculate_ema(prices, MACD_SLOW)

            # MACD = 빠른 EMA - 느린 EMA
            macd = ema_fast - ema_slow

            logger_instance.debug(f"MACD 계산 완료: {macd:.2f}")
            return macd

        except Exception as e:
            logger_instance.error(f"MACD 계산 실패: {e}")
            return 0

    def _calculate_ema(self, prices, period):
        """
        EMA (지수이동평균) 계산

        Args:
            prices (list): 가격 리스트
            period (int): 기간

        Returns:
            float: EMA 값
        """
        if len(prices) < period:
            return statistics.mean(prices)

        # 단순이동평균(SMA)으로 시작
        sma = statistics.mean(prices[-period:])

        # 계수
        multiplier = 2 / (period + 1)

        # EMA = 이전EMA + 계수 * (현재가 - 이전EMA)
        ema = sma
        for price in prices[-period:]:
            ema = price * multiplier + ema * (1 - multiplier)

        return ema

    def _calculate_bollinger_bands(self, candles):
        """
        볼린저밴드 계산
        상단 + 중단 + 하단 선 / 가격이 하단 터치 = 매수 신호

        Args:
            candles (list): 분봉 데이터

        Returns:
            str: "buy" (하단 접촉), "strong_buy" (하단 돌파), "hold" (중립), None (상단)
        """
        if len(candles) < BB_PERIOD:
            return "hold"

        try:
            prices = [c['close'] for c in candles[-BB_PERIOD:]]
            current_price = prices[-1]

            # 중간값 (20일 평균)
            middle = statistics.mean(prices)

            # 표준편차
            variance = statistics.variance(prices)
            std_dev = variance ** 0.5

            # 상단/하단
            upper_band = middle + (BB_STD_DEV * std_dev)
            lower_band = middle - (BB_STD_DEV * std_dev)

            # 신호 판정
            if current_price < lower_band:
                return "strong_buy"  # 하단 돌파
            elif current_price < lower_band + (std_dev * 0.5):
                return "buy"  # 하단 근처
            else:
                return "hold"

        except Exception as e:
            logger_instance.error(f"볼린저밴드 계산 실패: {e}")
            return "hold"

    def _analyze_volume_surge(self, candles):
        """
        거래량 급증 분석
        최근 거래량이 평균보다 20% 이상 많으면 True

        Args:
            candles (list): 분봉 데이터

        Returns:
            bool: 거래량 급증이면 True
        """
        if len(candles) < 5:
            return False

        try:
            volumes = [c['volume'] for c in candles]
            recent_volume = volumes[-1]
            avg_volume = statistics.mean(volumes[:-1])  # 최근 제외한 평균

            # 최근 거래량이 평균의 120% 이상?
            if recent_volume > avg_volume * 1.2:
                logger_instance.debug(
                    f"거래량 급증 감지: {recent_volume} > {avg_volume * 1.2:.0f}"
                )
                return True

            return False

        except Exception as e:
            logger_instance.error(f"거래량 분석 실패: {e}")
            return False


# 프로그램 어디서나 이 예측기를 사용하기 위해 전역 인스턴스 생성
predictor = AIPredictor()

# ==========================================
# 사용 예시
# ==========================================
# from ai_predictor import predictor
#
# # 특정 종목 분석
# prediction = predictor.predict_stock("068270", "셀트리온", 25000)
#
# if prediction:
#     print(f"종목: {prediction['stock_name']}")
#     print(f"추천 매수가: {prediction['recommended_buy_price']}원")
#     print(f"목표 매도가: {prediction['target_sell_price']}원")
#     print(f"손절가: {prediction['stop_loss_price']}원")
#     print(f"신뢰도: {prediction['confidence']}%")
#     print(f"이유: {prediction['reason']}")
