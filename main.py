from datetime import datetime
import re
from config.UrlList import *
from ignore.config import *
import FinanceDataReader as fdr
import pymysql
from bs4 import BeautifulSoup
import requests

class KoreaInvestment():
    def __init__(self):
        super().__init__()
        self.Url_dict = Url.Url_dict
        self.config = config()
        self.MySqlGuest = self.config["MySqlGuest"] #host, user, password
        self.con, self.cur =self.ConnectMySql(self.MySqlGuest["host"],self.MySqlGuest["user"],self.MySqlGuest["password"])
        self.Dcon =self.ConnectMySqlForDataFrame(self.MySqlGuest["host"],self.MySqlGuest["user"],self.MySqlGuest["password"])

    def function_start(self):
        try:
            for url_name, url_info in self.Url_dict.items():
                url = url_info["URL"]
                url_class_name = url_info["ClassName"]
                self.get_news_from_crawling(url, url_name, url_class_name)

            self.extr_stocks_from_news()  # db에 있는 NEWS들중에 종목 추출 안된 종목 추출
        finally:
            self.con.close()


    def function_wiat(self):
        self.Insert()
        self.select("STOCKS")
        self.get_code_list_by_market("KOSDAQ")  # 코스닥, 장내  구할려고


    def get_news_from_crawling(self,url, url_name, ul_class_name):
        if url_name == "네이버금융_주요뉴스":
            news_list = self.for_naver_finance_news_article_add_more(url, url_name, ul_class_name)
        else:
            news_list = self.for_naver_finance_news_article_other(url, url_name, ul_class_name)

        #한 네이버 페이지 본문,img_link update
        self.update_detail_information(news_list)

        print(news_list)

        for one_news_dict in news_list:
            self.Insert(table_name="myDB.NEWS", dict=one_news_dict)

    def extr_stocks_from_news(self):# db에 있는 NEWS들중에 종목 추출 안된 종목 추출
        base_dict = dict()
        base_dict["ANAL_YN"] = 'N'
        news_tuple =self.select(TableName="myDB.NEWS",selectList=["SEQ", "OCCR_DT", "TITLE","TEXT"],where_dict=base_dict, orderbyacsList=["SEQ", "OCCR_DT"])
        base_dict =dict()
        stocks_tuple = self.select(TableName="myDB.STOCKS",selectList=["Market", "Symbol","Name"], orderbyacsList=["Market", "Symbol", "Name"])

        #NEWS순서
        SEQ     = 0
        OCCR_DT = 1
        TITLE   = 2
        TEXT    = 3

        #STOCKS순서
        Market = 0
        Symbol = 1
        Name   = 2

        test_list = list()
        for new_idx, one_news_tuple in enumerate(news_tuple):
            test_dict = dict()
            test_dict["SEQ"] = one_news_tuple[SEQ]
            test_dict["Symbol"] = list()
            # 같은 위치에서 발견되는 종목 삭제하기 위해서
            # ex: LG, LG화학
            idx_list = list() #지울수도
            dup_dict=dict()

            for stock_idx, one_stock_tuple in enumerate(stocks_tuple):
                # 같은 위치에서 발견되는 중복종목삭제
                find_idx = one_news_tuple[TEXT].find(one_stock_tuple[Name])
                if find_idx != -1:#발견시
                    idx_list.append(find_idx)
                    # find_index 기반으로 [5] =[005930, 001234]
                    if find_idx not in dup_dict :
                        dup_dict[find_idx] =[one_stock_tuple[Symbol]]
                    else:
                        dup_dict[find_idx].append([one_stock_tuple[Symbol]])


            for key, symbol_list  in dup_dict.items():
                #key =5 , symbol_list =[005930, 001234]
                max_name_symbol = ('','000000')

                if len(symbol_list) > 1 : # 2개 값 가지고있을때
                    for symbol in symbol_list:
                        for one_tuple in stocks_tuple:
                            if symbol in one_tuple:
                                if len(max_name_symbol[0]) <= len(one_tuple[Name]):
                                    max_name_symbol= (one_tuple[Name], one_tuple[Symbol])
                    test_dict["Symbol"].append(max_name_symbol[1])
                else: # 리스트의 값이 1개일때
                    test_dict["Symbol"].append(symbol_list[0])

            test_list.append(test_dict)

        for idx, one_dict  in enumerate(test_list):
            if len(one_dict['Symbol']) == 0: #추출된 종목이 없을때
                self.update(TableName="myDB.NEWS",setDict={"ANAL_YN": "Y", "EXTR_YN": "N"},where_dict={"SEQ": one_dict['SEQ']})
            else:
                self.update(TableName="myDB.NEWS", setDict={"ANAL_YN": "Y", "EXTR_YN": "Y", "EXTR_STCK_CD_LIST": one_dict['Symbol']},
                            where_dict={"SEQ": one_dict['SEQ']})

    def get_code_list_by_market(self, market_code):
        '''
        maket_code = "KOSPI", "KOSDAQ", "NASDAQ"

        '회사명':'Name',
        '종목코드':'Symbol',
        '업종':'Sector',
        '주요제품':'Industry',
        '상장일':'ListingDate',
        '결산월':'SettleMonth',
        '대표자명':'Representative',
        '지역':'Region',
           '''
        fdr_DataFrame =fdr.StockListing(market_code)
        #DB COLUMN SIZE에 안맞는것들 삭제
        fdr_DataFrame['ListingDate'] = fdr_DataFrame['ListingDate'].dt.strftime("%Y%m%d")
        fdr_DataFrame['SettleMonth'] = fdr_DataFrame['SettleMonth'].str[:-1]
        #DUP 데이터있을까봐 삭제
        fdr_DataFrame.drop_duplicates(['Symbol'], keep='first')

        #6자리 이상의 데이터가 있음 ex) 73501BB4 해당데이터 삭제
        fdr_DataFrame.drop(fdr_DataFrame[fdr_DataFrame["Symbol"].map(len) > 6].index, inplace=True)

        #DataFrame MySql Insert
        fdr_DataFrame.to_sql(name="STOCKS", con=self.Dcon, if_exists='append', index=False)

        # # Todo: 시장 종목 이름 업데이트 필요 있음
        # Market_name.Market["Name_Code"]


    def ConnectMySql(self,host,user,pwd):
        con = pymysql.connect(host=host, user=user, password=pwd,
                              db='mysql', charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()

        return con,cur

    def ConnectMySqlForDataFrame(self,host,user,pwd):
        from sqlalchemy import create_engine
        db_connection_str = f'mysql+pymysql://{user}:{pwd}@{host}/mysql'
        db_connection = create_engine(db_connection_str)
        conn = db_connection.connect()
        return conn

    def Insert(self,table_name='', dict=dict()):
        #key :col_name, value : data

        temp_str = f"INSERT INTO {table_name}("
        for key, value in dict.items():
            temp_str = temp_str + key + ','
        temp_str = temp_str[:-1] + ") VALUES ("

        for key, value in dict.items():
            #value에 ', " 변경
            if type(value) == str:
                value =value.replace("\'" , "\\\'")
            temp_str = temp_str + f"'{value}',"
        temp_str = temp_str[:-1] + ");"
        print(temp_str)

        try:
            self.cur.execute(temp_str)
            self.con.commit()
        except pymysql.Error as err:
            print("Something went wrong: {}".format(err))
            self.con.rollback()


    def InsertFromSelect(self, table_name, dict):
        # key :col_name, value : data
        test_dict = {'Market': 'KOSPI', 'Symbol': '006840', 'Name': 'AK홀딩스', 'Sector': '기타 금융업', 'Industry': '지주사업',
                     'ListingDate': '19990811', 'SettleMonth': '12', 'Representative': '채형석, 이석주(각자 대표이사)',
                     'HomePage': 'http://www.aekyunggroup.co.kr'}

        temp_str = f"INSERT INTO {table_name}("
        for key, value in dict.items():
            temp_str = temp_str + key + ','
        temp_str = temp_str[:-1] + ") SELECT "

        for key, value in dict.items():
            temp_str = temp_str + f"'{value}',"
        temp_str = temp_str[:-1] + f" FROM {table_name} "
        print(temp_str)

        # try:
        #     self.cur.execute(temp_str)
        #     self.con.commit()
        # except pymysql.Error as err:
        #     print("Something went wrong: {}".format(err))
        #     self.con.rollback()

        # DB 연결 종료
        # self.con.close()

    def select(self,TableName='', selectList=list(), where_dict=dict(), orderbyacsList=list()):

        # temp_str = f"SELECT * FROM {TableName} A WHERE ( '{Market}' = '' or A.Market = '{Market}')and ('{Symbol}'= '' or A.Symbol ='{Symbol}');"
        temp_str = f"SELECT * FROM {TableName} A "

        #select 절 추가하기
        if len(selectList) == 0:
            temp_str = f"SELECT * FROM {TableName} A "
        else:
            temp_str = f"SELECT  "
            for one_select in selectList:
                temp_str += f"{one_select} ,"
            temp_str = temp_str[:-1] +f" FROM {TableName} A "

        # where절 추가하기 key,value값없으면 그냥 조회한다
        if len(where_dict) != 0 :
            temp_str += "WHERE 1=1 "
            for key,value in where_dict.items():
                if type(value) == str:
                    temp_str += f"AND A.{key} = \'{value}\'"
                else:
                    temp_str += f"AND A.{key} = {value}"

        # order by 추가하기
        if len(orderbyacsList) != 0:
            temp_str += "order by "
            for one_value in orderbyacsList:
                temp_str += f"{one_value} ,"
            temp_str = temp_str[:-1]

        # print(temp_str)
        try:
            self.cur.execute(temp_str)
            rows = self.cur.fetchall()
            return rows

        except pymysql.Error as err:
            print("Something went wrong: {}".format(err))

    def update(self,TableName='', setDict=dict(), where_dict=dict()):

        temp_str = f"UPDATE {TableName} A SET "

        # SET 절 추가하기
        for key,value in setDict.items():
            if type(value) == str:
                temp_str += f"A.{key} = \'{value}\' ,"
            elif type(value) == list:
                temp_str += f"A.{key} = \'{','.join(value)}\' ,"
            else:
                temp_str += f"A.{key} = {value} ,"
        temp_str = temp_str[:-1]

        # where절 추가하기 key,value값없으면 그냥 조회한다
        if len(where_dict) != 0:
            temp_str += "WHERE 1=1 "
            for key,value in where_dict.items():
                if type(value) == str:
                    temp_str += f"AND A.{key} = \'{value}\'"
                elif type(value) == list:
                    temp_str += f"AND A.{key} = \'{','.join(value)}\'"
                else:
                    temp_str += f"AND A.{key} = {value}"


        print(temp_str)
        try:
            self.cur.execute(temp_str)
            self.con.commit()
        except pymysql.Error as err:
            print("Something went wrong: {}".format(err))
            self.con.rollback()

    def get_html(self, url):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
        # response = requests.get(url)
        response = requests.get(url, headers=headers)
        return response

    def parser(self, html):
        # return BeautifulSoup(html.content.decode('utf-8', 'replace'), 'html.parser')
        return BeautifulSoup(html.content.decode('euc-kr', 'replace'),'html.parser')


    def get_html_one_class_find(self,data, tag, name):
        return data.find(tag,name)


    def update_detail_information(self,news_list):
        for idx, one_news in enumerate(news_list):
            img_url_list = list()
            article_link = one_news["URL"]
            soup_1 = self.parser(self.get_html(article_link))
            main_article_html = soup_1.find("div", id="content")
            img_links = main_article_html.find_all("img", recursive=True)

            # 이미지가 없을경우
            if len(img_links) != 0:
                for idx2, img_link in enumerate(img_links):
                    img_url_list.append(img_link['src'])

            main_article_html.find('div', class_='link_news').decompose()  # 뒤에 잡다한 데이터가 들어와서

            # main_article = main_article_html.text.replace("\n","").replace("\t","")
            main_article = main_article_html.text.replace("\t", "")
            news_list[idx]["TEXT"] = main_article.strip()
            news_list[idx]["IMG_URL_LIST"] = ''.join(img_url_list)

        return news_list

    def for_naver_finance_news_article_other(self, url,url_name, ul_class_name):

        soup = self.parser(self.get_html(url))
        new_area_text = soup.find("ul", class_=ul_class_name).find("dl") # url에 해당되는 HTML에 맞는 태그 찾기

        news_list = list()
        for child in new_area_text.findChildren():
            #네이버증권의 [뉴스포커스] 탭은  'thumb(image), articleSubject(제목),articleSummary(요약)으로 이루어져있다.
            child_class = child.get("class")[0] if child.get("class") != None else " "
            if child_class == 'articleSubject':
                link = re.findall('href="(.+?)"', str(child))[0]
                title = re.findall("title=(.+?)</a>", str(child))[0]
                link = link.replace("amp;", "").replace("§","&sect")  # 네이버 링크에서 amp;라는 것 때문에 접근이 불가능하여 별도 처리  &sect -> § 처리됨
                news_list.append({"OCCR_DT": datetime.today().strftime("%Y%m%d"),
                                  "TITLE": title,
                                  "OCCR_LOC": url_name,
                                  "URL":  url[:url.find('/news/news_list')] + link
                                  })

        return news_list


    def for_naver_finance_news_article_add_more(self, url,url_name, ul_class_name):
        soup = self.parser(self.get_html(url))
        new_area_text = soup.find("ul", class_=ul_class_name).find_all("li", recursive=False)# url에 해당되는 HTML에 맞는 태그 찾기
        news_list = list()

        for idx, one_news in enumerate(new_area_text):
            a_tags =one_news.find_all("a", recursive=True)

            news = re.findall('href="(.+?)">(.+?)</a>', str(a_tags))[-1]
            link = news[0].replace("amp;", "").replace("§", "&sect")  # 네이버 링크에서 amp;라는 것 때문에 접근이 불가능하여 별도 처리  &sect -> § 처리됨
            news_list.append({"OCCR_DT": datetime.today().strftime("%Y%m%d"),
                              "TITLE": news[1],
                              "OCCR_LOC" : url_name,
                              "URL": url[:url.find('/news/mainnews.naver')] + link
                              })

        return news_list
