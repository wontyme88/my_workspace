# ==========================================
# database.py - SQLite 데이터베이스 관리
# ==========================================
# 역할: 모든 거래 기록과 일별 예수금을 저장/조회
# 복리 원리 적용: 어제의 "종료 예수금" = 오늘의 "시작 예수금"

import sqlite3
import os
from datetime import datetime
from logger import logger_instance
from config import DB_FILE


class Database:
    """SQLite 데이터베이스 관리 클래스"""

    def __init__(self, db_file=DB_FILE):
        """
        데이터베이스 초기화

        Args:
            db_file (str): 데이터베이스 파일 경로
        """
        self.db_file = db_file
        self.conn = None
        self.cursor = None

        # 데이터베이스 파일이 없으면 새로 생성
        is_new_db = not os.path.exists(db_file)

        # SQLite 데이터베이스 연결
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

        # 새 데이터베이스면 테이블 자동 생성
        if is_new_db:
            self._create_tables()
            logger_instance.info(f"새 데이터베이스 생성: {db_file}")
        else:
            logger_instance.info(f"기존 데이터베이스 연결: {db_file}")

    def _create_tables(self):
        """데이터베이스 테이블 생성"""

        # ==========================================
        # 테이블 1: daily_balance (일별 예수금) ← 복리 추적!
        # ==========================================
        # 각 날짜별로 시작 예수금, 매도 수익, 종료 예수금을 기록
        # 복리: day1의 종료 예수금 → day2의 시작 예수금
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_balance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,           -- 거래 날짜 (YYYY-MM-DD)
                start_balance REAL NOT NULL,         -- 하루 시작 예수금
                profit_loss REAL DEFAULT 0,          -- 당일 수익/손실
                end_balance REAL NOT NULL,           -- 하루 종료 예수금 (= 시작 + 수익)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ==========================================
        # 테이블 2: trades (매매 기록)
        # ==========================================
        # 매수/매도가, 수량, 수익/손실을 모두 기록
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,                  -- 거래 날짜 (YYYY-MM-DD)
                stock_code TEXT NOT NULL,            -- 종목 코드 (예: "005930" = 삼성전자)
                stock_name TEXT NOT NULL,            -- 종목명 (예: "삼성전자")
                buy_price REAL NOT NULL,             -- 매수가
                buy_quantity INTEGER NOT NULL,       -- 매수 수량
                buy_time TEXT,                       -- 매수 시간 (HH:MM:SS)
                sell_price REAL,                     -- 매도가
                sell_quantity INTEGER,               -- 매도 수량
                sell_time TEXT,                      -- 매도 시간 (HH:MM:SS)
                profit_loss REAL,                    -- 수익/손실 (= (매도가-매수가) * 수량)
                profit_percent REAL,                 -- 수익률 (%)
                hold_days INTEGER DEFAULT 0,         -- 보유 기간 (거래일)
                status TEXT DEFAULT 'open',          -- 상태: 'open' (진행중), 'closed' (완료), 'forced_sold' (강제매도)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ==========================================
        # 테이블 3: price_history (가격 이력)
        # ==========================================
        # 각 종목의 분봉/일봉 데이터 저장 (백테스트나 분석용)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,            -- 종목 코드
                date TEXT NOT NULL,                  -- 날짜
                time TEXT,                           -- 시간 (분봉 데이터일 때)
                open_price REAL,                     -- 시가
                high_price REAL,                     -- 고가
                low_price REAL,                      -- 저가
                close_price REAL NOT NULL,           -- 종가
                volume INTEGER,                      -- 거래량
                candle_type TEXT DEFAULT 'daily',    -- 'daily' 또는 'minute'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ==========================================
        # 테이블 4: backtest_results (백테스트 결과)
        # ==========================================
        # 과거 데이터로 전략을 테스트한 결과 저장
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backtest_date TEXT NOT NULL,         -- 백테스트 실행 날짜
                start_date TEXT NOT NULL,            -- 테스트 기간 시작일
                end_date TEXT NOT NULL,              -- 테스트 기간 종료일
                initial_balance REAL NOT NULL,       -- 초기 자금
                final_balance REAL NOT NULL,         -- 최종 자금
                total_profit REAL NOT NULL,          -- 총 수익
                total_profit_percent REAL NOT NULL,  -- 총 수익률 (%)
                win_count INTEGER DEFAULT 0,         -- 승리 횟수
                loss_count INTEGER DEFAULT 0,        -- 패배 횟수
                win_rate REAL DEFAULT 0,             -- 승률 (%)
                avg_profit REAL DEFAULT 0,           -- 평균 수익
                max_loss REAL DEFAULT 0,             -- 최대 손실폭
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # ==========================================
        # 테이블 5: daily_picks (일별 추천 종목)
        # ==========================================
        # 분석 모드에서 매일 생성한 추천 종목 저장
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_picks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,                  -- 분석 날짜
                stock_code TEXT NOT NULL,            -- 종목 코드
                stock_name TEXT NOT NULL,            -- 종목명
                current_price REAL NOT NULL,         -- 분석 당시 현재가
                recommended_buy_price REAL NOT NULL, -- 추천 매수가
                target_sell_price REAL NOT NULL,     -- 목표 매도가
                stop_loss_price REAL NOT NULL,       -- 손절가
                confidence REAL DEFAULT 0,           -- 신뢰도 (0~100%)
                buy_time_start TEXT,                 -- 추천 매수 시간 시작
                buy_time_end TEXT,                   -- 추천 매수 시간 종료
                expected_quantity INTEGER,           -- 예상 매수 수량
                rsi_value REAL,                      -- RSI 값
                macd_value REAL,                     -- MACD 값
                was_bought BOOLEAN DEFAULT 0,        -- 실제 매수했는지 여부
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()
        logger_instance.info("데이터베이스 테이블 생성 완료")

    # ==========================================
    # daily_balance (일별 예수금) 관련 함수
    # ==========================================

    def get_today_balance(self, today_date=None):
        """
        오늘의 예수금 정보 조회
        없으면 None 반환

        Args:
            today_date (str): 조회 날짜 (YYYY-MM-DD), 기본값은 오늘

        Returns:
            dict: {'date', 'start_balance', 'profit_loss', 'end_balance'} 또는 None
        """
        if today_date is None:
            today_date = datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute(
            "SELECT date, start_balance, profit_loss, end_balance FROM daily_balance WHERE date = ?",
            (today_date,)
        )
        row = self.cursor.fetchone()

        if row:
            return {
                'date': row[0],
                'start_balance': row[1],
                'profit_loss': row[2],
                'end_balance': row[3]
            }
        return None

    def get_yesterday_balance(self):
        """
        어제의 종료 예수금 조회 (복리 적용용)
        어제가 없으면 None 반환

        Returns:
            float: 어제의 종료 예수금 또는 None
        """
        self.cursor.execute(
            "SELECT end_balance FROM daily_balance ORDER BY date DESC LIMIT 1"
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def insert_daily_balance(self, date, start_balance, profit_loss, end_balance):
        """
        일별 예수금 기록 (새로 생성)

        Args:
            date (str): 날짜 (YYYY-MM-DD)
            start_balance (float): 시작 예수금
            profit_loss (float): 당일 수익/손실
            end_balance (float): 종료 예수금
        """
        try:
            self.cursor.execute('''
                INSERT INTO daily_balance (date, start_balance, profit_loss, end_balance)
                VALUES (?, ?, ?, ?)
            ''', (date, start_balance, profit_loss, end_balance))
            self.conn.commit()
            logger_instance.debug(f"일별 예수금 기록 저장: {date} {end_balance}원")
        except sqlite3.IntegrityError:
            logger_instance.warning(f"이미 존재하는 날짜 기록: {date}")

    def update_daily_balance(self, date, profit_loss, end_balance):
        """
        일별 예수금 업데이트 (매도 후 수익 반영)

        Args:
            date (str): 날짜 (YYYY-MM-DD)
            profit_loss (float): 수익/손실
            end_balance (float): 종료 예수금
        """
        try:
            self.cursor.execute('''
                UPDATE daily_balance
                SET profit_loss = ?, end_balance = ?, updated_at = CURRENT_TIMESTAMP
                WHERE date = ?
            ''', (profit_loss, end_balance, date))
            self.conn.commit()
            logger_instance.debug(f"일별 예수금 업데이트: {date} {end_balance}원")
        except Exception as e:
            logger_instance.error(f"일별 예수금 업데이트 실패: {e}")

    # ==========================================
    # trades (매매 기록) 관련 함수
    # ==========================================

    def insert_trade(self, date, stock_code, stock_name, buy_price, buy_quantity, buy_time):
        """
        매수 기록 저장

        Args:
            date (str): 거래 날짜
            stock_code (str): 종목 코드
            stock_name (str): 종목명
            buy_price (float): 매수가
            buy_quantity (int): 매수 수량
            buy_time (str): 매수 시간

        Returns:
            int: 저장된 거래 ID
        """
        try:
            self.cursor.execute('''
                INSERT INTO trades
                (date, stock_code, stock_name, buy_price, buy_quantity, buy_time, status)
                VALUES (?, ?, ?, ?, ?, ?, 'open')
            ''', (date, stock_code, stock_name, buy_price, buy_quantity, buy_time))
            self.conn.commit()
            trade_id = self.cursor.lastrowid
            logger_instance.info(
                f"매수 기록 저장: {stock_name}({stock_code}) {buy_quantity}주 @ {buy_price}원"
            )
            return trade_id
        except Exception as e:
            logger_instance.error(f"매수 기록 저장 실패: {e}")
            return None

    def close_trade(self, trade_id, sell_price, sell_quantity, sell_time):
        """
        매도로 거래 완료

        Args:
            trade_id (int): 거래 ID
            sell_price (float): 매도가
            sell_quantity (int): 매도 수량
            sell_time (str): 매도 시간
        """
        try:
            # 수익/손실 계산
            self.cursor.execute(
                "SELECT buy_price, buy_quantity FROM trades WHERE id = ?",
                (trade_id,)
            )
            row = self.cursor.fetchone()
            if not row:
                logger_instance.error(f"거래 기록 없음: ID {trade_id}")
                return

            buy_price = row[0]
            profit_loss = (sell_price - buy_price) * sell_quantity
            profit_percent = ((sell_price - buy_price) / buy_price) * 100

            self.cursor.execute('''
                UPDATE trades
                SET sell_price = ?, sell_quantity = ?, sell_time = ?,
                    profit_loss = ?, profit_percent = ?, status = 'closed',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (sell_price, sell_quantity, sell_time, profit_loss, profit_percent, trade_id))
            self.conn.commit()
            logger_instance.info(
                f"매도 완료: ID {trade_id} {sell_quantity}주 @ {sell_price}원 (+{profit_loss:.0f}원)"
            )
        except Exception as e:
            logger_instance.error(f"매도 기록 업데이트 실패: {e}")

    def get_open_trades(self):
        """
        진행 중인 거래 조회

        Returns:
            list: (id, date, stock_code, stock_name, buy_price, buy_quantity) 튜플 리스트.
                  date는 매수일(YYYY-MM-DD).
        """
        self.cursor.execute(
            "SELECT id, date, stock_code, stock_name, buy_price, buy_quantity "
            "FROM trades WHERE status = 'open'"
        )
        return self.cursor.fetchall()

    # ==========================================
    # daily_picks (일별 추천 종목) 관련 함수
    # ==========================================

    def insert_daily_pick(self, date, stock_code, stock_name, current_price,
                         recommended_buy_price, target_sell_price, stop_loss_price,
                         confidence, buy_time_start, buy_time_end, expected_quantity,
                         rsi_value=None, macd_value=None):
        """
        일별 추천 종목 저장 (분석 모드)

        Args:
            date (str): 분석 날짜
            stock_code (str): 종목 코드
            stock_name (str): 종목명
            current_price (float): 현재가
            recommended_buy_price (float): 추천 매수가
            target_sell_price (float): 목표 매도가
            stop_loss_price (float): 손절가
            confidence (float): 신뢰도 (0~100)
            buy_time_start (str): 추천 매수 시간 시작
            buy_time_end (str): 추천 매수 시간 종료
            expected_quantity (int): 예상 매수 수량
            rsi_value (float): RSI 값
            macd_value (float): MACD 값
        """
        try:
            self.cursor.execute('''
                INSERT INTO daily_picks
                (date, stock_code, stock_name, current_price, recommended_buy_price,
                 target_sell_price, stop_loss_price, confidence, buy_time_start,
                 buy_time_end, expected_quantity, rsi_value, macd_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date, stock_code, stock_name, current_price, recommended_buy_price,
                  target_sell_price, stop_loss_price, confidence, buy_time_start,
                  buy_time_end, expected_quantity, rsi_value, macd_value))
            self.conn.commit()
            logger_instance.debug(f"일별 추천 종목 저장: {stock_name}({stock_code})")
        except Exception as e:
            logger_instance.error(f"일별 추천 종목 저장 실패: {e}")

    # ==========================================
    # 데이터베이스 연결 관리
    # ==========================================

    def close(self):
        """데이터베이스 연결 종료"""
        if self.conn:
            self.conn.close()
            logger_instance.debug("데이터베이스 연결 종료")

    def __del__(self):
        """프로그램 종료 시 자동으로 연결 해제"""
        self.close()


# 프로그램 어디서나 이 database를 사용하기 위해 전역 인스턴스 생성
db_instance = Database()

# ==========================================
# 사용 예시
# ==========================================
# from database import db_instance
#
# # 오늘 예수금 조회
# today_balance = db_instance.get_today_balance()
#
# # 어제 종료 예수금 조회 (복리 적용)
# yesterday_end = db_instance.get_yesterday_balance()
#
# # 매수 기록 저장
# trade_id = db_instance.insert_trade(
#     "2026-05-16", "005930", "삼성전자", 70000, 10, "09:30:00"
# )
#
# # 매도로 거래 완료
# db_instance.close_trade(trade_id, 70200, 10, "10:30:00")
