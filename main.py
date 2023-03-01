import pandas as pd
import matplotlib.pyplot as plt
import os


def EMA(samples, periods, today, isDataFrame):
    alpha = 2/(periods+1)
    alphaCalc = 1 - alpha
    nominator = 0.0
    denominator = 0.0
    for i in range(0, periods):
        denominator = denominator + pow(alphaCalc, i)
        if isDataFrame is True:
            nominator = nominator + pow(alphaCalc, i) * samples.loc[i+today]["Zamkniecie"]
        else:
            nominator = nominator + pow(alphaCalc, i) * samples[i+today]
    return nominator / denominator


def MACD(samples, today):
    EMA_12 = EMA(samples, 12, today, True)
    EMA_26 = EMA(samples, 26, today, True)
    return EMA_12 - EMA_26


def SIGNAL(MACDsamples, index):
    return EMA(MACDsamples, 9, index, False)


def CSVinput():
    path = os.path.dirname(os.path.abspath(__file__))
    path = path + "\\Quotes\\"
    #filename = input('Input file name to process it: ')
    filename = 'CD project'
    path = path + filename
    path = path + '.csv'
    samples = pd.read_csv(path, usecols=['Zamkniecie'], nrows=1035)
    return samples


def output(MACDsamples, SIGNALsamples):
    plt.style.use('_mpl-gallery')
    fig, ax = plt.subplots()
    x = [i for i in range(0, 1000)]
    for i in range(0, 9):
        MACDsamples.pop()
    ax.plot(x, MACDsamples, linewidth=2.0)
    ax.plot(x, SIGNALsamples, linewidth=2.0)
    plt.show()


def main():
    samples = CSVinput()
    MACDsamples = []
    SIGNALsamples = []
    for i in range(0, 1009):
        MACDsamples.insert(i, MACD(samples, i))
    for i in range(0, 1000):
        SIGNALsamples.insert(i, SIGNAL(MACDsamples, i))
    output(MACDsamples, SIGNALsamples)


if __name__ == '__main__':
    main()
