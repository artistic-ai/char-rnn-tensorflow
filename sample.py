from __future__ import print_function
import tensorflow as tf

import argparse
import os
from six.moves import cPickle

from model import Model
from utils import StructFromArgs

from six import text_type


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str, default='save',
                        help='model directory to store checkpointed models')
    parser.add_argument('-n', type=int, default=2000,
                        help='number of characters to sample')
    parser.add_argument('--prime', type=text_type, default=u' ',
                        help='prime text')
    parser.add_argument('--sample', type=int, default=1,
                        help='0 to use max at each timestep, 1 to sample at each timestep, 2 to sample on spaces')

    args = parser.parse_args()
    print(sample(**vars(args)))


def load_model(save_dir='save'):
    with open(os.path.join(save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    model = Model(saved_args, True)
    with open(os.path.join(save_dir, 'chars_vocab.pkl'), 'rb') as f:
        chars, vocab = cPickle.load(f)
    return {'model': model, 'chars': chars, 'vocab': vocab}


def restore_session(save_dir='save'):
    sess = tf.Session()
    tf.global_variables_initializer().run()
    saver = tf.train.Saver(tf.global_variables())
    ckpt = tf.train.get_checkpoint_state(save_dir)
    if ckpt and ckpt.model_checkpoint_path:
        saver.restore(sess, ckpt.model_checkpoint_path)
        return sess


def get_sample(model, sess, n=2000, prime=u' ', sample_type=1):
    return model['model'].sample(sess, model['chars'], model['vocab'], n, prime, sample_type)


def sample(save_dir='save', n=2000, prime=u' ', sample_type=1):
    model = load_model(save_dir)
    sess = restore_session(save_dir)
    with sess:
        return get_sample(model, sess, n, prime, sample_type)


if __name__ == '__main__':
    main()
