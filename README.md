\# POC 1 : 



&nbsp;l’analyse statistique et l’exploitation des évaluations des formations



\## pour exécuter le code :



Créer un environnement virtuel pour python 

pip install requirements.py

dans le terminal : cd evaluations - Copie

streamlit run main.py

Pour accéder à l’interface de dashboard, utilisez les identifiants suivants :

Nom d’utilisateur : user.cdd

Mot de passe : 123





\##  Installation



&nbsp;Cloner le dépôt

```bash

git clone https://github.com/votre-username/nom-du-projet.git

cd nom-du-projet



\## Structure du projet : 



├── src/ 

│

├───backend

│   │   analysis.py

│   │   nlp\_preprocessing.py

│   │   topic\_modeling.py

│   │   \_\_init\_\_.py

│   │

│   ├───auth

│   │   │   login.py

│   │   │   \_\_init\_\_.py

│   │   │

│   │   └───\_\_pycache\_\_

│   │           login.cpython-37.pyc

│   │           \_\_init\_\_.cpython-37.pyc

│   │

│   ├───cache

│   ├───models

│   │       bertopic\_model.pkl

│   │

│   └───\_\_pycache\_\_

│           analysis.cpython-312.pyc

│           analysis.cpython-37.pyc

│           nlp\_preprocessing.cpython-37.pyc

│           topic\_modeling.cpython-312.pyc

│           topic\_modeling.cpython-37.pyc

│           \_\_init\_\_.cpython-312.pyc

│           \_\_init\_\_.cpython-37.pyc

│

├───config

│   │   settings.py

│   │   \_\_init\_\_.py

│   │

│   └───\_\_pycache\_\_

│           settings.cpython-37.pyc

│           \_\_init\_\_.cpython-37.pyc

│

├───data

│   │   evaluation\_formation\_francais.csv

│   │   loader.py

│   │   \_\_init\_\_.py

│   │

│   └───\_\_pycache\_\_

│           loader.cpython-312.pyc

│           loader.cpython-37.pyc

│           \_\_init\_\_.cpython-37.pyc

│

├───frontend

│   │   completion\_rates.py

│   │   scores\_analysis.py

│   │   summary\_cards.py

│   │   temporal\_analysis.py

│   │   \_\_init\_\_.py

│   │

│   └───\_\_pycache\_\_

│           completion\_rates.cpython-312.pyc

│           completion\_rates.cpython-37.pyc

│           scores\_analysis.cpython-312.pyc

│           scores\_analysis.cpython-37.pyc

│           summary\_cards.cpython-312.pyc

│           summary\_cards.cpython-37.pyc

│           temporal\_analysis.cpython-312.pyc

│           temporal\_analysis.cpython-37.pyc

│           \_\_init\_\_.cpython-312.pyc

│           \_\_init\_\_.cpython-37.pyc

│

├───utils

│   │   preprocessing.py

│   │   report\_generator.py

│   │   \_\_init\_\_.py

│   │

│   └───\_\_pycache\_\_

│           report\_generator.cpython-312.pyc

│           report\_generator.cpython-37.pyc

│           \_\_init\_\_.cpython-312.pyc

│           \_\_init\_\_.cpython-37.pyc

│

└───\_\_pycache\_\_

&nbsp;       config.cpython-312.pyc

&nbsp;       config.cpython-37.pyc

├── README.md     # Ce fichier

└── requirements.txt  # Dépendances Python

