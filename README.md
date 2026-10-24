# Compresseur Hybride (LZ77 + Huffman)

Ce dépôt contient le code source en Python d'un outil de compression et décompression de données basé sur une approche hybride combinant le codage par dictionnaire **LZ77** et le codage d'entropie de **Huffman**. Ce projet a été réalisé dans le cadre de l'examen de **Traitement du Signal et Compression de Données**.

---

## 🛠️ Fonctionnalités

- **LZ77 (Fenêtre Glissante) :** Analyse les redondances dans les flux de données et génère des tokens sous forme de paires (décalage, longueur) ou de caractères littéraux.
- **Codage de Huffman :** Optimise la représentation binaire des tokens en attribuant des codes de longueur variable selon leur fréquence d'apparition.
- **Support Multiformat :** Manipulation directe en mode binaire (`bytes`), permettant de tester la compression sur divers types de fichiers (textes, audios, images, vidéos).

---

## 📋 Prérequis

- **Python :** Version 3.10 ou supérieure recommandée.
- Aucune bibliothèque externe complexe n'est requise (utilise uniquement les modules natifs `heapq` et `pickle`).

---

## 🚀 Utilisation

Le script s'exécute via une interface interactive en ligne de commande :

```bash
python HybridCompression.py

1. Compresser un fichier
Lancez le script.

Entrez le mode : c (pour compresser).

Indiquez le chemin du fichier source (ex: tests/sample.txt).

Indiquez le chemin et le nom du fichier de sortie compressé (ex: archive.bin).

2. Décompresser un fichier
Lancez le script.

Entrez le mode : d (pour décompresser).

Indiquez le chemin du fichier compressé (ex: archive.bin).

Indiquez le chemin du fichier de sortie restauré (ex: restored_file.txt).

📂 Structure du Dépôt
Plaintext
├── HybridCompression.py    # Script principal du compresseur/décompresseur
├── tests/                  # Dossier contenant les fichiers de test (texte, audio, image, vidéo)
└── README.md               # Documentation du projet
📊 Évaluation des Performances
Conformément aux exigences du sujet, les tests de taux de compression et d'efficacité ont été menés sur quatre types de fichiers :

Fichiers Texte

Fichiers Audio

Fichiers Images

Fichiers Vidéo