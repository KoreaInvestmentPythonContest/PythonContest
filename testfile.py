from konlpy.tag import Kkma, Komoran, Okt

# 형태소 분석기 정의

# okt = Okt()

# kkm = Kkma()

# kom = Komoran()

#형태소를 분석할 텍스트 정의

text = '마음에 꽂힌 칼한자루 보다 마음에 꽂힌 꽃한송이가 더 아파서 잠이 오지 않는다'



# 형태소 분석기의 pos메소드를 이용해 형태소를 분석

kom.pos(text)

kkm.pos(text)

okt.pos(text,norm=True, stem=True)