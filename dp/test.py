#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import gym

import scipy.misc as smp
import tensorflow as tf
import cv2
import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""

tf.logging.set_verbosity(tf.logging.INFO)

def draw(pixels):
    smp.toimage(pixels).show()

def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

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
        self.W_fc1 = weight_variable([20*20*64, 1024], name='W_fc1')
        self.b_fc1 = bias_variable([1024], name='b_fc1')
        self.h_pool2_flat = tf.reshape(self.h_pool2, [-1, 20*20*64])
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
        return vb

def rgb2gray(rgb):
    return numpy.dot(rgb[...,:3], [0.299, 0.587, 0.114])

def compress(img):
    img = rgb2gray(img[50:,:,:] / numpy.float32(255))
    return cv2.resize(img, (80, 80))

def main(unused_argv):
    import scipy.misc as smp

    env = gym.make('Assault-v0')

    x = tf.placeholder(tf.float32, [None, 4, 80, 80])
    Q = CNN(x)
    Q_predict = tf.argmax(Q.y_conv, axis=1)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver(Q.save_vb())
        saver.restore(sess, "./a")

        M, T = 20, 100
        for episode in xrange(M):
            observation = env.reset()
            # for t in xrange(T):
            sr = 0
            t = 0
            s = [compress(observation)] * 4
            while 1:
                # env.render()
                action = Q_predict.eval(feed_dict={x: [s]})[0]
                observation, reward, done, info = env.step(action)
                s = (s + [compress(observation)])[1:]
                sr += reward
                t += 1
                if done:
                    print("Episode finished after {} timesteps with reward {}".format(t+1, sr))
                    break


if __name__ == '__main__':
    tf.app.run()
