#!/usr/bin/python
# -*- coding: utf-8 -*-


import numpy
import gym

import scipy.misc as smp
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)


def draw(pixels):
    smp.toimage(pixels).show()

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)

class CNN(object):
    def __init__(self, x):
        self.x_image = tf.reshape(x, [-1, 80, 80, 3])
        self.W_conv1 = weight_variable([5, 5, 3, 32])
        self.b_conv1 = bias_variable([32])
        self.h_conv1 = tf.nn.relu(conv2d(self.x_image, self.W_conv1) + self.b_conv1)
        self.h_pool1 = max_pool_2x2(self.h_conv1)
        self.W_conv2 = weight_variable([5, 5, 32, 64])
        self.b_conv2 = bias_variable([64])
        self.h_conv2 = tf.nn.relu(conv2d(self.h_pool1, self.W_conv2) + self.b_conv2)
        self.h_pool2 = max_pool_2x2(self.h_conv2)
        self.W_fc1 = weight_variable([20*20*64, 1024])
        self.b_fc1 = bias_variable([1024])
        self.h_pool2_flat = tf.reshape(self.h_pool2, [-1, 20*20*64])
        self.h_fc1 = tf.nn.relu(tf.matmul(self.h_pool2_flat, self.W_fc1) + self.b_fc1)
        self.W_fc2 = weight_variable([1024, 7])
        self.b_fc2 = bias_variable([7])
        self.y_conv = tf.matmul(self.h_fc1, self.W_fc2) + self.b_fc2

    def save_vb(self):
        vb = {}
        vb['W_conv1'] = self.W_conv1
        vb['b_conv1'] = self.b_conv1
        vb['W_conv2'] = self.W_conv2 
        vb['b_conv2'] = self.b_conv2
        vb['W_fc1'] = self.W_fc1
        vb['b_fc1'] = self.b_fc1
        vb['W_fc2'] = self.W_fc2
        vb['b_fc2'] = self.b_fc2
        return vb

    def copy_op(self, other):
        op = []
        op.append(tf.assign(self.W_conv1, other.W_conv1))
        op.append(tf.assign(self.b_conv1, other.b_conv1))
        op.append(tf.assign(self.W_conv2, other.W_conv2))
        op.append(tf.assign(self.b_conv2, other.b_conv2))
        op.append(tf.assign(self.W_fc1, other.W_fc1))
        op.append(tf.assign(self.b_fc1, other.b_fc1))
        op.append(tf.assign(self.W_fc2, other.W_fc2))
        op.append(tf.assign(self.b_fc2, other.b_fc2))
        return op

def choice(items, rate):
    return numpy.random.choice(items, 1, p=[rate, 1. - rate])[0] == items[0]

def compress(img):
    return smp.imresize(numpy.array(img)[50:,:,:], (80, 80)) / numpy.float32(1)

def main(unused_argv):
    import scipy.misc as smp

    env = gym.make('Assault-v0')

    x = tf.placeholder(tf.float32, [None, 80, 80, 3])
    y = tf.placeholder(tf.float32, [None, 1])
    a = tf.placeholder(tf.float32, [None, 7])
    Q = CNN(x)

    x_ = tf.placeholder(tf.float32, [None, 80, 80, 3])
    y_ = tf.placeholder(tf.float32, [None, 1])
    a_ = tf.placeholder(tf.float32, [None, 7])
    Q_= CNN(x_)

    Q_predict = tf.argmax(Q.y_conv, axis=0)
    Q_max_predict = tf.reduce_max(Q_.y_conv, axis=0)
    cost = tf.reduce_sum(tf.square(tf.reduce_sum(Q.y_conv * a, axis=0) - y))
    train_op = tf.train.RMSPropOptimizer(0.001, momentum=0.95).minimize(cost)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        sess.run(Q_.copy_op(Q))

        gama = 0.99

        D = [None] * 10000  # D = [None for i in xrange(10000)]
        D_n, D_size = 0, 0
        C = 0

        M, T = 20000, 1000
        for episode in xrange(M):
            print "episode : %s" % episode
            s = compress(env.reset())
            rate = 1.
            for t in xrange(T):
                action = None
                if D_size < 10000 or choice(('r', 'n'), rate):
                    action = env.action_space.sample()
                else:
                    action = Q_predict.eval(feed_dict={x: [s]})[0]

                x_n, r, done, info = env.step(action)
                if done:
                    r = -100.
                s_n = compress(x_n)

                D[D_n] = (s, action, float(r), s_n, done)
                D_n += 1
                if D_n >= 10000:
                    D_n = 0

                if D_size >= 10000:
                    print D_n
                    xx, yy, aa = [], [], []
                    mini_batch = numpy.random.choice(len(D), 32, replace=False)
                    for i in mini_batch:
                        r_y = 0.
                        if D[i][4]:
                            r_y = D[i][2]
                        else:
                            r_y = D[i][2] + gama * Q_max_predict.eval(feed_dict={x_: [D[i][3]]})[0]
                        yy.append([r_y])
                        xx.append(D[i][0])
                        aa.append([0.] * 7)
                        aa[-1][D[i][1]] = 1

                    train_op.run(feed_dict={x: xx, y: yy, a: aa})

                    if C >= 100:
                        print "C: %s" % C
                        sess.run(Q_.copy_op(Q))
                        C = 0
                        saver = tf.train.Saver(Q_.save_vb())
                        save_path = saver.save(sess, "/tmp/cnn_q_model/a")

                    rate -= 9.1e-07
                    C += 1
                else:
                    D_size += 1

                s = s_n
                if done:
                    break


if __name__ == '__main__':
    tf.app.run()
