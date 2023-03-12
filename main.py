from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib
from shapely.geometry import LineString
import numpy as np

SAMPLES_NUMBER = 1000
ALL_SAMPLES_NUMBER = SAMPLES_NUMBER + 35
MACD_SAMPLES_NUMBER = SAMPLES_NUMBER + 9


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
    filename = input('Input file name to process it: ')
    path = path + filename
    path = path + '.csv'
    samples = pd.read_csv(path, usecols=['Zamkniecie', 'Data', 'Najwyzszy', 'Najnizszy', 'Wolumen'],
                          nrows=ALL_SAMPLES_NUMBER)
    return samples


def output(MACDsamples, SIGNALsamples, samples, MoneyFlowSamples):
    matplotlib.use("TkAgg")
    plt.style.use('ggplot')
    x = []
    for i in range(0, SAMPLES_NUMBER):
        splittedDate = str(samples.loc[i]['Data']).split('-')
        date = datetime(int(splittedDate[0]), int(splittedDate[1]), int(splittedDate[2]))
        x.append(date)
    x.reverse()
    plt.plot(x, MACDsamples, linewidth=1.0)
    plt.plot(x, SIGNALsamples, linewidth=1.0)
    plt.title("wykres wskaźnika MACD/SIGNAL")
    plt.xlabel("dni")
    plt.ylabel("wartości wskaźnika")
    plt.legend(["MACD", "SIGNAL"])
    plt.tight_layout()
    plt.show()
    samplesArray = []
    for i in range(0, SAMPLES_NUMBER):
        samplesArray.append(samples.loc[i]["Zamkniecie"])
    samplesArray.reverse()
    plt.plot(x, samplesArray, linewidth=1.0)
    plt.xlabel("dni")
    plt.ylabel("wartości ceny zamknięcia")
    plt.legend(["Dane"])
    plt.title("wykres danych akcji firmy CD project")
    plt.tight_layout()
    plt.show()
    plt.plot(x, MoneyFlowSamples, linewidth=1.0)
    plt.xlabel("dni")
    plt.ylabel("wartości wskaźnika")
    plt.legend(["Money Flow"])
    plt.title("wykres wskaźnika Money Flow")
    plt.tight_layout()
    plt.show()


def MoneyFlow(samples, today, periods):
    lastTypical = 0.0
    positiveMoneyFlow = 0.0
    negativeMoneyFlow = 0.0
    for i in range(0, periods):
        typical = (samples.loc[i + today]["Zamkniecie"] + samples.loc[i + today]["Najwyzszy"] + samples.loc[i + today][
            "Najnizszy"]) / 3
        moneyFlow = typical * samples.loc[i + today]["Wolumen"]
        if typical > lastTypical:
            positiveMoneyFlow = positiveMoneyFlow + moneyFlow
        else:
            negativeMoneyFlow = negativeMoneyFlow + moneyFlow
        lastTypical = typical
    moneyRatio = positiveMoneyFlow / negativeMoneyFlow
    mfi = 100 - (100 / (1+moneyRatio))
    return mfi


def simulation(MACDsamples, SIGNALsamples, samples, MoneyFlowSamples):
    samples = samples.loc[::-1]
    MACDsamples.reverse()
    SIGNALsamples.reverse()
    MoneyFlowSamples.reverse()
    x = np.arange(0, SAMPLES_NUMBER)
    first_line = LineString(np.column_stack((x, MACDsamples)))
    second_line = LineString(np.column_stack((x, SIGNALsamples)))
    intersection = first_line.intersection(second_line)
    xs = set()
    if intersection.geom_type == 'MultiPoint':
        xs = set(round(point.x) for point in intersection.geoms)
    elif intersection.geom_type == 'Point':
        xs.add(round(intersection.x))
    for i in range(SAMPLES_NUMBER):
        if MoneyFlowSamples[i] > 80 or MoneyFlowSamples[i] < 20:
            xs.add(i)
    xs = list(xs)
    xs.sort()
    capital = 1000.0
    actions = 0.0
    for i in xs:
        if MoneyFlowSamples[i] > 80:
            actions = actions + (capital / samples.loc[i]["Zamkniecie"])
            capital = 0.0
            continue
        if MoneyFlowSamples[i] < 20:
            capital = capital + (actions * samples.loc[i]["Zamkniecie"])
            actions = 0.0
            continue
        if (MACDsamples[i-1] < SIGNALsamples[i-1]) and (SIGNALsamples[i+1] < MACDsamples[i+1]):
            capital = capital + (actions * samples.loc[i]["Zamkniecie"])
            actions = 0.0
            continue
        if(MACDsamples[i - 1] > SIGNALsamples[i - 1]) and (SIGNALsamples[i+1] > MACDsamples[i+1]):
            actions = actions + (capital / samples.loc[i]["Zamkniecie"])
            capital = 0.0
    if actions != 0.0:
        capital = capital + actions * samples.loc[SAMPLES_NUMBER - 1]["Zamkniecie"]
    print(capital)


def main():
    samples = CSVinput()
    MACDsamples = []
    SIGNALsamples = []
    MoneyFlowSamples = []
    for i in range(0, MACD_SAMPLES_NUMBER):
        MACDsamples.insert(i, MACD(samples, i))
    for i in range(0, SAMPLES_NUMBER):
        SIGNALsamples.insert(i, SIGNAL(MACDsamples, i))
    for i in range(0, 9):
        MACDsamples.pop()
    for i in range(0, SAMPLES_NUMBER):
        MoneyFlowSamples.insert(i, MoneyFlow(samples, i, 14))
    simulation(MACDsamples, SIGNALsamples, samples, MoneyFlowSamples)
    output(MACDsamples, SIGNALsamples, samples, MoneyFlowSamples)


if __name__ == '__main__':
    main()
