#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy
import gym

import scipy.misc as smp
import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)

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
        self.x_image = tf.reshape(x, [-1, 80, 80, 3])
        self.W_conv1 = weight_variable([5, 5, 3, 32], name='W_conv1')
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

def compress(img):
    return smp.imresize(numpy.array(img)[50:,:,:], (80, 80)) / numpy.float32(1)

def main(unused_argv):
    import scipy.misc as smp

    env = gym.make('Assault-v0')

    x = tf.placeholder(tf.float32, [None, 80, 80, 3])
    Q = CNN(x)
    Q_predict = tf.argmax(Q.y_conv, axis=0)

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess, "/tmp/cnn_q_model/a")

        M, T = 20, 100
        for episode in xrange(M):
            observation = env.reset()
            for t in xrange(T):
                env.render()
                s = compress(observation)
                action = Q_predict.eval(feed_dict={x: [s]})[0]
                observation, reward, done, info = env.step(action)
                if done:
                    print("Episode finished after {} timesteps with reward {}".format(t+1, reward))
                    break


if __name__ == '__main__':
    tf.app.run()
