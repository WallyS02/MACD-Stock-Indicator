import pandas as pd
import jupyter
import os


def EMA(samples, periods, today):
    alpha = 2/(periods+1)
    alphaCalc = 1 - alpha
    nominator = samples[today]
    denominator = 1.0
    for i in range(0, periods):
        denominator = denominator + pow(alphaCalc, i)
        nominator = nominator + pow(alphaCalc, i) * samples[i+today]
    return nominator / denominator


def MACD(samples, today):
    EMA_12 = EMA(samples, 12, today)
    EMA_26 = EMA(samples, 26, today)
    return EMA_12 - EMA_26


def SIGNAL(MACDsamples, index):
    return EMA(MACDsamples, 9, index)


def CSVinput():
    path = os.path.dirname(os.path.abspath(__file__))
    path = path + "\\Quotes\\"
    #filename = input('Input file name to process it: ')
    filename = 'Dogecoin'
    path = path + filename
    path = path + '.csv'
    samples = pd.read_csv(path, usecols=['Zamkniecie'], nrows=1000)
    return samples


def output():
    print()


def main():
    samples = CSVinput()
    MACDsamples = []
    SIGNALsamples = []


if __name__ == '__main__':
    main()
