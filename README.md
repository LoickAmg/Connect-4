# Puissance 4 (Connect Four)

Un Puissance 4 en Python/Pygame, avec trois modes de jeu (local, IA, en ligne), axé sur la manipulation de grille, la logique de jeu et l'algorithmique (minimax), avec une logique séparée du rendu (facile à tester unitairement) et une CI GitHub Actions qui lint + teste à chaque push.

## Fonctionnalités

- Grille 6x7 classique, gravité des pions à la souris, prévisualisation avant de jouer
- Détection de victoire dans les 4 directions (ligne, colonne, 2 diagonales) et match nul
- **Mode local** : deux joueurs sur le même clavier/souris
- **Mode contre l'IA** : minimax avec élagage alpha-bêta, 3 niveaux de difficulté (profondeur 2/4/6), calculée dans un thread séparé pour ne pas geler la fenêtre
- **Mode multijoueur en ligne** : connexion directe pair-à-pair en sockets TCP (un joueur héberge, l'autre rejoint via son adresse IP), sans dépendance externe
- Écran de fin de partie avec relance (`R`) sans quitter le jeu
- Logique du plateau, de l'IA et du réseau 100% testables sans fenêtre graphique

## Structure du projet

```
connect-four/
├── src/
│   ├── main.py       # point d'entrée (affiche le menu puis lance la partie)
│   ├── menu.py         # écran de menu (choix du mode, difficulté, IP)
│   ├── game.py           # boucle de jeu et rendu pygame
│   ├── ai.py               # IA minimax + élagage alpha-bêta (testable)
│   ├── network.py            # connexion TCP pair-à-pair (testable)
│   ├── board.py                 # logique pure du plateau (testable)
│   └── settings.py                # constantes (grille, couleurs, tailles...)
├── tests/
│   ├── test_board.py    # logique du plateau
│   ├── test_ai.py         # l'IA prend un coup gagnant / bloque l'adversaire
│   └── test_network.py      # échange de messages et détection de déconnexion
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

Un menu au clavier s'affiche pour choisir le mode :

- `1` — deux joueurs en local
- `2` — contre l'IA (puis `1`/`2`/`3` pour la difficulté)
- `3` — multijoueur en ligne (`1` pour héberger, `2` pour rejoindre + saisir l'IP)

En partie : clic gauche sur une colonne pour y jouer, `R` pour rejouer après une fin de partie, `Échap` pour quitter.

### Multijoueur en ligne

Le mode en ligne fonctionne en pair-à-pair, sans serveur tiers : un des deux
joueurs choisit "Héberger" (le jeu ouvre un port TCP — `5555` par défaut — et
attend), l'autre choisit "Rejoindre" et saisit l'adresse IP de l'hôte (et le
port si besoin, ex. `192.168.1.10:5555`). Sur le même réseau local, l'IP
locale de l'hôte suffit ; pour jouer via Internet, l'hôte doit rediriger le
port 5555 sur sa box/routeur (ou utiliser un tunnel type ngrok/Tailscale).

## Lancer les tests

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Prochaines étapes possibles

- Historique des coups et bouton "annuler"
- Meilleure UI pour le menu (souris, thème, animations)
- Conteneuriser avec Docker (voir le projet transversal #25 de la roadmap)
