import cv2
import torch
from torch import nn
import numpy as np

class CharCNNClassifier(nn.Module):
    def __init__(self):
        super(CharCNNClassifier, self).__init__()
        
        # Сверточные слои
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1)
        
        # Максимальный пулинг
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Полносвязные слои
        self.fc1 = nn.Linear(32 * 10 * 10, 64)  # После пулинга размер изображения уменьшается
        self.fc2 = nn.Linear(64, 8)  # Выходной вектор длины 3
        
        # Функция активации
        self.relu = nn.ReLU()
    
    def forward(self, x):
        # Применяем свертки и пулинг
        x = self.pool(self.relu(self.conv1(x)))  # Размер: (batch_size, 16, 20, 20) <- размер уменьшился в 2 раза
        x = self.pool(self.relu(self.conv2(x)))  # Размер: (batch_size, 32, 10, 10) <- размер уменьшился в 2 раза
        
        # Выравниваем тензор для полносвязного слоя
        x = x.view(x.size(0), -1)  # Размер: (batch_size, 32 * 10 * 10)
        
        # Применяем полносвязные слои
        x = self.relu(self.fc1(x))  # Размер: (batch_size, 128)
        x = self.fc2(x)  # Размер: (batch_size, 8)
        
        return x

def get_model(path):
    model = CharCNNClassifier()
    model.load_state_dict(torch.load(path))
    return model

def resize_image_height40(image):
    """
    Сжимает изображение по высоте, сохраняя пропорции.

    :param image: Изображение в формате NumPy (40 x W x C).
    :return: Сжатое изображение.
    """
    HEIGHT = 40
    # Получаем текущие размеры изображения
    (original_height, original_width) = image.shape[:2]

    # Вычисляем новую ширину, сохраняя пропорции
    aspect_ratio = original_width / original_height
    new_width = int(HEIGHT * aspect_ratio)

    # Масштабируем изображение
    resized_image = cv2.resize(image, (new_width, HEIGHT), interpolation=cv2.INTER_AREA)

    return resized_image

def classifier_image_word(model, image_word):
    resize_image = resize_image_height40(image_word)
    chars = np.array([[resize_image[:, i*40:(i+1)*40]] for i in range(resize_image.shape[1]//40)])
    if len(chars) == 0:
        return torch.Tensor([0.0 for _ in range(8)])

    data = torch.Tensor(chars)
    rez = model(data)
    return torch.mean(rez, 0)

def interpretation_class(class_):
    print("Нет информации")