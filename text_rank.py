# -*- coding: utf-8 -*-

from typing import List
from konlpy.tag import Okt
from textrankr import TextRank


class OktTokenizer:
    okt: Okt = Okt()

    def __call__(self, text: str) -> List[str]:
        tokens: List[str] = self.okt.phrases(text)
        return tokens


ex_text1 = \
    "SK바이오팜은 혁신 신약 '세노바메이트'가 유럽의약품청(EMA) 산하 약물사용자문위원회(CHMP)로부터 판매 승인 권고를 받았다고 1일 밝혔다.\n\
유럽연합 집행위원회(EC·European Commission)의 최종 승인이 CHMP 권고일로부터 약 67일 내 이뤄진다.\n\
이에 따라 세노바메이트가 올해 2분기 내 시판 허가를 획득할 전망이다.\n\
유럽은 세계에서 두 번째로 큰 뇌전증 치료제 시장으로, 세계보건기구(WHO) 데이터에 따르면 약 600만명의 환자가 있는 것으로 추정된다.\n\
세노바메이트는 SK바이오팜이 자체 개발해 2019년 11월 미국 FDA 승인을 받은 뇌전증 치료제(미국 제품명 엑스코프리/ XCOPRI®)로, 유럽에서는 파트너사인 안젤리니파마를 통해 ‘온투즈리(ONTOZRYTM)’라는 제품명으로 출시될 예정이다.\n\
안젤리니파마는 지난 100년 동안 상업화 역량을 갖춘 전통 제약사로, 15개 현지 법인과 70여개국 유통망을 통해 독일, 프랑스, 영국, 스위스 등 유럽 주요국가들을 적극적으로 공략해 나간다는 계획이다.\n\
SK바이오팜 조정우 사장은 \"CHMP의 판매 승인 권고는 SK바이오팜이 지난 20여년 동안 개발한 세노바메이트를 유럽 뇌전증 환자들에게 제공하는데 중요한 이정표가 될 것\"이라며 \"혁신 신약을 성공적으로 출시할 수 있도록 파트너사와 긴밀히 협력해 나가겠다\"고 말했다.\n\
안젤리니파마 피에루이지 안토넬리(Pierluigi Antonelli) 사장은 \"세노바메이트의 CHMP 판매 승인 권고는 안젤리니파마에 있어 기념비적인 일\"이라며 \"혁신적인 포트폴리오를 통해 중추신경계(CNS) 환자들의 니즈를 충족시킬 수 있는 유럽 선두주자가 되겠다\"고 말했다.\n\
한편 세노바메이트가 유럽 허가를 획득할 경우 SK바이오팜은 안젤리니파마로부터 최대 4억 3000만달러의 단계별 마일스톤을 수령하게 된다. 판매가 본격화되면 매출에 따른 로열티는 별도로 받는다. 지난해 12월 기술수출 계약 국가가 32개국에서 41개국으로 확대되면서 수익 규모는 더욱 증가할 전망이다.\n\
SK바이오팜은 세노바메이트의 유럽 상업화를 위해 지난 2019년 스위스 제약사 아벨 테라퓨틱스(이하 아벨)와 라이선스 계약을 체결했다. 최근 아벨이 이탈리아 대표 제약사이자 중추신경계(CNS)에 특화된 안젤리니파마에 인수되면서 세노바메이트의 상업화 권리도 함께 양도됐다."


if __name__ == '__main__':
    ok_tokenizer: OktTokenizer = OktTokenizer()
    text_rank: TextRank = TextRank(ok_tokenizer)

    k: int = 3  # num sentences in the resulting summary
    #
    # summarized: str = text_rank.summarize(ex_text1, k)
    # print(summarized)  # gives you some text

    summaries: List[str] = text_rank.summarize(ex_text1, k, verbose=False)
    for i, summary in enumerate(summaries):
        print(i+1, summary)























