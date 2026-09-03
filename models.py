import numpy as np

# np.float128 is missing on most Windows NumPy builds. float64 is portable.
DTYPE = np.float64


class linear_model:
    '''
    Linear model class is used to create the regression model that is used in the
    assignment.
    It has three data elements:
    W: Stores the weight vector for the linear regression (plus one term for bias, using the bias trick)
    lr: learning rate for the gradient descent update equation
    LIST_W: Stores the weight vector after each update (used later to show how weights change after each epoch)

    It has three functions:
    forward(): it calculates the predicted output by the model for given input points
    backward(): it performs the weight update by gradient descent
    loss(): it computes the Euclidean loss between the predicted and the actual values corresponding to the input data points
    '''

    def __init__(self, W_size, lr, init='random'):
        '''
        Initializes an object of the linear_model class.

        INPUT:
        -----
        W_size: an integer equal to the feature_size + 1 (for bias)
        lr: the learning rate to be used in weight update during gradient descent
        init: method for initialization of weight matrix
        '''
        self.lr = lr
        if init == 'random':
            self.W = np.random.random((W_size, 1))
        elif init == 'zeros':
            self.W = np.zeros((W_size, 1))
        else:
            raise Exception
        self.LIST_W = np.zeros((W_size, 0))

    def forward(self, feat):
        '''
        Predicted output for given feature matrix.

        feat: (n_points x n_features)
        y_pred: (n_points x 1)  =  feat @ W
        '''
        y_pred = np.matmul(feat, self.W)
        return y_pred

    def backward(self, y_actl, y_pred, feat):
        '''
        Gradient descent weight update. No return value.

        W <- W - (lr / n) * feat.T @ (y_pred - y_actl)
        Then append the new W onto LIST_W for plotting.
        '''
        loss_pred = np.array((y_pred - y_actl), dtype=DTYPE)
        self.W = self.W - ((self.lr) / (feat.shape[0])) * (np.matmul(np.transpose(feat), loss_pred))
        self.LIST_W = np.append(self.LIST_W, self.W, 1)

    def loss(self, y_actl, y_pred):
        '''
        Euclidean loss: mean of squared errors, divided by 2.
        Returns a scalar.
        '''
        A = np.array((y_pred - y_actl), dtype=DTYPE)
        A = A / (2 * A.shape[0])
        scalar_LOSS = sum(A * A)
        return scalar_LOSS


def calc_features(X, choice, param=5):
    '''
    Turn raw x into a feature matrix (with a bias column of 1s).

    choice: 'linear' | 'poly' | 'fourier' | 'your_own_features'
    param:  extra size (poly degree+1, number of Fourier pairs, etc.)
    '''
    feat = []
    for x in X:
        if choice == 'linear':
            b = np.array([[1]] * x.shape[0])
            a = (np.c_[x, b]).tolist()
            feat.append(a[0])

        elif choice == 'poly':
            b = [[0.5]] * x.shape[0]
            a = np.array(b)
            for i in range(param - 1):
                a = (np.c_[(x ** (i + 1)), a])
            for i in a:
                feat.append((i.tolist()))

        elif choice == 'fourier':
            b = [[1]] * x.shape[0]
            a = np.array(b)
            for i in range((param)):
                a = (np.c_[(np.sin(x * (i + 1))), a])
                a = (np.c_[(np.cos(x * (i + 1))), a])
            for i in a:
                feat.append((i.tolist()))

        elif choice == 'your_own_features':
            b = [[50]] * x.shape[0]
            a = np.array(b)
            c = x * x
            for i in range(param):
                b = (np.c_[(112 * np.sin(x * (i + 1))), b])
                b = (np.c_[(112 * np.cos(x * (i + 1))), b])
            a = (np.c_[c, b])
            for i in a:
                feat.append((i.tolist()))

    return np.array(feat, dtype=DTYPE)
