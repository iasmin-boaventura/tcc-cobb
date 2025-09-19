import torch.nn as nn

class AngleCNN(nn.Module):
    def __init__(self):
        """
        CNN simples para estimativa de ângulo de vértebra.
        Entrada: imagem grayscale (1 canal)
        Saída: valor do ângulo (1 float)
        """
        super(AngleCNN, self).__init__()

        # Camadas convolucionais e pooling
        self.conv = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1),  # 1 canal de entrada → 32 filtros
            nn.ReLU(),
            nn.MaxPool2d(2),  # reduz resolução pela metade

            nn.Conv2d(32, 64, 3, padding=1), # 32 → 64 filtros
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        # Camadas totalmente conectadas
        self.fc = nn.Sequential(
            nn.Linear(64*16*16, 128), # flatten e primeira FC
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1) # saída: valor do ângulo
        )

    def forward(self, x):
        x = self.conv(x)
        x = x.view(x.size(0), -1)  # flatten
        x = self.fc(x)
        return x