from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from lxml import html

from ..schemas import Portfolio, Transaction


def parse_file(filename: str) -> Portfolio:
    parser = html.HTMLParser(encoding='koi8-r')
    doc = html.parse(filename, parser=parser)
    lines = doc.xpath('//table[@width="900"]/tr')

    result: Portfolio = defaultdict(list)
    ticker = None
    for line in lines[1:]:
        if len(line) == 1:
            ticker = line.xpath('.//b/text()')[0]
        elif len(line) == 11:
            result[ticker].append(Transaction(
                timestamp=datetime.strptime(f'{line[1][0].text.strip()} {line[2][0].text.strip()}', '%d.%m.%Y %H:%M:%S'),
                reason=line[3][0].text.strip() == 'Покупка',
                count=int(line[4][0].text.strip()),
                price=Decimal(line[5][0].text.strip())
            ))
    return result
