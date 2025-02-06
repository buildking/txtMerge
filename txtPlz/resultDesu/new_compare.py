from tkinter import *
import pandas as pd
import log
import datetime
from DbUtil import DbUtil


#로그파일 세팅
logger = log.setLogging("queryMake_sqlite")
logger.debug("config file read")

dbUtil = DbUtil('db/knia.db')#손해보험협회 약어(knia)

def dbcompare(_text=None):

    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"\n[{time}] 계약 갱신 전,후 공통계약 찾기를 시작합니다.\n")

    dbRow = dbUtil.selectCompareResult()
    resultExcel = pd.DataFrame(dbRow, columns=[['소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>'],['연번', '계약소멸일', '피보험자', '피보험자생년월일', '모집인', '모집인생년월일', '연번', '계약체결일', '피보험자', '피보험자생년월일', '모집인', '모집인생년월일']])
    logger.info(resultExcel)
    print(resultExcel)
    resultExcel.to_excel('./excel_result/excel_result.xlsx')

    logger.info("DB 비교 완료")

    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 공통계약 찾기를 종료합니다.\n")
    _text.see(END)