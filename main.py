import re
from config.UrlList import *
from config.Market import *
from ignore.config import *


from bs4 import BeautifulSoup
import requests
class KoreaInvestment():
    def __init__(self):
        super().__init__()
        self.market = Market_name.Market
        self.Url_list = Url_List.Url
        self.config = config()

    def function_start(self):
        self.for_naver_finance_news_article_add_more(self.Url_list["네이버금융_주요뉴스"])

    def function_wiat(self):
        self.for_naver_finance_news_article_add_more(self.Url_list["네이버금융_주요뉴스"])

        self.get_name_list_by_code()  # 코스닥, 장내  구할려고

    def get_name_list_by_code(self) : #코스피,코스닥  구할려고
        code_name_list = list()
        aa = dict()
        code_list_kospi = self.get_code_list_by_market("11")
        # code_list_kosdac = self.get_code_list_by_market("12")
        # print(f"코스닥개수:{len(code_list_kosdac)}")
        # print(f"장내:{len(code_list_kospi)}")
        #
        #
        # # Todo: 시장 종목 이름 업데이트 필요 있음
        # Market_name.Market["Name_Code"]



    def get_code_list_by_market(self, market_code):
        """
        [시장구분값]
          11 : 유가증권
          12 : 코스닥시장
          13 : 코넥스시장
          """
        name ="한국예탁결제원_주식정보서비스"
        url = self.Url_list[name]
        params = {'serviceKey': self.config[name], 'caltotMartTpcd': market_code}

        response = requests.get(url, params=params)
        print(response.content)
        # code_list = code_list.split(";")[:-1]
        # return code_list


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
            # if idx == 0:
            a_tags =one_news.find_all("a", recursive=True)
            # print(f"a_tags: {a_tags} ")
            news = re.findall('href="(.+?)">(.+?)</a>', str(a_tags))[-1]
            # print(f"news: {news}")
            link = news[0].replace("amp;", "")  # 네이버 링크에서 amp;라는 것 때문에 접근이 불가능하여 별도 처리
            # print(f"link: {link}")
            news_list.append({"title": news[1],
                              "link": url[:url.find('/news/mainnews.naver')] + link
                              })

        # print(f"new_list : {news_list}")
        for idx, one_news in enumerate(news_list):
            # if idx == 0:
                article_link = one_news["link"]
                soup_1 = self.parser(self.get_html(article_link))
                main_article_html = soup_1.find("div",id="content")
                # print(idx,one_news,main_article_html)
                main_article_html.find('div',class_='link_news').decompose()
                main_article = main_article_html.text.replace("\n","").replace("\t","")
                news_list[idx]["main_text"] = main_article
                print(news_list[idx])

        return news_list








