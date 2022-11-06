#!/usr/bin/env python3
import argparse
from typing import Optional

from matplotlib import pyplot

from . import brokers
from .schemas import Transaction


DEBUG: Optional[str] = None


def partial_accounting(deals: list[Transaction]) -> list[Transaction]:
    # не очень хорошая идея менять входящий массив
    # можно воспользоваться deepcopy
    start_item = 0

    try:
        for item in deals:
            if not item.reason:  # если продажа
                sell = item.count  # сколько осталось вычесть из партий
                while sell > 0:
                    left = deals[start_item].count  # акций осталось в партии-покупке
                    current = left - sell
                    if current > 0:
                        # в партии-покупке не всё исчерпали -> обновим количество и выходим
                        sell = 0
                        deals[start_item].count = current
                    else:
                        # партия-покупка распродана полностью
                        sell = sell - left  # обновляем сколько надо распродать
                        start_item += 1
                        while not deals[start_item].reason:
                            # ищем следующую партию-покупку
                            start_item += 1
        return [deal for deal in deals[start_item:] if deal.reason]
    except IndexError:
        # всё распродали
        return []


def plot(key: str, deals: list[Transaction]):
    if len(deals) == 0:
        print(f'Empty data for {key}')
        return
    x_values = [x.timestamp.strftime('%d.%m.%Y') for x in deals]
    y_values = [float(x.price) for x in deals]
    sizes = [x.count for x in deals]

    fig, ax = pyplot.subplots()
    ax.scatter(x_values, y_values, s=sizes)
    fig.autofmt_xdate()
    fig.set_size_inches(15, 10)
    if DEBUG:
        pyplot.show()
    else:
        pyplot.savefig(f'plots/{key}.png')
    pyplot.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help='Data source')
    parser.add_argument('--broker', type=str, help='Your broker')
    args = parser.parse_args()

    # importer = import_module(f'.brokers.{args.broker}')
    importer = getattr(brokers, args.broker)
    portfolio = importer(args.filename)

    if DEBUG is not None:
        parties = {DEBUG: partial_accounting(portfolio[DEBUG])}
        plot(DEBUG, parties[DEBUG])
    else:
        parties = {name: partial_accounting(value) for name, value in portfolio.items()}
        for key in parties:
            plot(key, parties[key])
