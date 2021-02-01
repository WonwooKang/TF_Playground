# -*- coding: utf-8 -*-

from typing import List
from konlpy.tag import Okt
from textrankr import TextRank
from app.utils.SeleniumManager import SeleniumManager, driver_clear


class OktTokenizer:
    okt: Okt = Okt()

    def __call__(self, text: str) -> List[str]:
        tokens: List[str] = self.okt.phrases(text)
        return tokens


ok_tokenizer: OktTokenizer = OktTokenizer()


def summarize(text):
    text_rank: TextRank = TextRank(ok_tokenizer)

    k: int = 3  # num sentences in the resulting summary
    # summarized: str = text_rank.summarize(ex_text1, k)
    # print(summarized)  # gives you some text

    summaries: List[str] = text_rank.summarize(text, k, verbose=False)
    for i, summary in enumerate(summaries):
        print(i + 1, summary)  # 나중에 리턴할 부분


def get_article_and_summarize():
    selenium_manager = SeleniumManager(headless=True)
    driver = selenium_manager.get_selenium_driver()

    driver.get('https://news.joins.com/article/23983859')
    article = driver.find_element_by_id('article_body').text
    print(article)
    summarize(article)

    print('===============')
    driver = selenium_manager.get_selenium_driver()
    driver.get('https://news.joins.com/article/23983802')
    article = driver.find_element_by_id('article_body').text
    print(article)
    summarize(article)

    print('===============')
    driver = selenium_manager.get_selenium_driver()
    driver.get('https://news.joins.com/article/23983804')
    article = driver.find_element_by_id('article_body').text
    print(article)
    summarize(article)

    selenium_manager.quit()


if __name__ == '__main__':
    get_article_and_summarize()
