import requests
import json
import re
import sys
import argparse
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import random
from utile.display import console

class Profileur:
    def __init__(self, nom, prenom, age=None):
        self.nom = nom.lower()
        self.prenom = prenom.lower()
        self.age = age
        self.resultats = {
            "informations_personnelles": {},
            "reseaux_sociaux": {},
            "adresses": [],
            "informations_professionnelles": {},
            "articles_et_mentions": [],
            "autres_informations": []
        }
        # Headers plus récents pour éviter les blocs
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
    def rechercher_google(self, requete, max_resultats=10):
        """Effectue une recherche Google avec des sélecteurs mis à jour"""
        url = f"https://www.google.com/search?q={quote_plus(requete)}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            resultats = []
            # Les résultats Google sont généralement dans des div class="g" ou "tF2Cxc"
            for g in soup.select('.tF2Cxc, .g'):
                anchors = g.find_all('a')
                if anchors:
                    lien = anchors[0]['href']
                    titre = g.find('h3').text if g.find('h3') else "Sans titre"
                    
                    # Nouveaux sélecteurs pour la description (snippet)
                    desc_tag = g.select_one('.VwiC3b, .st, .y8L7Rb')
                    description = desc_tag.text if desc_tag else "Pas de description"
                    
                    resultats.append({
                        'titre': titre,
                        'lien': lien,
                        'description': description
                    })
                if len(resultats) >= max_resultats:
                    break
            return resultats
        except Exception as e:
            return []
    
    def analyser_reseaux_sociaux(self):
        console.print("[bold blue][*] Recherche sur les réseaux sociaux...[/bold blue]")
        plateformes = {
            "LinkedIn": f"site:linkedin.com/in/ \"{self.prenom} {self.nom}\"",
            "Facebook": f"site:facebook.com/ \"{self.prenom} {self.nom}\"",
            "Twitter/X": f"site:twitter.com/ \"{self.prenom} {self.nom}\"",
            "Instagram": f"site:instagram.com/ \"{self.prenom} {self.nom}\""
        }
        
        for plateforme, requete in plateformes.items():
            resultats = self.rechercher_google(requete, max_resultats=3)
            if resultats:
                self.resultats["reseaux_sociaux"][plateforme] = resultats
            sleep(random.uniform(1, 2))
    
    def extraire_informations(self, resultat):
        """Amélioration de l'extraction de données dans le texte"""
        texte = f"{resultat['titre']} {resultat['description']}"
        
        motifs = {
            "Email": r'[\w\.-]+@[\w\.-]+\.\w+',
            "Téléphone": r'(?:\+?33|0)[1-9](?:[\s.-]?\d{2}){4}',
            "Âge": r'(\d+)\s*ans',
            "Ville": r'(?:habite à|vit à|réside à)\s*([A-Z][\w-]+)'
        }
        
        for type_info, motif in motifs.items():
            correspondances = re.findall(motif, texte, re.IGNORECASE)
            if correspondances:
                if type_info not in self.resultats["informations_personnelles"]:
                    self.resultats["informations_personnelles"][type_info] = []
                # On nettoie et on ajoute
                for c in correspondances:
                    if isinstance(c, tuple): c = c[0]
                    self.resultats["informations_personnelles"][type_info].append(c.strip())

    def rechercher_adresses(self):
        console.print("[bold blue][*] Recherche d'adresses...[/bold blue]")
        requete = f"\"{self.prenom} {self.nom}\" adresse"
        resultats = self.rechercher_google(requete, max_resultats=5)
        
        motif_adresse = r'\d+\s+[\w\s]{5,30}\s+(?:rue|avenue|boulevard|impasse|place|chemin|voie)\s+[\w\s]+'
        for resultat in resultats:
            self.extraire_informations(resultat) # On en profite pour extraire d'autres infos
            adresses = re.findall(motif_adresse, resultat['description'], re.IGNORECASE)
            if adresses:
                self.resultats["adresses"].extend(adresses)

    def rechercher_informations_professionnelles(self):
        console.print("[bold blue][*] Recherche professionnelle...[/bold blue]")
        requete = f"\"{self.prenom} {self.nom}\" entreprise OR poste OR emploi"
        resultats = self.rechercher_google(requete, max_resultats=5)
        if resultats:
            self.resultats["informations_professionnelles"]["Pros"] = resultats

    def executer_recherche_complete(self):
        """Lance l'ensemble des modules"""
        self.analyser_reseaux_sociaux()
        self.rechercher_adresses()
        self.rechercher_informations_professionnelles()
        return self.resultats
    
    def afficher_resultats(self):
        """Affichage structuré avec les couleurs de ton application"""
        console.print(f"\n[bold green]======= RAPPORT DE PROFILAGE : {self.prenom.upper()} {self.nom.upper()} =======[/bold green]")
        
        # 1. Infos Personnelles
        if self.resultats["informations_personnelles"]:
            console.print("\n[bold cyan][📊] Informations extraites :[/bold cyan]")
            for cat, vals in self.resultats["informations_personnelles"].items():
                unique_vals = ", ".join(set(vals))
                console.print(f"  • [yellow]{cat}[/yellow]: {unique_vals}")
        
        # 2. Réseaux Sociaux
        if self.resultats["reseaux_sociaux"]:
            console.print("\n[bold cyan][🌐] Présence en ligne :[/bold cyan]")
            for plateforme, items in self.resultats["reseaux_sociaux"].items():
                console.print(f"  [bold underline]{plateforme}[/bold underline]:")
                for i in items:
                    console.print(f"    - {i['titre']}\n      [dim]{i['lien']}[/dim]")

        # 3. Adresses
        if self.resultats["adresses"]:
            console.print("\n[bold cyan][🏠] Adresses potentielles :[/bold cyan]")
            for adr in set(self.resultats["adresses"]):
                console.print(f"  • {adr.strip()}")

        # 4. Professionnel
        if self.resultats["informations_professionnelles"]:
            console.print("\n[bold cyan][💼] Secteur Professionnel :[/bold cyan]")
            for _, res in self.resultats["informations_professionnelles"].items():
                for r in res[:2]:
                    console.print(f"  • {r['titre']}\n    [dim]{r['lien']}[/dim]")

        console.print("\n[bold green]================ END OF REPORT =================[/bold green]")