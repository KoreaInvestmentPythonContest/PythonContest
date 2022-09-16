
import pymysql


def  Connect():
    con = pymysql.connect(host='ec2-34-226-124-76.compute-1.amazonaws.com', user='guest', password='12345678',
                      db='mysql', charset='utf8')  # 한글처리 (charset = 'utf8')
    cur = con.cursor()


    test_dict = { 'Market': 'KOSPI','Symbol': '006840', 'Name': 'AK홀딩스', 'Sector': '기타 금융업', 'Industry': '지주사업',
     'ListingDate': '19990811', 'SettleMonth': '12', 'Representative': '채형석, 이석주(각자 대표이사)',
     'HomePage': 'http://www.aekyunggroup.co.kr'}

    insert_data = "INSERT INTO  STOCKS( Market, Symbol, Name, Sector, Industry, ListingDate, SettleMonth, Representative, HomePage)" \
                  f"VALUES ({test_dict['Market']},{test_dict['Symbol']},{test_dict['Name']},{test_dict['Sector']},{test_dict['Industry']}," \
                  f"{test_dict['ListingDate']},{test_dict['SettleMonth']},{test_dict['Representative']},{test_dict['HomePage']})"

    temp_str= "INSERT INTO STOCKS("
    for key,value in test_dict.items():
        temp_str =temp_str + key + ','
    temp_str =temp_str[:-1] +") VALUES ("
    for key,value in test_dict.items():
        temp_str = temp_str + f"'{value}',"
    temp_str = temp_str[:-1] +");"
    print(temp_str)

    try:
        cur.execute(temp_str)
        con.commit()
    except pymysql.Error as err:
        print("Something went wrong: {}".format(err))
        con.rollback()
    # 데이타 Fetch
    # for one_fetch in cur.fetchall():
    #     print(one_fetch)  # 전체 rows

    # STEP 5: DB 연결 종료
    con.close()

if __name__ == "__main__":
    Connect()