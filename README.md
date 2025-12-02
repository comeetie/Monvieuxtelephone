# Mon vieux Téléphone U43

Un petit projet perso pour transformer un téléphone filaire ancien (modèle **U43**) en interface audio interactive.


[//]: # (https://upload.wikimedia.org/wikipedia/commons/3/33/T%C3%A9l%C3%A9phone_U43_B.C.I.jpg)
![Un magnifique Téléphone U4](./U43.png)

L’utilisateur décroche le combiné, compose un numéro, et le système lit des fichiers audio ou exécute des scripts Python selon la structure du répertoire `Stories/`.
Avec la possibilité de créer des histoires dont vous êtes le héros type "si ... rendez-vous au 53, sinon rendez-vous au 128."

Ce projet repose sur :
- un raspberry Pi Zéro ou Pi Zéro 2
- une carte son i2c/i2s type Waveshare WM8960 
- un combiné téléphonique U43 connecté à la carte son du RPI, et aux GPIO du Pi pour la lecture du cadran rotatif et de l'interrupteur décroché / raccroché
- Python (lecture audio, exécution de scripts)
- mpg123 pour jouer les MP3 
- systemd pour démarrer automatiquement au boot 
- Bluetooth optionnel pour rediriger le son vers un casque et profiter d'une bonne qualité audio 


# Fonctionnement général

Le script principal est `storyphone.py`
Chaque dossier dans `Stories/` correspond à un chiffre.
Les numéros composés construisent progressivement un chemin :

```text
Stories/
├── 1/
│ ├── description.mp3
│ ├── ...
│ ├── 5.py
│ └── 2/
│ ├── description.mp3
│ ├── ...
│ └── 3.mp3
│ ...
├── 4/
│ ├── description.mp3
│ ├── ...
│ └── 3/
│ ├── description.mp3
│ ├── ...
│ └── 120.mp3
```

## Exemple
- Utilisateur tape **123** → le Pi lance :  
  - `Stories/1/2/3.mp3`  

- Utilisateur tape **43** → le Pi lit :  
  - `Stories/4/3/description.mp3` et garde **43** comme préfix pour les futurs numéros
  - Si l'utilisateur compose ensuite 120  le Pi lit `Stories/4/3/120.mp3`
  - Ce mode permet de gérer les histoires interactives on place les fichier de l'histoire dans le même répertoire et l'utilisateur n'a pas besoin de retaper l'indicatif du dossier à chaque chapitre.   
 


## Autres scripts 

Plusieurs petit outils,

Pour tester les entrées du téléphone et debugger

- `test_switch.py`
- `rotary.py`
- `rotary_raw.py`

Pour créer le contenu :

- `txt2mp3.py` génération des description audio avec gtts a partir de txt
- `download_podcast.py` téléchargement de podcast et renomage 1.mp3, ... ,25.mp3
- `generate_meteo.py` génération de fichier audio avec la méteo a faire tourner avec `cron (0 */5 * * * /usr/bin/python3 /home/pi/generate_meteo.py >> /home/pi/cron.log 2>&1)`
- `heure.py` horloge parlante
- `prochain_passage.py` prochain passages théorique API IDFM
- `prochain_passage_rt.py` prochain passages temps réél API IDFM



# Installation

## Cablage du Pi


![cadran rotatif crédit revolunet](https://raw.githubusercontent.com/revolunet/s63/master/assets/anim-cadran.gif)


| Fonction / cables du U43                                    | GPIO |
| ----------------------------------------------------------- | ---- |
| Détection décroché (Fil bleu de l'interrupteur)             | 17   |
| Masse décroché (Fil marron de l'interrupteur)               | GND  |
| Lecture impulsions numérotés (Fil rouge du cadran)          | 25   |
| Masse impulsions numérotés (Fil blanc-rouge du cadran)      | GND  |
| Fil Rouge et Bleu du combiné      | sortie audio de Waveshare WM8960  |


## Dépendances
```bash
sudo apt install mpg123 
pip3 install gtts requests
```

## Liens, références

- https://fablab-chalon.fr/wp-content/uploads/2023/02/Projet-Telephone-U43-2022-11.pdf
- http://jacques.reumont.free.fr/Arduino/U43.pdf
- https://github.com/revolunet/s63
