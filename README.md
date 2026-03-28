# Chatbot FAQ 

Application web de chatbot 

Le projet propose **2 modes de fonctionnement** :

- **Mode Standard** : recherche de similarité simple entre la question utilisateur et les questions définies dans `faq.json`
- **Mode Groq** : recherche dans la FAQ + reformulation de la réponse avec un modèle LLM via l’API **Groq**

---

## Fonctionnalités

- Interface web simple et rapide avec Streamlit
- Questions/réponses configurables dans un fichier `faq.json`
- Deux modes :
  - Standard
  - Groq
- Possibilité de modifier la FAQ sans toucher au code
- Fonctionne localement sur un ordinateur
- Fallback si aucune réponse pertinente n’est trouvée

---

## Structure du projet

```bash
chatbot-faq/
│
├── chatbot.py
├── faq.json
├── .env
├── requirements.txt
├── .gitignore
└── README.md


##  Prérequis

Avant de lancer le projet, il faut avoir :

Python 3.10+ recommandé
pip


1. Cloner le projet
git clone https://github.com/VOTRE-USERNAME/VOTRE-REPO.git
cd VOTRE-REPO

2. Créer un environnement virtuel
-Windows
python -m venv venv
venv\Scripts\activate

-Mac / Linux
python3 -m venv venv
source venv/bin/activate

Quand l’environnement est activé, vous verrez généralement (venv) au début de la ligne du terminal.



3. Installer les dépendances
pip install -r requirements.txt

4. Configurer le fichier .env
Créer un fichier .env à la racine du projet.

Exemple :
GROQ_API_KEY=votre_cle_api_groq


5. Lancer l’application
streamlit run chatbot.py

Après lancement, Streamlit affichera une adresse locale dans le terminal, généralement :

http://localhost:8501

Ouvrir ce lien dans le navigateur.



PS Obtenir une clé API Groq
Créer un compte sur Groq Console
Générer une API key
Ajouter la clé dans le fichier .env
Exemple :
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxx

api_key :
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


Le chatbot ne trouve pas de réponse ?

Vérifier :

que la question existe dans faq.json
qu’il y a plusieurs formulations possibles
que le JSON est bien formé
