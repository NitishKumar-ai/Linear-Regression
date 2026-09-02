import numpy as np

class linear_model:
    '''
    Linear mode class is used to creat thre regression model used in the assiment.
    It has three data elemets:
    w: stores the weight for the linear regression(plus one term for bias , using the bias trick)
    lr: learning rate for the gradient desecnet update equation
    LIST_W: stores the weight vector after each update (used later to show how weights change after each epoch)

    It has three function:
    forword(): it calculate the perdicted wright of the model for given inputs points
    backword(): it perfrom the weghts update descnet
    loass(): it compute the eculidean loss beween the perdicted value and the actual values to the input data points
    '''

def __init__(self, W_size, lr , init='random'):
    '''
    initilizees an object of the linear model class.

    INPUT:

    '''
    self.lr = lr
    if init == "random": # initlise the weight matrix with random values
        self.W =np.random((W_size, 1))
    elif init == 'zeros': # intilise the the weight matrix with zero values
        self.W = np.zeros(W_size, 0)
    else:
        raise Exception
    self.LIST_W = np.zeros(W_size, 0)