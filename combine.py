import os
import sys
import sqlite3
import chardet
from tkinter import *
import tkinter.messagebox as msbox
import pandas as pd
import log
import datetime
import glob

logger = log.setLogging("combine")

if getattr(sys, 'frozen', False):  # PyInstaller로 실행된 경우
    base_folder = os.path.dirname(sys.executable)  # 🔥 실행 파일이 위치한 폴더
else:
    base_folder = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(base_folder, "txtPlz")
result_folder = os.path.join(data_folder, "resultDesu")
db_folder = os.path.join(base_folder, "database")
db_path = os.path.join(db_folder, "gacha.db")

# 🔥 파일의 인코딩을 감지하는 함수
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read(100000)
        result = chardet.detect(raw_data)
        return result["encoding"] if result["encoding"] else "utf-8"

# 🔥 SQLite 데이터베이스 설정
def setup_database():
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
        logger.info("DB폴더 생성")

    conn = sqlite3.connect(db_path)
    logger.info("DB 생성")
    cursor = conn.cursor()

    # 기존 데이터 저장 테이블
    cursor.execute("""
    DROP TABLE IF EXISTS gacha_data;
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gacha_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        등급 TEXT,
        item_id INTEGER,
        이름 TEXT,
        횟수 INTEGER,
        뽑기 INTEGER,
        기대확률 REAL,
        결과확률 REAL,
        파일명 TEXT,
        UNIQUE(item_id, 파일명)
    );
    """)

    # 중복 데이터 저장 테이블
    cursor.execute("""
    DROP TABLE IF EXISTS duplicate_gacha_data;
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS duplicate_gacha_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        등급 TEXT,
        item_id INTEGER,
        이름 TEXT,
        횟수 INTEGER,
        뽑기 INTEGER,
        기대확률 REAL,
        결과확률 REAL,
        파일명 TEXT,
        원본_파일 TEXT,
        중복_발생_시간 TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

# 🔥 중복 데이터를 별도 테이블에 저장하는 함수
def insert_into_duplicate_db(row, original_file):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO duplicate_gacha_data (등급, item_id, 이름, 횟수, 기대확률, 결과확률, 뽑기, 파일명, 원본_파일)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        row["등급"],
        row["ID"],
        row["이름"],
        row["횟수"],
        row["기대 확률(%)"],
        row["결과 확률(%)"],
        row["뽑기"],
        row["파일명"],
        original_file
    ))

    conn.commit()
    conn.close()

# 🔥 TXT 데이터를 SQLite에 삽입하는 함수
def insert_into_db(df):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()


    for _, row in df.iterrows():
        try:
            cursor.execute("""
            INSERT INTO gacha_data (등급, item_id, 이름, 횟수, 기대확률, 결과확률, 뽑기, 파일명)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (row["등급"], row["ID"], row["이름"], row["횟수"], row["기대 확률(%)"], row["결과 확률(%)"], row["뽑기"], row["파일명"]))
        except sqlite3.IntegrityError:  # 🔥 중복 데이터 발생 시 예외 처리
            insert_into_duplicate_db(row, row["파일명"])  # 중복 데이터를 별도 테이블에 저장

    conn.commit()
    conn.close()

# 🔥 SQLite 데이터를 조회하여 TXT 파일로 저장하는 함수
def export_data_to_txt(_text=None):
    conn = sqlite3.connect(db_path)
    
    # 🔥 결과 저장 폴더 확인 및 생성
    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    try:
        # 🔥 `item_id` + `파일명` 기준으로 GROUP BY 수행 (각 파일별 데이터)
        query = """
        SELECT item_id, 이름, 등급, 파일명,
               SUM(횟수) AS 횟수,
               SUM(뽑기) AS 뽑기,
               AVG(기대확률) AS 기대확률,
               AVG(결과확률) AS 결과확률
        FROM gacha_data
        GROUP BY item_id, 파일명
        """
        df = pd.read_sql(query, conn)

        # 🔥 Step 1: item_id 기준으로 통합 (각 파일별 데이터를 합산)
        grouped_df = df.groupby(["item_id", "이름", "등급"]).agg({
            "횟수": "sum",  # 횟수 합산
            "뽑기": "sum",  # 횟수 합산
            "기대확률": "mean"  # 기대확률 평균(고정값이라서 상관 없음)
        }).reset_index()

        # 🔥 0값 방지: 최종 RollCount가 0이면 새로운 결과확률을 0.00000000으로 설정
        grouped_df["새로운 결과확률"] = grouped_df.apply(
            lambda row: f"{(row['횟수'] / row['뽑기']):.8f}" if row["뽑기"] > 0 else "0.00000000",
            axis=1
        )

        # 🔥 Step 4: 기대확률도 소수점 8자리로 통일
        grouped_df["기대확률"] = grouped_df["기대확률"].apply(lambda x: f"{x:.8f}")

        # 🔥 Step 5: 합계 행 추가
        total_expected_prob = grouped_df["기대확률"].astype(float).sum()
        total_actual_prob = grouped_df["새로운 결과확률"].astype(float).sum()
        total_row = pd.DataFrame({
            "item_id": ["합계"],
            "이름": [""],
            "등급": [""],
            "횟수": [grouped_df["횟수"].sum()],
            "기대확률": [f"{total_expected_prob:.8f}"],
            "뽑기": [grouped_df["뽑기"].sum()],  # 🔥 0을 포함한 평균 계산
            "새로운 결과확률": [f"{total_actual_prob:.8f}"]
        })

        # 🔥 최종 DataFrame에 합계 행 추가
        grouped_df = pd.concat([grouped_df, total_row], ignore_index=True)

        # 🔥 TXT 파일로 저장
        final_file_path = os.path.join(result_folder, "merge_result.txt")
        grouped_df.to_csv(final_file_path, sep="\t", index=False, encoding="utf-8-sig")

        logger.info(f"🎉 최종 그룹화된 데이터 저장 완료: {final_file_path}")
        print(f"✅ 최종 그룹화된 데이터가 {final_file_path} 에 저장되었습니다.")

        time = str(datetime.datetime.now())[0:-7]
        _text.insert(END, f"[{time}] 모든 SQLite데이터가 [{result_folder}]폴더의 txt파일로 추출되었습니다.\n")

    except Exception as e:
        _text.insert(END, f"데이터 내보내기 오류 발생: {e}\n")
        logger.error(f"❌ 데이터 내보내기 오류: {e}")
        print(f"⚠️ 데이터 내보내기 오류 발생: {e}")
        msbox.showwarning("데이터 오류 발생", f"{e}")

    finally:
        conn.close()

# 🔥 TXT 파일을 읽고 SQLite에 저장하는 함수
def txtCombine(_text=None):
    setup_database()

    # 🔥 폴더가 없으면 자동으로 생성
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        time = str(datetime.datetime.now())[0:-7]
        _text.insert(END, f"[{time}] {data_folder} (폴더: {data_folder}) 폴더 생성됨.\n")
        logger.info(f"📁 폴더 생성됨: {data_folder}")

    txt_files = glob.glob(os.path.join(data_folder, "*.txt"))

    if len(txt_files) < 2:
        msbox.showwarning("파일 개수 부족", f"{data_folder}폴더에 txt 파일이 2개 이상 필요합니다.")
        logger.debug("TXT 파일 개수 부족")
        return

    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"\n[{time}] TXT 데이터 SQLite 저장 시작.\n")

    for file_path in txt_files:
        try:
            detected_encoding = detect_encoding(file_path)
            df = pd.read_csv(file_path, sep="\t", skiprows=1, header=None, encoding=detected_encoding)

            df.columns = ["등급", "ID", "이름", "횟수", "기대 확률(%)", "결과 확률(%)"]
            # 🔥 뽑기 값 계산 (ZeroDivisionError 방지)
            df["뽑기"] = df.apply(lambda row: 
                int(round(row["횟수"] / row["결과 확률(%)"])) 
                if pd.notna(row["결과 확률(%)"]) and row["결과 확률(%)"] > 0 and row["횟수"] > 0 
                else 0, axis=1
            ).replace([float("inf"), -float("inf")], 0)  # 🔥 무한대 값 방지
            df["파일명"] = os.path.basename(file_path)

            insert_into_db(df)  # 🔥 SQLite에 데이터 삽입

            time = str(datetime.datetime.now())[0:-7]
            _text.insert(END, f"[{time}] {os.path.basename(file_path)} (인코딩: {detected_encoding}) SQLite 저장 완료.\n")
        
        except Exception as e:
            msbox.showwarning("파일 오류", f"{os.path.basename(file_path)}을 읽을 수 없습니다.")
            _text.insert(END, f"파일 오류: {os.path.basename(file_path)}을 읽을 수 없습니다.\n")
            logger.error(f"파일 오류: {os.path.basename(file_path)} - {e}")
            return

    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 모든 TXT 데이터가 SQLite에 저장되었습니다.\n")

    logger.info("TXT 데이터 SQLite 저장 완료")
    print("TXT 데이터 SQLite 저장 완료")

    export_data_to_txt(_text)

    _text.see(END)
