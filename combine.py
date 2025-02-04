from os import *
from tkinter import *
import tkinter.messagebox as msbox
import pandas as pd
import log
import datetime

#log declare
logger = log.setLogging("combine")


#엑셀 합치기
def excelCombine(_text=None):

    #합칠 파일이 부족할 때 경고문
    def combineError(state):
        msbox.showwarning("파일 개수 부족", f"{state}폴더에 합칠 엑셀파일이 부족합니다.")
        logger.debug(f"{state}folder has not enough file")
        print(f"{state}folder has not enough file")

    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"\n[{time}] 엑셀파일 취합을 시작합니다.\n")

    ## end read ##
    #폴더 안의 파일 리스트 생성
    endFileList = listdir('excel_end')
    logger.info(endFileList)
    print(endFileList)
    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 계약 갱신 전 파일 리스트\n{endFileList}\n")


    #폴더 안의 파일 저장할 리스트 생성
    endExcelList = []
    endExcelList.clear()

    #리스트 안의 파일 하나씩 꺼내기
    for endExcel in endFileList:
        try:

            endExcelThing = pd.DataFrame()
            endExcelThing = pd.read_excel(f'./excel_end/{endExcel}')

            #파일 읽는데 성공했다면, 리스트에 엑셀 저장
            endExcelList.append(endExcelThing)

        except:

            #엑셀파일 인식이 안된다면, 에러메세지 띄우기
            msbox.showwarning("파일 인식 불가", "excel_end폴더를 확인해주세요.")
            logger.debug("end excel file don't observed")
            print("end excel file don't observed")

    ## new read ##
    #폴더 안의 파일 리스트 생성
    newFileList = listdir('excel_new')
    logger.info(newFileList)
    print(newFileList)
    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 계약 갱신 후 파일 리스트\n{newFileList}\n")

    #폴더 안의 파일 저장할 리스트 생성
    newExcelList = []
    newExcelList.clear()

    #파일리스트 안의 파일 하나씩 꺼내기
    for newExcel in newFileList:
        try:
            newExcelThing = pd.DataFrame()
            newExcelThing = pd.read_excel(f'./excel_new/{newExcel}')

            #파일 읽는데 성공했다면, 리스트에 엑셀 저장
            newExcelList.append(newExcelThing)

        except:

            #엑셀파일 인식이 안된다면, 에러메세지 띄우기
            msbox.showwarning("파일 인식 불가", "excel_new폴더를 확인해주세요.")
            logger.debug("new excel file don't observed")
            print("new excel file don't observed")

    #end merge

    #폴더 안에 파일이 없거나 하나뿐이라면 에러메세지 띄우기
    if len(endExcelList) == 0 or len(endExcelList) == 1:
        combineError('end')
        return


    #첫번째 엑셀파일을 데이터프레임에 삽입
    combineendExcel = endExcelList[0]

    #폴더 안에 있는 엑셀 리스트들을 차례대로 병합
    for endExcelOne in endExcelList[1:]:
        combineendExcel = pd.concat([endExcelOne, combineendExcel], join='outer')

    # 만들어진 엑셀 행*열 개수 tuple형태로 저장
    combineendExcelShape = combineendExcel.shape

    #기존 '연번' 컬럼 삭제
    combineendExcel = combineendExcel.drop(columns='연번', axis=1)

    #새로운 '연번'에 들어갈 list 생성
    endIndexList = []
    endIndexList.clear()

    #엑셀 row 수 세기
    x = 0
    for index in range(combineendExcelShape[0]):
        x += 1
        endIndexList.append(x)

    #새로 생성한 '연번'을 첫번째 칼럼으로 삽입
    combineendExcel.insert(0, '연번', endIndexList)
    #end파일 엑셀로 만들기
    combineendExcel.to_excel('./excel_result/excel_end.xlsx', index=False)
    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 계약 갱신 전 엑셀파일 취합에 성공했습니다. \n")


    #new merge

    #폴더 안에 파일이 없거나 하나뿐이라면 에러메세지 띄우기
    if len(newExcelList) == 0 or len(newExcelList) == 1:
        combineError('new')
        return


    #첫번째 엑셀파일을 데이터프레임에 삽입
    combinenewExcel = newExcelList[0]

    #폴더 안에 있는 엑셀 리스트들을 차례대로 병합
    for newExcelOne in newExcelList[1:]:
        combinenewExcel = pd.concat([newExcelOne, combinenewExcel], join='outer')

    # 만들어진 엑셀 행*열 개수 tuple형태로 저장
    combinenewExcelShape = combinenewExcel.shape

    #기존 '연번' 컬럼 삭제
    combinenewExcel = combinenewExcel.drop(columns='연번', axis=1)


    #새로운 '연번'에 들어갈 list 생성
    newIndexList = []
    newIndexList.clear()

    #엑셀 row 수 세기
    x = 0
    for index in range(combinenewExcelShape[0]):
        x += 1
        newIndexList.append(x)

    #새로 생성한 '연번'을 첫번째 칼럼으로 삽입
    combinenewExcel.insert(0, '연번', newIndexList)
    #new파일 엑셀로 만들기
    combinenewExcel.to_excel('./excel_result/excel_new.xlsx', index=False)
    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 계약 갱신 후 엑셀파일 취합에 성공했습니다. \n")
    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 엑셀파일 취합을 종료합니다.\n")
    _text.see(END)
    logger.info("combine complete")
    print("Excel file combine complete")
