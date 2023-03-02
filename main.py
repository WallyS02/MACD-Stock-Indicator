from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib


def EMA(samples, periods, today, isDataFrame):
    alpha = 2 / (periods + 1)
    alphaCalc = 1 - alpha
    nominator = 0.0
    denominator = 0.0
    for i in range(0, periods):
        denominator = denominator + pow(alphaCalc, i)
        if isDataFrame is True:
            nominator = nominator + pow(alphaCalc, i) * samples.loc[i + today]["Zamkniecie"]
        else:
            nominator = nominator + pow(alphaCalc, i) * samples[i + today]
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
    # filename = input('Input file name to process it: ')
    filename = 'CD projekt'
    path = path + filename
    path = path + '.csv'
    samples = pd.read_csv(path, usecols=['Zamkniecie', 'Data'], nrows=1035)
    #samples = pd.read_csv(path)
    #samples[::-1].to_csv("Quotes/CD projekt.csv")
    return samples


def output(MACDsamples, SIGNALsamples, samples):
    matplotlib.use("TkAgg")
    plt.style.use('ggplot')
    x = []
    for i in range(0, 1000):
        splittedDate = str(samples.loc[i]['Data']).split('-')
        date = datetime(int(splittedDate[0]), int(splittedDate[1]), int(splittedDate[2]))
        x.append(date)
    # x = [i for i in range(0, 1000)]
    for i in range(0, 9):
        MACDsamples.pop()
    plt.plot(x, MACDsamples, linewidth=2.0)
    plt.plot(x, SIGNALsamples, linewidth=2.0)
    plt.title("wykres wskaźnika MACD/SIGNAL")
    plt.xlabel("dni próbek")
    plt.ylabel("wartości wskaźnika")
    plt.legend(["MACD", "SIGNAL"])
    plt.tight_layout()
    plt.show()
    samplesArray = []
    for i in range(0, 1000):
        samplesArray.append(samples.loc[i]["Zamkniecie"])
    plt.plot(x, samplesArray, linewidth=2.0)
    plt.xlabel("dni próbek")
    plt.ylabel("wartości zamknięcia")
    plt.legend(["Dane"])
    plt.title("wykres danych akcji firmy CD project")
    plt.tight_layout()
    plt.show()


def main():
    samples = CSVinput()
    MACDsamples = []
    SIGNALsamples = []
    for i in range(0, 1009):
        MACDsamples.insert(i, MACD(samples, i))
    for i in range(0, 1000):
        SIGNALsamples.insert(i, SIGNAL(MACDsamples, i))
    output(MACDsamples, SIGNALsamples, samples)


if __name__ == '__main__':
    main()
