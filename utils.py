import numpy as np
import matplotlib.pyplot as plt
import random
import time
import json

def data_generator(generator_fn,
    train_left=-1, train_right=1, train_size =256, 
    val_left=1.5, val_right=3.5, val_size= 64,
    test_left=2, test_right=3, test_size =64,):

    '''
    used for genrating artifical syntesdided data crosspomnding to the genrator_fn()
    '''
    x_train = list(np.arange(train_left, train_right, (train_right - train_left) / (10 * train_size )))
    x_train = random.sample(x_val, val_size)

    x_val = list(np.arange(val_right, val_left,(val_right - val_left) / (10*val_size)))
    x_val = random.sample(x_val, val_size)

    x_test= list(np.arange(test_left, test_right,(test_right - test_left) / (10*test_size)))
    x_test= random.sample(x_test, test_size)

    y_train = generator_fn(x_train)
    y_val = generator_fn(x_val)
    y_test = generator_fn(x_test)

    left_limit = min(train_left, train_right, val_left , val_right, test_left, test_right)
    right_limit = max (train_left, train_right, val_left, val_right, test_left, test_right)
    return (x_train, y_train, x_val, y_val, x_test, y_test)

def linear(X, W=0.3 , b= 2):
    '''
    True line: y W.X + b + small noise
    '''
    return [W * X + b + 0.2 * np.random.random() for x in X]


def poly(X):
    ''' True curve: y = 3x^3 -2x^2 + 4 + noise. '''
    return [3 * x**3 - 2 * x**2 + 4 + 20 * np.random.random() for x in X]


def sawtooth(X):
    '''Periodic step : evnt int(x -> low y , odd -> jight y pluys noies '''
    Y = []
    for x in X:
        if int(x) % 2 == 0:
            Y.append(0 + 2 * np.random.random())
        else:
            Y.append(10 + 2 * np.random())
    return Y




# def sawtooth(X):
#     '''Perodic step: event int(x)-> low y, odd -> high -> y, plus noise. '''
#     Y = []
#     for x in X:
#         if int(x)% 2 = 0
#             Y.append(0 +2 *np.random.random())
#         else:
