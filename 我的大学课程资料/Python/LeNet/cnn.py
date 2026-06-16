import torch

def corr2d(x, kernel):
    batch_size, in_channels, height, width = x.shape
    out_channels, _, kernel_height, kernel_width = kernel.shape
    
    output_height = height - kernel_height + 1
    output_width = width - kernel_width + 1
    
    output = torch.zeros(batch_size, out_channels, output_height, output_width)
    
    for b in range(batch_size):
        for oc in range(out_channels):
            for i in range(output_height):
                for j in range(output_width):
                    output[b, oc, i, j] = (x[b, :, i:i+kernel_height, j:j+kernel_width] * 
                                         kernel[oc, :, :, :]).sum()
    
    return output

def max_pool2d(x, kernel_size, stride=None):
    if stride is None:
        stride = kernel_size
        
    batch_size, channels, height, width = x.shape
    out_height = (height - kernel_size) // stride + 1
    out_width = (width - kernel_size) // stride + 1
    
    output = torch.zeros(batch_size, channels, out_height, out_width)
    
    for b in range(batch_size):
        for c in range(channels):
            for i in range(out_height):
                for j in range(out_width):
                    h_start = i * stride
                    h_end = h_start + kernel_size
                    w_start = j * stride
                    w_end = w_start + kernel_size
                    output[b, c, i, j] = torch.max(x[b, c, h_start:h_end, w_start:w_end])
    
    return output

class Conv2D:
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, padding=0):
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        
        scale = torch.sqrt(torch.tensor(2.0 / (in_channels * kernel_size * kernel_size)))
        self.weights = torch.randn(out_channels, in_channels, kernel_size, kernel_size) * scale
        self.bias = torch.zeros(out_channels)
        
        self.weights.requires_grad = True
        self.bias.requires_grad = True

    def forward(self, x):
        return corr2d(x, self.weights) + self.bias

    def parameters(self):
        return [self.weights, self.bias]

class MaxPool2D:
    def __init__(self, kernel_size, stride=None):
        self.kernel_size = kernel_size
        self.stride = stride if stride is not None else kernel_size

    def forward(self, x):
        return max_pool2d(x, self.kernel_size, self.stride)

class Linear:
    def __init__(self, in_features, out_features):
        scale = torch.sqrt(torch.tensor(2.0 / (in_features + out_features)))
        self.weights = torch.randn(in_features, out_features) * scale
        self.bias = torch.zeros(out_features)
        
        self.weights.requires_grad = True
        self.bias.requires_grad = True

    def forward(self, x):
        return torch.matmul(x, self.weights) + self.bias

    def parameters(self):
        return [self.weights, self.bias]
    
def relu(x):
    return torch.maximum(torch.tensor(0), x)

def softmax(x):
    return torch.exp(x) / torch.sum(torch.exp(x), dim=1, keepdim=True)

class CNN:
    def __init__(self):
        self.conv1 = Conv2D(in_channels=1, out_channels=6, kernel_size=5)
        self.pool1 = MaxPool2D(kernel_size=2, stride=2)
        self.conv2 = Conv2D(in_channels=6, out_channels=16, kernel_size=5)
        self.pool2 = MaxPool2D(kernel_size=2, stride=2)
        self.conv3 = Conv2D(in_channels=16, out_channels=120, kernel_size=5)
        self.fc1 = Linear(120, 84)
        self.fc2 = Linear(84, 10)
        self.training = True

    def __call__(self, x):
        return self.forward(x)

    def forward(self, x):     
        if len(x.shape) == 3:
            x = x.unsqueeze(0)

        x = self.conv1.forward(x)
        x = relu(x)
        x = self.pool1.forward(x)

        x = self.conv2.forward(x)
        x = relu(x)
        x = self.pool2.forward(x)

        x = self.conv3.forward(x)
        x = relu(x)

        x = x.reshape(x.shape[0], -1)
        
        x = self.fc1.forward(x)
        x = relu(x)
        x = self.fc2.forward(x)

        return softmax(x)

    def parameters(self):
        params = []
        params.extend(self.conv1.parameters())
        params.extend(self.conv2.parameters())
        params.extend(self.conv3.parameters())
        params.extend(self.fc1.parameters())
        params.extend(self.fc2.parameters())
        return params
    
    def train(self, mode=True):
        self.training = mode
        return self
    
    def eval(self):
        return self.train(False)

