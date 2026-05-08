# Watch_dogs_projet

## Arboressence : 

Watch_dogs_projet/
├── main.py              # Fichier principal
├── module/
│   ├── phone.py         # Module PhonyNode
│   ├── web.py           # Module WebScanner
│   ├── mail.py          # Module EmailOSINT
│   └── pseudo.py        # Module UsernameOSINT
├── core/
│   ├── base.py          # Classe parente JustradamusModule
│   └── config.py        # Headers et timeout
└── utile/
    └── display.py       # Fonctions d'affichage (print_banner, console)

## Installation : 

git clone https://github.com/Julien-hub0309/Watch_dogs_projet.git

cd Watch_dogs_projet

pip install requests 
pip install phonenumbers 
pip install dnspython 
pip install rich

## Utilisation : 

cd Watch_dogs_projet

python3 main.py 
