#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

np.set_printoptions(precision=4)

train_data_name = './dataset/winequality-white.csv'

feature_num = 11
enable_test = True
quadratic = True

def read_data():
    train_set = np.genfromtxt(train_data_name, comments='#', delimiter=';')
    return (train_set, train_set)

def linear_regression(t, x, y, test_set, ma):
    a = 0.1
    l = 10
    m = len(x)
    iter_num = 200
    for _ in xrange(iter_num):
        t = (1. - a * l / m) * t - a / m * np.dot(x.transpose(), np.dot(x, t) - y)
        if enable_test and _ % 5 == 0:
            print "round %s" % _
            test_linear_regression(t, test_set[:, :-1], test_set[:, -1], ma)

def test_linear_regression(t, x, y, ma):
    x = x / ma
    if quadratic:
        x = np.append(x, x * x, axis=1)

    p = np.dot(x, t)
    for _ in xrange(10):
        print p[_], y[_]
    p = np.sum(p - y)
    print p * p

def train(x, y, test_set):
    ma = np.max(x, axis=0)
    x = x / ma

    t = np.random.randn(feature_num)
    if quadratic:
        x = np.append(x, x * x, axis=1)
        t = np.random.randn(feature_num * 2)
    
    linear_regression(t, x, y, test_set, ma)

def main():
    train_set, test_set = read_data()

    train(train_set[:, :-1], train_set[:, -1], test_set)

if __name__ == '__main__':
    main()
