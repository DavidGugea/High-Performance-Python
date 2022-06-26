from random import normalvariate, randint
from itertools import count
from datetime import datetime


def read_data(filename):
    with open(filename) as fd:
        for line in fd:
            data = line.strip().split(',')
            timestamp, value = map(int, data)
            yield datetime.fromtimestamp(timestamp), value


def read_fake_data(filename):
    for timestamp in count():
        #  We insert an anomalous data point approximately once a week
        if randint(0, 7 * 60 * 60 * 24 - 1) == 1:
            value = normalvariate(0, 1)
        else:
            value = 100

        yield datetime.fromtimestamp(timestamp), value
