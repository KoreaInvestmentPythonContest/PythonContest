from datetime import datetime
import re
from config.UrlList import *
from config.Market import *
from ignore.config import *
import FinanceDataReader as fdr
import pymysql

from bs4 import BeautifulSoup
from kiwipiepy import Kiwi
import requests
class KoreaInvestment():
    def __init__(self):
        super().__init__()
        self.market = Market_name.Market
        self.Url_list = Url_List.Url
        self.config = config()
        self.MySqlGuest = self.config["MySqlGuest"] #host, user, password
        self.con, self.cur =self.ConnectMySql(self.MySqlGuest["host"],self.MySqlGuest["user"],self.MySqlGuest["password"])
        self.Dcon =self.ConnectMySqlForDataFrame(self.MySqlGuest["host"],self.MySqlGuest["user"],self.MySqlGuest["password"])

    def function_start(self):
        try:
            with self.cur:
                news_list = self.for_naver_finance_news_article_add_more(self.Url_list["네이버금융_주요뉴스"])
                for one_news_dict in news_list:
                    self.Insert("myDB.NEWS", one_news_dict)

        # DB 연결 종료
        finally:
            self.con.close()



    def function_wiat(self):
        self.Insert()

        self.select("STOCKS")
        self.get_code_list_by_market("KOSDAQ")  # 코스닥, 장내  구할려고



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


    def Kiwi_morphological_analysis(self):
        print("test")

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

    def Insert(self,table_name,dict):
        #key :col_name, value : data
        test_dict = {'Market': 'KOSPI', 'Symbol': '006840', 'Name': 'AK홀딩스', 'Sector': '기타 금융업', 'Industry': '지주사업',
                     'ListingDate': '19990811', 'SettleMonth': '12', 'Representative': '채형석, 이석주(각자 대표이사)',
                     'HomePage': 'http://www.aekyunggroup.co.kr'}



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

        # DB 연결 종료
        # finally:
        #     self.con.close()

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

    def select(self,TableName='',Market='',Symbol=''):
        temp_str = f"SELECT * FROM {TableName} A WHERE ( '{Market}' = '' or A.Market = '{Market}')and ('{Symbol}'= '' or A.Symbol ='{Symbol}');"

        try:
            self.cur.execute(temp_str)
            rows = self.cur.fetchall()
            for row in rows:
                print(row)

        except pymysql.Error as err:
            print("Something went wrong: {}".format(err))


    def get_html(self,url):
        headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
        response = requests.get(url)
        # response = requests.get(url, headers=headers)
        return response

    def parser(self, html):
        return BeautifulSoup(html.content.decode('euc-kr', 'replace'),'html.parser')


    def get_html_one_class_find(self,data, tag, name):
        return data.find(tag,name)



    def for_naver_finance_news_article(self,url):
        soup = self.parser(self.get_html(url))
        a_tag_list = soup.find("div", "news_area").find_all("a", recursive=True)
        news_list = list()

        for idx, one_news in enumerate(a_tag_list):
            news = re.findall('href="(.+?)">(.+?)</a>', str(one_news))[0]
            link = news[0].replace("amp;", "")  # 네이버 링크에서 amp;라는 것 때문에 접근이 불가능하여 별도 처리
            print("link",link)
            news_list.append({ "title" : news[1],
                                "link" : url+link[:link.find(r'"')]
                             })

        # print(news_list)
        for idx, one_news in enumerate(news_list):
            # if idx == 0:
            article_link = one_news["link"]
            soup_1 = self.parser(self.get_html(article_link))
            main_article_html = soup_1.find("div",id="content")
            # print(idx,one_news,main_article_html)
            # main_article_html.find('div',class_='link_news').decompose()
            # main_article = main_article_html.text
            # news_list[idx]["main_text"] = main_article




        return news_list

    def for_naver_finance_news_article_add_more(self,url):
        soup = self.parser(self.get_html(url))
        new_area_text = soup.find("ul", class_="newsList").find_all("li", recursive=False)
        news_list = list()


        for idx, one_news in enumerate(new_area_text):
            # if idx == 2:
            a_tags =one_news.find_all("a", recursive=True)
            news = re.findall('href="(.+?)">(.+?)</a>', str(a_tags))[-1]
            # print(f"news: {news}")
            link = news[0].replace("amp;", "")  # 네이버 링크에서 amp;라는 것 때문에 접근이 불가능하여 별도 처리
            # print(f"link: {link}")
            news_list.append({"OCCR_DT": datetime.today().strftime("%Y%m%d"),
                              "TITLE": news[1],
                              "OCCR_LOC" : "네이버금융_주요뉴스",
                              "URL": url[:url.find('/news/mainnews.naver')] + link
                              })

        # print(f"new_list : {news_list}")
        for idx, one_news in enumerate(news_list):
            img_url_list = list()
            # if idx == 0:
            article_link = one_news["URL"]
            soup_1 = self.parser(self.get_html(article_link))
            main_article_html = soup_1.find("div",id="content")
            img_links =main_article_html.find_all("img", recursive=True)

            #이미지가 없을경우
            if len(img_links) != 0:

                for idx2, img_link in enumerate(img_links):
                    img_url_list.append(img_link['src'])

            main_article_html.find('div',class_='link_news').decompose() #뒤에 잡다한 데이터가 들어와서

            # main_article = main_article_html.text.replace("\n","").replace("\t","")
            main_article = main_article_html.text.replace("\t", "")
            news_list[idx]["TEXT"] = main_article.strip()
            news_list[idx]["IMG_URL_LIST"] = ''.join(img_url_list)
            # print(news_list[idx])

        return news_list








