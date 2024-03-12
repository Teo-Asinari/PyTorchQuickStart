import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

def main():
    training_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=ToTensor(),
    )

    test_data = datasets.FashionMNIST(
        root="data",
        train=False,
        download=True,
        transform=ToTensor()
    )

    batch_size = 64

    train_dataloader = DataLoader(training_data, batch_size=batch_size)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)

    for X, y in test_dataloader:
        print(f"Shape of X [N, C, H, W]: {X.shape}")
        print(f"Shape of y: {y.shape} {y.dtype}")
        break

    device = ("cuda" if torch.cuda.is_available()
              else "mps" if torch.backends.mps.is_available()
              else "cpu")

    print(f"Using {device} device")

    # FROM THE TUTORIAL:
    #To define a neural network in PyTorch, we create a class that inherits
    # from nn.Module. We define the layers of the network in the __init__
    # function and specify how data will pass through the network in the forward
    # function. To accelerate operations in the neural network, we move it to
    # the GPU or MPS if available.

    class NeuralNetwork(nn.Module):
        def __init__(self):
            super().__init__()
            self.flatten = nn.Flatten()
            self.linear_relu_stack = nn.Sequential(
                nn.Linear(28*28, 512),
                nn.ReLU(),
                nn.Linear(512, 512),
                nn.ReLU(),
                nn.Linear(512, 10)
            )

        def forward(self, x):
            x = self.flatten(x)
            return  self.linear_relu_stack(x)

    model = NeuralNetwork().to(device)
    print(model)


    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

    def train(dataloader, model, loss_fn, optimizer):
        size = len(dataloader.dataset)
        model.train()

        for batch, (X, y) in enumerate(dataloader):
            X, y = X.to(device), y.to(device)

            prediction = model(X)
            loss = loss_fn(prediction, y)

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            if batch % 100 == 0:
                loss, current = loss.item(), (batch + 1) * len(X)
                print(f"loss: {loss:>7f} [{current:>5d}/{size:>5d}]")

    def test(dataloader, model, loss_fn):
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        model.eval()
        test_loss, correct = 0, 0
        with torch.no_grad():
            for X, y in dataloader:
                X, y = X.to(device), y.to(device)
                prediction = model(X)
                test_loss += loss_fn(prediction, y).item()
                correct += (prediction.argmax(1) == y).type(torch.float).sum().item()
            test_loss /= num_batches
            correct /= size
            print(f"Test Error: \n Accuracy: {(100*correct) :>0.1f}%, Avg loss: {test_loss:>8f} \n")

    epochs = 5
    for t in range(epochs):
        print(f"Epoch {t+1}\n-------------------")
        train(train_dataloader, model, loss_fn, optimizer)
        test(test_dataloader, model, loss_fn)
    print("Done!")

    torch.save(model.state_dict(), "model.pth")
    print("Saved the pytorch model to the file model.pth")

    model = NeuralNetwork.to(device)
    model.load_state_dict(torch.load("model.pth"))

    classes = [
        "T-shirt/top",
        "Trouser",
        "Pullover",
        "Dress",
        "Coat",
        "Sandal",
        "Shirt",
        "Sneaker",
        "Bag",
        "Ankle boot"
    ]

    model.eval()
    x, y = test_data[0][0], test_data[0][1]
    with torch.no_grad():
        x = x.to(device)
        prediction = model(x)
        predicted, actual = classes[prediction[0].argmax(0)], classes[y]
        print(f'Predicted: "{predicted}" Actual: "{actual}"')

# TODO
# Explain/learn meaning of the following statements/snippets:
# .to(device)
# with torch.no_grad()
# how did it determine I had a CUDA gpu?
# what is mps?
if __name__ == "__main__":
    main()