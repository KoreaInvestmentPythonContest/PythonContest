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



def for_naver_finance_news_article(url):
    soup = parser(get_html(url))
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
        soup_1 = parser(get_html(article_link))
        main_article_html = soup_1.find("div",id="content")
        # print(idx,one_news,main_article_html)
        # main_article_html.find('div',class_='link_news').decompose()
        # main_article = main_article_html.text
        # news_list[idx]["main_text"] = main_article




    return news_list

def for_naver_finance_news_article_add_more(url):
    soup = parser(get_html(url))
    new_area_text = soup.find("ul", class_="newsList").find_all("li", recursive=False)
    news_list = list()


    for idx, one_news in enumerate(new_area_text):
        # if idx == 0:
        a_tags =one_news.find_all("a", recursive=True)
        # print(f"a_tags: {a_tags} ")
        news = re.findall('href="(.+?)">(.+?)</a>', str(a_tags))[0]
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
            soup_1 = parser(get_html(article_link))
            main_article_html = soup_1.find("div",id="content")
            # print(idx,one_news,main_article_html)
            main_article_html.find('div',class_='link_news').decompose()
            main_article = main_article_html.text
            news_list[idx]["main_text"] = main_article
            print(news_list[idx])

    return news_list

if __name__ == '__main__':
    url_list = {'네이버금융': 'https://finance.naver.com',
                '네이버뉴스':'https://news.naver.com',
                '네이버금융_주요뉴스' : 'https://finance.naver.com/news/mainnews.naver'

                }
    # url = url_list['네이버금융']
    # temps =for_naver_finance_news_article(url)

    url = url_list['네이버금융_주요뉴스']
    temps = for_naver_finance_news_article_add_more(url)







