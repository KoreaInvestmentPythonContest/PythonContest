
import pymysql


def  Connect():
    con = pymysql.connect(host='ec2-34-226-124-76.compute-1.amazonaws.com', user='guest', password='12345678',
                      db='mysql', charset='utf8')  # 한글처리 (charset = 'utf8')
    cur = con.cursor()

    sql = "SELECT *  FROM NEWS"
    cur.execute(sql)

    # 데이타 Fetch
    for one_fetch in cur.fetchall():
        print(one_fetch)  # 전체 rows

    # STEP 5: DB 연결 종료
    con.close()

if __name__ == "__main__":
    Connect()