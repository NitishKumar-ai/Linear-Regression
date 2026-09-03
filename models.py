import numpy as np

class linear_model:
    def __init__(self, W_size, lr, init="random"):
        """W_size = number of features (including thge bisas 1). lr = step size. """
        self.lr = lr
        if init == "random":
            self.W = np.zeros((W_size, 1))
        elif init == "zeros":
            self.W = np.zeros(W_size, 1)
        else:
            raise ValueError("init must be randon or zeros")
        self.LIST_W = np.zeros(W_size, 0)

    def forword(slef, feat)