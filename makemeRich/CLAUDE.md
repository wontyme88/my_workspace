# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 📌 프로젝트 개요 (Project Overview)

**키움증권 OpenAPI+ 기반 한국 주식 자동매매 프로그램 (완전 자동!)**

- 목표: **한 주당 150~200원 이상 수익실현** (매수가 대비 상승)
  - 예: 25,000원에 매수 → 25,200원에 매도 (한 주당 +200원) = 목표 달성!
  - 예: 40주 매수 시 총 수익 = 200원 × 40주 = 8,000원
- 가격대: 1만~5만원 종목 집중
- 투자 원칙: 복리 사용 (매도 수익 → 다음날 매수금에 자동 포함)
- **핵심 특징: 완전 자동** 🤖
  - 매일 자동 분석
  - 조건 만족 시 자동 매수
  - 목표가/손절가 도달 시 자동 매도

---

## 🏗️ 핵심 아키텍처 (Core Architecture)

### 모듈 구조 (10개 파일)

```
main.py (진입점)
    ↓
Step 1: 자금 설정 (risk_manager.py)
    ├─ 어제의 종료 예수금 조회 → 오늘의 시작 예수금 설정 (복리)
    └─ DB에 일별 예수금 기록
    ↓
Step 2: 종목 스캔 (stock_scanner.py)
    ├─ kiwoom_api에서 전체 종목 로드
    ├─ 가격 범위 필터링 (1만~5만원)
    ├─ 거래량, ETF/우선주 제외
    └─ 조건 충족 종목 리스트 반환
    ↓
Step 3: 개별 분석 (ai_predictor.py)
    ├─ 분봉 데이터 조회 (5분봉)
    ├─ 기술 지표 계산: RSI, MACD, 볼린저밴드, 거래량
    ├─ 신뢰도 계산 (0~100%)
    └─ 추천: 매수 시간, 목표가, 손절가 반환
    ↓
Step 4: 리스크 점검 (risk_manager.py)
    ├─ 오늘 이미 거래했는지 확인
    ├─ 예수금 충분 여부 확인
    └─ 일일 손실 한도 확인
    ↓
Step 5: 매매 실행 (trader.py)
    ├─ 분석 모드: 주문 없이 추천만 출력/저장
    ├─ 모의 모드: 키움 모의 서버로 주문
    ├─ 실거래 모드: 키움 실거래 서버로 주문
    └─ DB에 거래 기록 저장
```

### 데이터베이스 설계 (SQLite)

**핵심 테이블:**

| 테이블 | 목적 | 주요 컬럼 |
|--------|------|---------|
| `daily_balance` | 일별 예수금 추적 (복리용) | date, start_balance, profit_loss, end_balance |
| `trades` | 매매 기록 | stock_code, buy_price, sell_price, profit_loss, status |
| `daily_picks` | 일별 추천 종목 | stock_code, recommended_price, confidence, buy_time |
| `price_history` | 가격 데이터 | stock_code, date, open, high, low, close, volume |
| `backtest_results` | 백테스트 결과 | start_date, end_date, win_rate, total_profit |

**복리 구현:**
- `daily_balance.end_balance` (어제) → `daily_balance.start_balance` (오늘) 자동 연계
- `trader.py`에서 매도 후 수익 즉시 반영

### 모드별 동작 (config.py의 MODE 설정)

| MODE | 동작 | 주문 | 사용 시기 |
|------|------|------|---------|
| `"analysis"` | 분석만 수행, 추천 출력 | ❌ 없음 | 검증용 |
| `"backtest"` | 과거 데이터로 시뮬레이션 | ❌ 없음 | 전략 검증 용 |
| `"live"` | **완전 자동** (분석 → 매수 → 매도) | ✅ 자동 | **현재 설정! 🤖** |

---

## 🎯 주요 설정값 (config.py)

**⚠️ 중요: MODE 설정 확인**

```python
MODE = "live"                  # ⭐ 현재: LIVE 모드 (자동 매매 활성화!)
# ↑ 변경 시: "analysis"(추천만), "backtest"(과거 검증), "live"(자동 매매)
INITIAL_DEPOSIT = 1000000      # 초기 투자금 (사용자 입력)
MIN_PRICE = 10000              # 최소 주가
MAX_PRICE = 50000              # 최대 주가
TARGET_PROFIT = 175            # 목표 수익 (한 주당 원) ← 중요!
STOP_LOSS_PERCENT = 3.0        # 손절률 (%)
MAX_HOLD_DAYS = 4              # 최대 보유 거래일
```

**기술 지표 설정:**
```python
RSI_PERIOD = 14                # RSI 계산 기간
RSI_OVERSOLD = 30              # 과매도 기준 (매수 신호)
MACD_FAST = 12, MACD_SLOW = 26 # 단기/중기 이동평균
BB_PERIOD = 20                 # 볼린저밴드 기간
MIN_CONFIDENCE = 60.0          # 최소 신뢰도 (%)
```

---

## 💻 자주 사용하는 명령어

### ⚙️ 환경 확인 (첫 실행 전 필수)
```bash
# 필요한 패키지 설치
pip install pandas numpy matplotlib pytz

# 데이터베이스 및 로그 디렉토리 생성 (자동 생성되지만 명시적으로도 가능)
mkdir -p logs

# Python 버전 확인 (Windows 32bit 필수: 진입점으로만 사용)
python --version
```

### 자동 거래 시작 (완전 자동! 🤖)
```bash
python main.py
```

**예상 출력:**
```
[2026-05-16 09:15:00] 자동매매 프로그램 시작...
[2026-05-16 09:15:00] 실행 모드: live
[2026-05-16 09:15:01] 스캔 완료: 조건 충족 종목 12개
[2026-05-16 09:15:02] 매수 추천 종목: 5개

============================================================
🤖 [자동 매수 주문 발송]
============================================================
종목: 셀트리온(068270)
수량: 40주
가격: 24,950원 (지정가)
총액: 998,000원
✅ 매수 주문 완료! (주문번호: 12345)

[Step 6] 보유 종목 모니터링 & 자동 매도
보유 종목: 1개 모니터링 중...

[목표가 도달 시 자동 매도]
============================================================
🤖 [자동 매도 주문 발송] (목표가 도달)
============================================================
종목: 셀트리온(068270)
수량: 40주
가격: 25,150원 (지정가)
총액: 1,006,000원
✅ 매도 주문 완료! (주문번호: 12346)
수익: +8,000원 ✅
```

### 로그 확인
```bash
# 오늘의 로그
cat logs/2026-05-16.log

# 실시간 모니터링
tail -f logs/2026-05-16.log
```

### 데이터베이스 확인
```bash
# SQLite CLI 실행
sqlite3 makemerich.db

# 어제의 예수금 조회
> SELECT date, start_balance, profit_loss, end_balance FROM daily_balance ORDER BY date DESC LIMIT 1;

# 최근 거래 기록 조회
> SELECT date, stock_name, buy_price, sell_price, profit_loss FROM trades WHERE status='closed' ORDER BY date DESC LIMIT 5;
```

### 모드 변경 (⚠️ 신중히!)
```bash
# 1. 분석 모드로 변경하여 주문 없이 추천만 보기
# config.py 편집 후: MODE = "live" → MODE = "analysis"
nano config.py

# 2. 백테스트로 전략 검증
# config.py 편집 후: MODE = "analysis" → MODE = "backtest"
python main.py

# 3. 자동 매매 재개
# config.py 편집 후: MODE = "backtest" → MODE = "live"
python main.py
```

---

## 🔄 개발 단계 및 체크리스트

### Phase 1: 환경 설정 (필수!)
- [ ] Windows 32bit Python 설치/확인
- [ ] 키움증권 OpenAPI+ 신청 및 설치
- [ ] 필요 패키지 설치 (pandas, numpy, matplotlib)
- [ ] 키움 계좌에 투자 자금 입금

### Phase 2: 코드 설정
- [ ] `config.py`에서 `INITIAL_DEPOSIT` 설정 (실제 투입할 금액)
- [ ] `MODE = "live"` 확인 (현재 설정됨)
- [ ] kiwoom_api.py의 place_order() 함수 구현

### Phase 3: 첫 실행
- [ ] `python main.py` 실행
- [ ] 자동 분석 완료 확인
- [ ] 자동 매수 주문 발송 확인
- [ ] 로그 및 데이터베이스 기록 확인

### Phase 4: 모니터링
- [ ] 매일 실행하여 자동 거래 진행
- [ ] 로그에서 매수/매도 기록 확인
- [ ] 데이터베이스에서 거래 결과 조회
- [ ] 복리 누적 확인 (매일 예수금 증가)

---

## ⚠️ 중요 제약사항 (Critical Constraints)

### 1️⃣ Windows 32bit Python 필수 (API 연동만)
- **키움 OpenAPI+는 Windows 32bit에서만 동작**
- 실제 API 호출(`place_order()`, `get_stock_data()`)은 Windows 32bit 필수
- 현재 `kiwoom_api.py`는 **샘플 데이터 반환 중** (실제 API 미구현)
- **Mac/Linux에서 테스트 가능**: `MODE="analysis"` 또는 `"backtest"`만 사용
- ⚠️ **API 미연동 상태에서 `MODE="live"`로 실행하면 주문이 실행되지 않을 수 있음**

### 2️⃣ 완전 자동 = 손실도 자동 (⚠️ 신중함!)
- **현재 MODE = "live"** → 주문이 자동으로 발송됨
- 손절도 자동으로 실현됨 (수동 개입 불가)
- 초기에는 **MODE를 "analysis"로 설정하여 추천만 확인한 후** 자금 증액 권장

### 3️⃣ 복리 자동 적용
- `database.py`의 `daily_balance` 테이블에서 **자동 추적**
- 매일 실행할 때마다 어제 예수금이 오늘의 시작 예수금으로 설정됨
- DB를 수동으로 조정하면 복리 계산이 깨지므로 주의!

---

## 🔍 핵심 함수 및 파일별 역할

### logger.py
```python
from logger import logger_instance
logger_instance.info("메시지")        # 일반 정보
logger_instance.warning("경고")       # 경고
logger_instance.error("오류")        # 오류
```
→ 파일과 콘솔에 동시 출력, 날짜별 로그 자동 분리

### database.py
```python
from database import db_instance
db_instance.get_today_balance()      # 오늘 예수금
db_instance.get_yesterday_balance()  # 어제 종료 예수금 (복리용)
db_instance.insert_trade(...)        # 매매 기록 저장
```

### stock_scanner.py
```python
from stock_scanner import scanner
filtered_stocks = scanner.scan_stocks()  # 조건 충족 종목 반환
# 결과: [{'code': '068270', 'name': '셀트리온', 'price': 25000}, ...]
```

### ai_predictor.py
```python
from ai_predictor import predictor
prediction = predictor.predict_stock('068270', '셀트리온', 25000)
# 결과: {'stock_code': ..., 'recommended_buy_price': ..., 'confidence': 72.5, ...}
```

### risk_manager.py
```python
from risk_manager import risk_manager
risk_manager.can_buy_today()                    # 오늘 매수 가능?
risk_manager.check_profit_target(...)           # 목표가 도달?
risk_manager.check_holding_days(...)            # 4일 초과?
risk_manager.generate_daily_report(...)         # 일일 리포트
```

### trader.py
```python
from trader import trader
result = trader.execute_analysis_mode(prediction, current_balance)
# 분석 모드: 주문 없이 추천만 출력/저장
```

### main.py
```python
# 자동으로 다음 순서 실행:
# 1. setup_initial_balance()      - 복리 적용된 예수금 설정
# 2. scan_stocks()                - 종목 스캔
# 3. analyze_stocks()             - 기술 지표 분석
# 4. check_risks()                - 리스크 점검
# 5. execute_trades()             - 매매 실행 (또는 추천 출력)
# 6. generate_report()            - 최종 리포트
```

---

## 📊 복리 작동 방식 (How Compound Interest Works)

**Day 1:**
```
초기 자금: 1,000,000원
매수: 40주 @ 25,000원 (= 1,000,000원)
매도: 40주 @ 25,200원 (한 주당 +200원 수익!)
수익: +200원 × 40주 = 8,000원
daily_balance.end_balance = 1,008,000원
```

**Day 2:**
```
daily_balance.start_balance = 1,008,000원 (자동 설정!)
이제 40주 이상 매수 가능! (더 많은 수량)
예: 1,008,000 ÷ 25,000 = 40주 (복리 적용됨)
```

**Day 3 이상:**
```
계속 복리 누적...
매일 조금씩 더 많은 수량을 매수할 수 있음
한 주당 150~200원 수익 × 누적된 수량 = 기하급수적 성장
```

---

## 🛠️ 디버깅 & 문제 해결

### 1. 로그 확인 (제일 먼저!)
```bash
# 오늘 로그 실시간 확인
tail -f logs/$(date +%Y-%m-%d).log

# 최근 100줄 확인
tail -100 logs/$(date +%Y-%m-%d).log

# 특정 키워드 검색
grep "ERROR\|주문\|매도" logs/$(date +%Y-%m-%d).log
```

### 2. 데이터베이스 상태 확인
```bash
sqlite3 makemerich.db
> .schema daily_balance
> SELECT * FROM daily_balance ORDER BY date DESC LIMIT 5;
> SELECT * FROM trades WHERE status='open';
> .quit
```

### 3. 특정 모듈만 테스트 (격리된 환경)
```python
python3
>>> from stock_scanner import scanner
>>> stocks = scanner.scan_stocks()
>>> print(f"스캔된 종목: {len(stocks)}개")

>>> from ai_predictor import predictor
>>> pred = predictor.predict_stock('068270', '셀트리온', 25000)
>>> print(f"신뢰도: {pred['confidence']}%")

>>> from database import db_instance
>>> balance = db_instance.get_today_balance()
>>> print(f"오늘 예수금: {balance}원")
```

### 🔴 일반적인 문제와 해결책

| 증상 | 원인 | 해결 |
|------|------|------|
| `ImportError: No module named 'XXX'` | 패키지 미설치 | `pip install pandas numpy matplotlib pytz` |
| `database.py` 오류 | DB 파일 손상 | `rm makemerich.db` (재실행 시 자동 재생성) |
| `MODE="live"`인데 주문 안 됨 | API 미연동 (Windows 32bit 필요) | `MODE="analysis"` 변경하고 테스트 |
| 로그가 생성 안 됨 | `logs/` 디렉토리 없음 | `mkdir -p logs` |
| 복리가 적용 안 됨 | 어제 데이터 없음 | 첫 실행은 `INITIAL_DEPOSIT` 사용, 다음부터 자동 |

---

## 🔗 모듈 의존성 맵 (Module Dependencies)

```
main.py (진입점)
  ├─ config.py (설정 읽기)
  ├─ logger.py (로그 출력)
  ├─ database.py (DB 연결 및 복리 적용)
  │   └─ makemerich.db (SQLite)
  ├─ kiwoom_api.py (주식 데이터 조회)
  │   └─ [Windows 32bit 키움 API]
  ├─ stock_scanner.py (종목 필터링)
  │   └─ kiwoom_api.py
  ├─ ai_predictor.py (기술 지표 분석)
  │   └─ kiwoom_api.py (분봉 데이터)
  ├─ risk_manager.py (리스크 점검)
  │   └─ database.py (예수금, 거래 확인)
  └─ trader.py (주문 실행)
      ├─ kiwoom_api.py (주문 발송)
      └─ database.py (거래 기록)
```

**주의**: 모든 모듈은 `logger`와 `config`에 의존 → 수정 시 영향 범위 크므로 신중할 것

---

## 📝 개발자 체크리스트

### 코드 변경 전
- [ ] `MODE`가 "analysis"인지 확인 (테스트 시)
- [ ] 데이터베이스 백업 (`cp makemerich.db makemerich.db.bak`)
- [ ] 로그 파일 생성 여부 확인 (`ls -la logs/`)

### 새 기능 추가 시
- [ ] `config.py`에 새 설정값 추가 (하드코딩 금지!)
- [ ] `logger_instance.info()`로 진행 상황 기록
- [ ] 기능을 `main.py`의 적절한 Step에 통합
- [ ] 백테스트로 검증

### 릴리스 전
- [ ] `MODE = "analysis"` 또는 `"backtest"`로 테스트
- [ ] 모든 로그 및 DB 기록 정상 여부 확인
- [ ] `MODE = "live"` 변경 시 **작은 금액으로 먼저 테스트**

---

## 📚 참고 자료

### 코드 레벨
- **기술 지표 이론**: `config.py` 주석 상세 설명
- **DB 스키마**: `database.py`의 `create_tables()` 참고
- **API 통합**: `kiwoom_api.py` (현재 샘플 구현)

### 외부 자료
- **키움 OpenAPI+**: [공식 문서](https://www.kiwoom.com/) (Windows 32bit 설치 필수)
- **기술 지표**: RSI, MACD, 볼린저밴드 이론은 금융 교과서 또는 TA-Lib 문서 참고
- **복리 계산**: 매일 `database.py`가 자동 처리 (수정 금지)
