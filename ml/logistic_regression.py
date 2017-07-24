#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

np.set_printoptions(precision=4)

train_data_name = './dataset/datatraining.txt'
test_data_name = './dataset/datatest.txt'

feature_num = 5
enable_test = True
quadratic = True

def read_data():
    train_set = np.genfromtxt(train_data_name, comments='#', delimiter=',')
    test_set = np.genfromtxt(test_data_name, comments='#', delimiter=',')
    return (train_set[:, 2:], test_set[:, 2:])

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

def logistic_regression(t, x, y, test_set, ma):
    a = 0.001
    m = len(x)
    iter_num = 200
    for _ in xrange(iter_num):
        t = t - a / m * np.dot(x.transpose(), sigmoid(np.dot(x, t)) - y)
        if enable_test and _ % 5 == 0:
            print "round %s" % _
            test_logistic_regression(t, test_set[:, :-1], test_set[:, -1], ma)

def test_logistic_regression(t, x, y, ma):
    x = x / ma
    if quadratic:
        x = np.append(x, x * x, axis=1)

    p = sigmoid(np.dot(x, t))
    for _ in xrange(10):
        if p[_] >= 0.5:
            print 1.0, y[_]
        else:
            print 0.0, y[_]

    a = np.log(sigmoid(p))
    b = np.log(sigmoid(1.0 - p))
    print -np.sum(np.dot(y.transpose(), a) + np.dot((1.0 - y).transpose(), b))

def train(x, y, test_set):
    ma = np.max(x, axis=0)
    x = x / ma

    t = np.random.randn(feature_num)
    if quadratic:
        x = np.append(x, x * x, axis=1)
        t = np.random.randn(feature_num * 2)
    
    logistic_regression(t, x, y, test_set, ma)

def main():
    train_set, test_set = read_data()

    train(train_set[:, :-1], train_set[:, -1], test_set)

if __name__ == '__main__':
    main()
