# 🟡 Boîte Blanche — Découverte de l'IA par les mécanismes

## 🎯 Objectif Pédagogique

**Armer l'esprit critique** par la compréhension des mécanismes internes de l'IA.
Contrairement à une approche "boîte noire" qui utilise des termes biologiques (`neurone`, `apprendre`, `comprendre`), la démarche **Boîte Blanche** consiste à **nommer le mécanisme sous le mot** : une somme pondérée, une descente de gradient, un calcul de probabilités.

---

## 📚 Structure du Parcours

### **Introduction**
- `index.html` : Page d'orientation vers les 9 chapitres

### **Chapitre 1 — Le neurone artificiel : une fonction, pas un organe**
- **Question** : On abandonne « est-il intelligent ? » pour « que calcule-t-il ? »
- **Objectif** : Ramener le « neurone » à sa réalité : somme pondérée + fonction d'activation
- **Contenu** : Somme pondérée, biais, fonction échelon (Heaviside)

### **Chapitre 2 — Le réseau : composer des transformations simples**
- **Question** : « que fait un neurone ? » → « que fait un réseau de neurones ? »
- **Objectif** : Montrer que le réseau est une chaîne de multiplications matricielles et de non-linéarités
- **Contenu** : Couches, profondeur, propagation avant, limites du perceptron, hiver de l'IA

### **Chapitre 3 — L'apprentissage : comment les poids se fixent**
- **Question** : On ne demande plus ce que fait le réseau, mais comment il s'est formé
- **Objectif** : Comprendre que les poids résultent d'une minimisation d'erreur
- **Contenu** : Fonction de perte, descente de gradient, rétropropagation, généralisation vs mémorisation

### **Chapitre 4 — Une même mécanique, des objectifs différents**
- **Question** : Pour quoi est-il fait ?
- **Objectif** : Comprendre que la taxonomie des IA est une taxonomie d'objectifs, pas de mécanismes
- **Contenu** : Classifieurs, régression, traduction, génération, apprentissage par renforcement

### **Chapitre 5 — La mécanique propre au langage**
- **Question** : Comment saisit-il le langage ?
- **Objectif** : Expliquer la chaîne : tokenisation → embeddings → attention → prédiction
- **Contenu** : Tokens, attention, génération auto-régressive

### **Chapitre 6 — Données et probabilités**
- **Question** : Que produit-il exactement ?
- **Objectif** : Comprendre que la sortie est une distribution de probabilités conditionnée
- **Contenu** : Corpus, biais, température, hallucination comme propriété structurelle

### **Chapitre 7 — « Comprendre » la question et planifier la réponse**
- **Question** : Que fait-il paraître ?
- **Objectif** : Dissocier l'effet de compréhension du mécanisme
- **Contenu** : Prompt, fine-tuning, alignement, plan de réponse

### **Chapitre 8 — Chain of thought : le raisonnement comme comportement émergent**
- **Question** : Que fait-il ?
- **Objectif** : Expliquer pourquoi les étapes intermédiaires améliorent les résultats
- **Contenu** : Agents, outils, test-time compute

### **Chapitre 9 — Ce que la boîte blanche révèle des limites**
- **Question** : Que révèle cette mécanique de ses limites ?
- **Objectif** : Armer l'esprit critique
- **Contenu** : Limites structurelles, évaluation, vérification, contrôle

---

## 🎓 Public Cible

- **Débutants** en intelligence artificielle
- **Pédagogues** cherchant une approche méchaniste
- **Curieux** qui veulent comprendre sans utiliser
- **Critiques** souhaitant démystifier l'IA

---

## 💡 Philosophie

> « On ne peut pas juger ce qu'on ne comprend pas. »
> La démarche Boîte Blanche propose une **compréhension mécanique** plutôt qu'une **utilisation aveugle** ou un **jugement sans fondement**.

---

## 🚀 Utilisation

1. Commencez par `index.html` pour une vue d'ensemble
2. Parcourez les chapitres dans l'ordre pour une progression logique
3. Chaque chapitre contient :
   - Des explications théoriques
   - Des exemples concrets
   - Des visualisations (le cas échéant)
   - Des liens vers les concepts suivants

---

## 📦 Contenu du Répertoire
```text 
boiteblanche/
├── index.html                 # Page d'accueil et d'orientation
├── chapitre1/chapitre1.html            # Le neurone artificiel
├── chapitre1-1.html          # Expérimentation pratique
├── chapitre2/chapitre2.html            # Le réseau
├── chapitre3/chapitre3.html            # L'apprentissage
├── chapitre4.html            # Objectifs différents
├── chapitre5.html            # Mécanique du langage
├── chapitre6.html            # Données et probabilités
├── chapitre7.html            # Compréhension et planification
├── chapitre8.html            # Chain of thought
├── chapitre9.html            # Limites
├── feu-modele-ia.html        # Simulation interactive
├── Perspective boîte blanche.md
└── img/                      # Images et illustrations
```

---

## 🎨 Caractéristiques

- ✅ **Approche progressive** : Chaque chapitre répond à une nouvelle question
- ✅ **Pédagogie visuelle** : Schémas, graphiques et animations
- ✅ **Interactivité** : Expérimentations pratiques (chapitre1-1.html, feu-modele-ia.html)
- ✅ **Rigueur scientifique** : Explications précises des mécanismes
- ✅ **Accessibilité** : Langage clair, sans jargon inutile

---
## 📖 Pour aller plus loin

Consultez `Perspective boîte blanche.md` pour une vision détaillée de la philosophie et de la progression pédagogique.

## 🌐 Application web et utilisation hors ligne

Le dépôt est publiable comme site statique, sans serveur applicatif ni étape de compilation.
Le workflow GitHub Actions `.github/workflows/deploy-pages.yml` valide les ressources,
puis publie le contenu sur GitHub Pages à chaque mise à jour de `main` (et à la demande).

Après activation de GitHub Pages avec **Source: GitHub Actions** dans les paramètres du dépôt,
l'application sera accessible à l'adresse :

**https://ric-typologies-des-ia.github.io/boiteblanche/**

La page d'accueil expose un manifeste PWA et enregistre un service worker. Les pages,
feuilles de style, scripts locaux et illustrations listés dans le cache de précaution sont
disponibles après le premier chargement en ligne ; l'application peut ensuite être installée
depuis un navigateur compatible et consultée hors connexion.

La visualisation des feux tricolores utilise une copie locale de **Chart.js 4.4.0**
(`vendor/chart.js/`), distribuée sous licence MIT avec son fichier de licence.
Cette dépendance est incluse dans le cache initial du service worker : aucun accès à un CDN
n'est nécessaire pour afficher les graphiques après l'installation du cache hors ligne.
