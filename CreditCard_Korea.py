#-*- coding: utf-8 -*-
import re
import time
import sys
import getopt
import os
import zipfile
import shutil
import io
# 설치해야할 모듈
import xlrd
from PyPDF2 import PdfFileReader


def checksum(string):
    '''
    Luhn 알고리즘 확인
    True/False 검증
    '''
    odd_sum = sum(list(map(int, string))[-1::-2])
    even_sum = sum([sum(divmod(2 * d, 10)) for d in list(map(int, string))[-2::-2]])
    return ((odd_sum + even_sum) % 10 == 0)


def searchInLine(textLine, line_position, cc_path, regex_list, mask):
    '''
    텍스트 줄 내에서 신용 카드 번호 검증
    발견되면 1 반환 , 그렇지 않으면 0 반환
    '''
    counter = 0
    for regEx in regex_list:
        m = re.finditer(r"%s" % regEx[1], textLine)
        for match in m:
            if mask:
                print(cc_path + "\t" + line_position + "\t" + regEx[0].rstrip() + "\t" +
                      match.group()[:0] + "" + match.group()[0:])
            else:
                print(cc_path + "\t" + line_position + "\t" +
                      regEx[0].rstrip() + "\t" + match.group())
            counter += 1
    return counter

## 카드번호 필터 사용
    
# def searchInLine(textLine, line_position, cc_path, regex_list, mask):
#     '''
#     텍스트 줄 내에서 신용 카드 번호 검증
#     발견되면 1 반환 , 그렇지 않으면 0 반환
#     카드번호 7자리부터 ****** 6자리 필터
#     '''
#     counter = 0
#     for regEx in regex_list:
#         m = re.finditer(r"%s" % regEx[1], textLine)
#         for match in m:
#             if mask:
#                 print(cc_path + "\t" + line_position + "\t" + regEx[0].rstrip() + "\t" +
#                       match.group()[:6] + "******" + match.group()[-4:])
#             else:
#                 print(cc_path + "\t" + line_position + "\t" +
#                       regEx[0].rstrip() + "\t" + match.group())
#             counter += 1
#     return counter


def textFSearch(cc_path, regex_list, mask):
    '''
    txt 파일 내에서 신용카드 번호 서치
    발견 된 총 신용 카드를 반환
    '''
    counter = 0
    line_counter = 1
    with open(cc_path, 'r', encoding="latin-1") as cc_file_data:
        for cc_file_line in cc_file_data:
            counter += searchInLine(cc_file_line, "Line_" +
                                    str(line_counter), cc_path, regex_list, mask)
            line_counter += 1
    return counter


def pdfFSearch(cc_path, regex_list, mask):
    '''
    pdf 파일 내에서 신용카드 번호 서치
    발견 된 총 신용 카드를 반환
    '''
    pdfCounter = 0  # pdf에서 찾은 총 CC 번호를 저장
    pdfPageCount = 0  # 페이지 반복 카운터
    text = ""  # 추출 된 모든 텍스트를 포함

    pdfReader = PdfFileReader(open(cc_path, 'rb'))
    # While 루프는 각 페이지를 읽습니다.
    while pdfPageCount < pdfReader.numPages:
        pageObj = pdfReader.getPage(pdfPageCount)
        pdfPageCount += 1
        text += pageObj.extractText()
        buf = io.StringIO(pageObj.extractText())
        linecount = 0
        for line in buf:
            linecount += 1
            pdfCounter += searchInLine(line, "Page" + str(pdfPageCount) +
                                       "_Line" + str(linecount), cc_path, regex_list, mask)
    # PDF에 포함 된 모든 것이 스캔 된 경우 (PyPDF는 이미지에서 텍스트를 추출 할 수 없음)
    if text == "":
        print(cc_path + " --> PDF file contains no text")
    return pdfCounter


def excelFSearch(cc_path, regex_list, mask):
    '''
    xls, xlsx 파일 내에서 신용카드 번호 서치
    발견 된 총 신용 카드를 반환
    '''
    counter = 0
    with xlrd.open_workbook(cc_path) as wb:
        for sheet in wb.sheets():
            for row in range(sheet.nrows):
                counter += searchInLine(','.join(sheet.row_values(row)),
                                        str(sheet.name) + "_row" + str(row), cc_path, regex_list, mask)
    return counter


def zipFSearch(cc_path, regex_list, mask):
    '''
    zip 파일 내에서 신용카드 번호 서치
    발견 된 총 신용 카드를 반환
    '''
    zipCount = 0
    with zipfile.ZipFile(cc_path, 'r') as zfile:
        print("-- Opening ZIP FILE --> " + cc_path)
        for finfo in zfile.infolist():
            fileCount = 0
            fileCount += searchInFile(zfile.extract(finfo), regex_list, mask)
            fileCount = (0 if fileCount < 0 else fileCount)
            print(os.path.join(cc_path, finfo.filename) + " --> " +
                  str(fileCount) + " credit cards in file - Inside ZIP file")
            zipCount += fileCount
            if "/" in finfo.filename:
                shutil.rmtree(finfo.filename.split("/")[0])
            else:
                os.remove(finfo.filename)
    print("-- End of ZIP FILE --> " + cc_path)
    return zipCount


def searchInFile(cc_path, regex_list, mask):
    '''
    파일이 지원되지 않으면 -1 반환
    '''
    if any(cc_path[-3:].lower() in s for s in unsupported_files):
        print(cc_path + " --> Unsupported file")
        return -1
    elif any(cc_path[-3:].lower() in s for s in ['xls', 'xlsx']):
        return excelFSearch(cc_path, regex_list, mask)
    elif any(cc_path[-3:].lower() in s for s in ['pdf']):
        return pdfFSearch(cc_path, regex_list, mask)
    elif zipfile.is_zipfile(cc_path):
        return zipFSearch(cc_path, regex_list, mask)
    else:
        return textFSearch(cc_path, regex_list, mask)


def searchInDir(cc_path, regex_list, mask):
    '''
    지정된 경로에 포함 된 파일에서 신용 카드 검색
    신용 카드가 포함 된 튜플을 반환
    '''
    count_cc_total = 0  # Total credit cards found in files
    count_nocc_files = 0  # Files containing no credit cards
    count_discarded_files = 0  # Files discarded because they are not supported
    count_cc_files = 0  # Files containing credit cards

    # 주어진 경로를 반복
    for root, dirs, files in os.walk(cc_path):
        for filename in files:
            count_fichero = searchInFile(
                os.path.join(root, filename), regex_list, mask)
            # CC가 발견 된 경우
            if count_fichero > 0:
                count_cc_files += 1
                print(os.path.join(root, filename) + " --> " +
                      str(count_fichero) + " credit cards in file")
            # CC가없는 경우
            elif count_fichero == 0:
                print(os.path.join(root, filename) + " --> " +
                      str(count_fichero) + " credit cards in file")
                count_nocc_files += 1
            # 파일이 폐기 된 경우
            elif count_fichero < 0:
                count_discarded_files += 1
                count_fichero = 0
            # 실행 중에 발견 된 총 CC 추가
            count_cc_total += count_fichero
    return count_cc_files + count_discarded_files + count_nocc_files, count_cc_files + count_nocc_files, count_discarded_files, count_cc_files, count_cc_total


if __name__ == '__main__':
    inputfile = ''
    inputdir = ''
    masking = True
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:d:m")
    except getopt.GetoptError:
        #  기본 옵션으로 현재 dir 파일 읽기
        print('Syntax: CreditCard_Korea.py -i </파일명> -d <inputdirectory> [-m] ')
        sys.exit(2)
    if not opts:
        print('Syntax: CreditCard_Korea.py -i </파일명> -d <inputdirectory> [-m] ')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('Usage CreditCardSearch.py -i </파일명> -d <inputdirectory> -o <outputfile> -m')
            sys.exit()
        elif opt in ("-i"):
            inputfile = arg
        elif opt in ("-d"):
            inputdir = arg
        elif opt in ("-m"):
            masking = False

    # 파일 확장자 지원 변수
    tested_files = ['txt', 'csv', 'xls', 'xlsx', 'rtf', 'xml', 'html', 'json', 'zip', 'pdf']
    unsupported_files = ['doc', 'docx', 'pptx', 'jpg', 'gif',
                         'png', 'mp3', 'mp4', 'wav', 'aiff', 'mkv', 'avi', 'exe', 'dll']

    # Print memo when the script starts
    print("[" + time.ctime() + "] CreditCardSearch started")

    # 카드사 대조 할 CSV 정규식 파일 호출
    regex_path = 'Korea.csv'
    regex_list = []
    with open(regex_path, 'r') as regex_file:
        for line in regex_file:
            line_list = line.rstrip().split(',')
            regex_list.append(line_list)

    # 스크립트가 검색 할 디렉토리를받은 경우
    if inputdir:
        dirResult = searchInDir(inputdir, regex_list, masking)
        print("--- Execution Summary ---")
        print(str(dirResult[0]) + "\tFiles read")
        print(str(dirResult[1]) + "\tFiles analyzed")
        print(str(dirResult[2]) + "\tFiles unsupported")
        print(str(dirResult[3]) + "\tFiles including credit cards")
        print(str(dirResult[4]) + "\tTotal credit cards found")

    # 스크립트가 분석 할 단일 파일을받은 경우
    elif inputfile:
        print(inputfile + " --> " + str(searchInFile(inputfile,
                                                     regex_list, masking)) + " credit cards in file\n")

    print("\n--- 설명 ---")
    print("파일에 포함 된 데이터를 읽으려고 시도하였으며 알려진 지원되지 않는 파일을 제외")
    print("테스트 된 파일: %s" % ','.join(tested_files))
    print("지원되지 않는 파일: %s" % ','.join(unsupported_files))
