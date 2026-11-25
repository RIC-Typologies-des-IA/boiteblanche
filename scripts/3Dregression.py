import numpy as np
import matplotlib.pyplot as plt

x = np.linspace(0, 1, 200)          # ensoleillement
premium = np.zeros_like(x)          # quartier ordinaire
premium_plus = np.ones_like(x)      # quartier premium

# Effet linéaire + interaction "premium x ensoleillement"
prix_ordonnaire = 100 + 20 * x
prix_premium = 120 + 35 * x + 15 * np.maximum(x - 0.5, 0)

plt.figure(figsize=(8, 5))
plt.plot(x, prix_ordonnaire, label="Quartier ordinaire")
plt.plot(x, prix_premium, label="Quartier premium")
plt.axvline(0.5, color="gray", linestyle="--", label="Seuil de surcote")
plt.xlabel("Ensoleillement")
plt.ylabel("Prix")
plt.title("Interaction : premium + ensoleillement")
plt.legend()
plt.grid(True)
plt.show()
