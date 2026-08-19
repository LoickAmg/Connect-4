# Puissance 4 (Connect Four)

Un Puissance 4 en Python/Pygame, axé sur la manipulation de grille et la logique de jeu : gravité des pions, détection de victoire (horizontale, verticale, diagonales), logique séparée du rendu (facile à tester unitairement), et une CI GitHub Actions qui lint + teste à chaque push.

## Fonctionnalités

- Grille 6x7 classique, gravité des pions à la souris
- Prévisualisation du pion avant de jouer (survol de colonne)
- Détection de victoire dans les 4 directions (ligne, colonne, 2 diagonales) et match nul
- Écran de fin de partie avec relance (`R`) sans quitter le jeu
- Logique du plateau 100% testable sans fenêtre graphique

## Structure du projet

```
connect-four/
├── src/
│   ├── main.py       # point d'entrée
│   ├── game.py         # boucle de jeu et rendu pygame
│   ├── board.py          # logique pure du plateau (testable)
│   └── settings.py         # constantes (grille, couleurs, tailles...)
├── tests/
│   └── test_board.py        # tests unitaires (pytest)
├── .github/workflows/ci.yml  # lint (ruff) + tests (pytest) sur push/PR
├── requirements.txt
└── requirements-dev.txt
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
```

> **Note Python 3.14** : comme pour le Snake clone, ce projet utilise `pygame-ce`
> (fork communautaire, drop-in compatible, `import pygame` inchangé) plutôt que
> `pygame` classique, qui ne fournit pas encore de wheel précompilée pour
> Python 3.14 sur Windows.

## Lancer le jeu

```bash
python -m src.main
```

Commandes : clic gauche sur une colonne pour y jouer, `R` pour rejouer après un game over, `Échap` pour quitter.

## Lancer les tests

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Prochaines étapes possibles

- Ajouter une IA simple (minimax) comme adversaire
- Ajouter un mode 2 joueurs en ligne (socket ou websocket)
- Conteneuriser avec Docker (voir le projet transversal #25 de la roadmap)
