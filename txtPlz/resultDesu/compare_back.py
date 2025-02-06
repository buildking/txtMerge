from tkinter import *
import pandas as pd
import log
import datetime
import time as Time

logger = log.setLogging("compare")

#end, new excel file compare
def excelCompare(_text=None):

    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"\n[{time}] 계약 갱신 전,후 공통계약 찾기를 시작합니다.\n")

    endDataFrame = pd.read_excel('./excel_result/excel_end.xlsx', dtype=str)
    newDataFrame = pd.read_excel('./excel_result/excel_new.xlsx', dtype=str)
    logger.info("파일읽기 완료")
    #print('파일읽기 완료.')

    #비교 통과한 end data와 new data의 row 저장(append로)
    coreRowNum = []
    coreRowNum.clear()
    coreRowNumPrint = []
    coreRowNumPrint.clear()

    start = Time.time()

    ##0.62초, 0.60초, 0.59초
    ## 이 방식으로 하는게 좋을거 같음. 속도 차이가 어마어마 하네
    b_dict = endDataFrame.to_dict("records")
    a_dict = newDataFrame.to_dict("records")
    i = 0
    j = 0
    for b in b_dict:
        j = 0
        for a in a_dict:
            if str(b['피보험자']) == str(a['피보험자']):
                if str(b['모집인명']) == str(a['모집인명']):
                    if str(b['피보험자\n주민등록번호'])[:5] == str(a['피보험자\n주민등록번호'])[:5]:
                        if str(b['모집인 주민번호'])[:5] == str(a['모집인 주민번호'])[:5]:
                            coreRowNum.append([i, j])
                            coreRowNumPrint.append([i+1, j+1])
            j = j + 1
        i = i + 1

    end = Time.time()
    logger.info("excute time >>>>> " + str(end - start) + "s")

    logger.debug("계약일 제외하고 일치하는 리스트")
    logger.debug(coreRowNumPrint)
    logger.debug(len(coreRowNumPrint))

    coreRowNumPrint = pd.DataFrame(coreRowNumPrint, columns=['전','후'])
    coreRowNumPrint.to_excel('./excel_result/excel_final_tryout_rows.xlsx')

    #1차로 걸러진 데이터 출력
    finalExcel_tryout = pd.DataFrame(columns=[['소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '소멸계약<이동 전>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>', '신규계약<이동 후>'],['회사명', '피보험자', '증권번호', '상품명', '상품분류', '계약소멸일', '상태', '회사명', '피보험자', '증권번호', '상품명', '상품분류', '계약체결일', '상태', '모집인명', '생년월일']])

    x = 0
    for b, a in coreRowNum:
        x += 1
        finalExcel_tryout.loc[x] = (endDataFrame.loc[b, '회사명'], endDataFrame.loc[b, '피보험자'], endDataFrame.loc[b, '증권번호'], endDataFrame.loc[b, '상품명'], endDataFrame.loc[b, '상품분류'], endDataFrame.loc[b, '계약소멸일'], endDataFrame.loc[b, '계약상태'], newDataFrame.loc[a, '회사명'], newDataFrame.loc[a, '피보험자'], newDataFrame.loc[a, '증권번호'], newDataFrame.loc[a, '상품명'], newDataFrame.loc[a, '상품분류'], newDataFrame.loc[a, '계약체결일'], newDataFrame.loc[a, '계약상태'], newDataFrame.loc[a, '모집인명'], newDataFrame.loc[a, '피보험자\n주민등록번호'])

    #1차로 걸러진 데이터 엑셀로 생성
    finalExcel_tryout.to_excel('./excel_result/excel_final_tryout.xlsx')


    #lastList = end[계약소멸일] - new[계약체결일] 의 list
    lastList = []
    lastList.clear()
    #lastListPrint = 사용자가 보기 편하게 출력용으로 제작
    lastListPrint = []
    lastListPrint.clear()

    ## _str(소멸일,체결일) 에는 각각 다음 타입이 들어올수 있음
    ## type 1. "2021-01-01" (문자타입으로 저장된데이터)
    ## type 2. "2021-01-01 00:00:00" (날짜타입으로 저장된데이터)
    ## type 3. "43891" (엑셀에서 날짜타입이 숫자타입으로 바뀌면 이와 같은 데이터)
    ## type 4. "20200101" (현재까지 발생한적은 없으나 고려할만한 타입임)
    ## return 이 datetime인 이유.. 계산이 편할것으로 생각돼서
    def dateDivision_2(_str):
        if _str.find("-") == -1:
            ## 하이픈(-) 을 찾지 못했으면 숫자 타입으로 본다.
            ## 숫자타입은 1990년 01월 01을 기준으로 삼기떄문에 아래와같은 코드를이용하여 변환한다고한다.(링크줄께)
            return datetime.datetime.fromordinal(datetime.datetime(1900, 1, 1).toordinal() + int(_str) - 2)
        else:
            ## 하이픈을 찾았으면 type1 또는 type2이다.
            ## 이 경우 앞에 10자리만 짤라서 date타입으로 만든다.
            return datetime.datetime.strptime(_str[:10], '%Y-%m-%d')

    #조건을 통과한 값의 (b'계약소멸일' - a'계약체결일')이 180이내인지 추려냄
    for i, j in coreRowNum:
        # endDate = len(endDataFrame.loc[i, '계약소멸일'])
        # newDate = len(newDataFrame.loc[j, '계약체결일'])
        ## endDateNum = dateDivision(endDataFrame.loc[i, '계약소멸일'])
        ## newDateNum = dateDivision(newDataFrame.loc[j, '계약체결일'])
        endDateNum = dateDivision_2(endDataFrame.loc[i, '계약소멸일'])
        newDateNum = dateDivision_2(newDataFrame.loc[j, '계약체결일'])

        ## 이후 사용법은 같으며 (dt-dt2).days 로 각 날짜의 간격을 일수로 얻을수 있다.(윤년이 고려되었는지는 모르겠음)
        if abs((newDateNum-endDateNum).days) <= 180:
            aSubB = newDateNum-endDateNum
            lastList.append([i, j, aSubB])
            lastListPrint.append([i+1, j+1, aSubB])
        # if abs(newDateNum-endDateNum) <= 180:
        #     aSubB = newDateNum-endDateNum
        #     lastList.append([i, j, aSubB])
        #     lastListPrint.append([i+1, j+1, aSubB])

    #개발자용
    lastExcel = pd.DataFrame(lastList, columns=['전','후', '날짜 차이'])
    logger.debug(lastExcel)#개발자용이기때문에 log에 남길필요 없음
    #사용자용
    lastExcelPrint = pd.DataFrame(lastListPrint, columns=['전','후', '날짜 차이'])
    lastExcelPrint.to_excel('./excel_result/excel_final_rows.xlsx', index=False)
    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 확인된 공통계약 리스트\n{lastExcelPrint}\n")

    # endFinal = pd.DataFrame
    # newFinal = pd.DataFrame


    endFinal = pd.concat([endDataFrame.loc[[b]] for b, a, diff in lastList], ignore_index=True)
    newFinal = pd.concat([newDataFrame.loc[[a]] for b, a, diff in lastList], ignore_index=True)

    columnList = endDataFrame.columns.tolist()
    for afcol in newDataFrame.columns.tolist():
        columnList.append(afcol)
    columnList.append('날짜 차이')

    logger.debug('최종 컬럼 리스트\n', columnList, '\n최종 컬럼 개수', len(columnList))
    #print('최종 컬럼 리스트\n', columnList, '\n최종 컬럼 개수', len(columnList))

    finalExcel = pd.concat([endFinal, newFinal, lastExcel.iloc[:, 2]], axis=1, ignore_index=True)
    finalExcel.columns = columnList

    finalExcel.to_excel('./excel_result/excel_final.xlsx')
    logger.info("compare complete")
    #print("Excel file compare complete")
    time = str(datetime.datetime.now())[0:-7]
    _text.insert(END, f"[{time}] 공통계약 찾기를 종료합니다.\n")
    _text.see(END)