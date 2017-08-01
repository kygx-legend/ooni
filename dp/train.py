#!/usr/bin/python
# -*- coding: utf-8 -*-


import numpy
import gym

import scipy.misc as smp
import tensorflow as tf

import os
import cv2

from gym.envs.registration import register

os.environ["CUDA_VISIBLE_DEVICES"] = "5"

# tf.logging.set_verbosity(tf.logging.INFO)

register(
    id='Assault-v99',
    entry_point='gym.envs.atari:AtariEnv',
    kwargs={'game': 'assault', 'obs_type': 'image', 'frameskip': 1, 'repeat_action_probability': 0},
    max_episode_steps=1000000,
    nondeterministic=False,
)

def rgb2gray(rgb):
    return numpy.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def draw(pixels):
    smp.toimage(pixels).show()

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='VALID')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')

def weight_variable(shape, name):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial, name=name)

def bias_variable(shape, name):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial, name=name)

class CNN(object):
    def __init__(self, x):
        self.x_image = tf.transpose(x, [0, 2, 3, 1]) # NCWH -> NWHC
        self.W_conv1 = weight_variable([5, 5, 4, 32], name='W_conv1')
        self.b_conv1 = bias_variable([32], name='b_conv1')
        self.h_conv1 = tf.nn.relu(conv2d(self.x_image, self.W_conv1) + self.b_conv1)
        self.h_pool1 = max_pool_2x2(self.h_conv1)
        self.W_conv2 = weight_variable([5, 5, 32, 64], name='W_conv2')
        self.b_conv2 = bias_variable([64], name='b_conv2')
        self.h_conv2 = tf.nn.relu(conv2d(self.h_pool1, self.W_conv2) + self.b_conv2)
        self.h_pool2 = max_pool_2x2(self.h_conv2)
        self.W_fc1 = weight_variable([17*17*64, 1024], name='W_fc1')
        self.b_fc1 = bias_variable([1024], name='b_fc1')
        self.h_pool2_flat = tf.reshape(self.h_pool2, [-1, 17*17*64])
        self.h_fc1 = tf.nn.relu(tf.matmul(self.h_pool2_flat, self.W_fc1) + self.b_fc1)
        self.keep_prob = 1.0
        self.h_fc1_drop = tf.nn.dropout(self.h_fc1, self.keep_prob)
        self.W_fc2 = weight_variable([1024, 7], name='W_fc2')
        self.b_fc2 = bias_variable([7], name='b_fc2')
        self.y_conv = tf.matmul(self.h_fc1_drop, self.W_fc2) + self.b_fc2

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
        """vb = [
            self.W_conv1,
            self.b_conv1,
            self.W_conv2,
            self.b_conv2,
            self.W_fc1,
            self.b_fc1,
            self.W_fc2,
            self.b_fc2
        ]"""
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
    img = rgb2gray(img[50:,:,:] / numpy.float32(255))
    return cv2.resize(img, (80, 80))

def main(unused_argv):
    import scipy.misc as smp

    env = gym.make('Assault-v99')

    x = tf.placeholder(tf.float32, [None, 4, 80, 80])
    y = tf.placeholder(tf.float32, [None, 1])
    a = tf.placeholder(tf.float32, [None, 7])
    Q = CNN(x)

    x_ = tf.placeholder(tf.float32, [None, 4, 80, 80])
    y_ = tf.placeholder(tf.float32, [None, 1])
    a_ = tf.placeholder(tf.float32, [None, 7])
    Q_= CNN(x_)

    Q_predict = tf.argmax(Q.y_conv, axis=1)
    Q_max_predict = tf.reduce_max(Q_.y_conv, axis=1)
    diff = tf.reduce_sum(Q.y_conv * a, axis=1, keep_dims=True) - y
    huber_loss = tf.where(tf.abs(diff) < 0.5, tf.square(diff), tf.abs(diff))
    cost = tf.reduce_sum(huber_loss)
    train_op = tf.train.RMSPropOptimizer(0.00025, momentum=0.95).minimize(cost)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        sess.run(Q_.copy_op(Q))

        summ_writer = tf.summary.FileWriter('./graph', graph = sess.graph)
        summ_writer.close()

        gama = 0.99

        expr_replay_mem_size = 100000
        D = [None] * expr_replay_mem_size  # D = [None for i in xrange(10000)]
        D_n, D_size = 0, 0
        C = 0

        M, T = 20000, 1000
        for episode in xrange(M):
            s = [compress(env.reset())] * 4
            rate = 1.
            sum_reward = 0
            action = None
            k = 0
            lives = 4
            while 1:
                if D_size < expr_replay_mem_size:
                    action = env.action_space.sample()
                else:
                    if k == 0:
                        if D_size < expr_replay_mem_size or choice(('r', 'n'), rate):
                            action = env.action_space.sample()
                        else:
                            action = Q_predict.eval(feed_dict={x: [s]})[0]
                        k = 3
                    else:
                        k -= 1

                x_n, r, done, info = env.step(action)
                sum_reward += r
                # env.render()
                if r > 0:
                    r = 1.
                if info["ale.lives"] != lives:
                    lives = info["ale.lives"]
                    r = -0.5
                if done:
                    r = -1.
                s_n = (s + [compress(x_n)])[1:]

                D[D_n] = (s, action, float(r), s_n, done)
                D_n += 1
                if D_n >= expr_replay_mem_size:
                    D_n = 0

                if D_size >= expr_replay_mem_size:
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

                    if C >= 1000:
                        print "C: %s, reward: %s, rate: %s" % (C, sum_reward, rate)
                        sess.run(Q_.copy_op(Q))
                        C = 0
                        saver = tf.train.Saver(Q_.save_vb())
                        save_path = saver.save(sess, "./a")

                    rate -= 9.1e-07
                    C += 1
                else:
                    D_size += 1

                s = s_n
                if done:
                    print "episode : %s, reward : %s" % (episode, sum_reward)
                    break


if __name__ == '__main__':
    tf.app.run()
