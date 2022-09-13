import re

from bs4 import BeautifulSoup
import requests

def get_html(url):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    response = requests.get(url)
    # response = requests.get(url, headers=headers)
    return response

def parser(html):
    return BeautifulSoup(html.content.decode('euc-kr', 'replace'),'html.parser')


def get_html_one_class_find(data, tag, name):
    return data.find(tag,name)



def for_naver_finance_new_article(url):
    soup = parser(get_html(url))
    new_area_text = soup.find("div", "news_area").find_all("a", recursive=True)
    new_title_link =dict()
    for idx, one_news in enumerate(new_area_text):
        news = re.findall('href="(.+?)">(.+?)</a>', str(one_news))[0]
        link = news[0].replace("amp;", "")  # 네이버 링크에서 amp;라는 것 때문에 접근이 불가능하여 별도 처리
        new_title_link[news[1]] = url+link[:link.find(r'"')]


    for idx, tmp in enumerate(new_title_link):
        print(idx,tmp,new_title_link[tmp])
        if idx == 0:
            article_link = new_title_link[tmp]
            soup_1 = parser(get_html(article_link))
            # main_article = soup_1.find_all("div",id="content")
            main_article = soup_1.find("div", {'id': 'content'}).text
            print(main_article)ee



    return new_title_link

if __name__ == '__main__':
    url_list = {'네이버금융': 'https://finance.naver.com', '네이버뉴스':'https://news.naver.com'}
    url = url_list['네이버금융']
    temps =for_naver_finance_new_article(url)







