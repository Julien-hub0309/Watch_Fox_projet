# Cahier des Charges — Watch Fox
## Framework OSINT d'Investigation & d'Intelligence Numérique

---

> **Document** : Cahier des Charges Technique et Fonctionnel  
> **Projet** : Watch Fox  
> **Version analysée** : v1.0 (build 2026-05-09)  
> **Auteur du projet** : Justradamus  
> **Type** : Outil CLI Python — OSINT / Cyber-investigation  
> **Date de rédaction du CDC** : 09 mai 2026  

---

## Table des matières

1. [Présentation générale](#1-présentation-générale)
2. [Contexte et objectifs](#2-contexte-et-objectifs)
3. [Périmètre fonctionnel](#3-périmètre-fonctionnel)
4. [Architecture technique](#4-architecture-technique)
5. [Spécifications détaillées des modules](#5-spécifications-détaillées-des-modules)
   - 5.1 [Module Téléphone (PhonyNode)](#51-module-téléphone--phonynode)
   - 5.2 [Module Web/IP (WebScanner)](#52-module-webip--webscanner)
   - 5.3 [Module Email (EmailOSINT)](#53-module-email--emailosint)
   - 5.4 [Module Pseudo/Username (UsernameOSINT)](#54-module-pseudousername--usernameosint)
   - 5.5 [Module Scan Réseau (NetworkScanner)](#55-module-scan-réseau--networkscanner)
   - 5.6 [Module Traceroute (Traceroute)](#56-module-traceroute--traceroute)
6. [Noyau applicatif (core)](#6-noyau-applicatif--core)
   - 6.1 [Classe de base (JustradamusModule)](#61-classe-de-base--justradamusmodule)
   - 6.2 [Scanner OSINT générique (OSINTScanner)](#62-scanner-osint-générique--osintscanner)
   - 6.3 [Configuration globale (config.py)](#63-configuration-globale--configpy)
7. [Utilitaires d'affichage](#7-utilitaires-daffichage)
8. [Persistance des données](#8-persistance-des-données)
9. [Interfaces d'entrée/sortie](#9-interfaces-dentréesortie)
10. [Dépendances et environnement](#10-dépendances-et-environnement)
11. [Exigences non fonctionnelles](#11-exigences-non-fonctionnelles)
12. [Limites actuelles et dette technique](#12-limites-actuelles-et-dette-technique)
13. [Pistes d'évolution](#13-pistes-dévolution)
14. [Glossaire](#14-glossaire)

---

## 1. Présentation générale

**Watch Fox** est un framework d'investigation numérique open source en ligne de commande (CLI), développé en Python 3.13. Il permet à un utilisateur de collecter, agréger et consolider des informations publiquement disponibles sur une cible numérique à partir de plusieurs vecteurs d'investigation : numéro de téléphone, adresse e-mail, pseudonyme/username, domaine web ou adresse IP, et infrastructure réseau.

Le projet est structuré autour d'un moteur modulaire extensible. Chaque type de cible correspond à un module indépendant qui hérite d'une classe de base commune, garantissant la cohérence des comportements (sauvegarde, affichage, persistance en base).

L'outil s'inscrit dans la catégorie des outils **OSINT** (Open Source Intelligence), dont la finalité est de recueillir des renseignements à partir de sources librement accessibles, sans exploitation de failles de sécurité ni accès non autorisé à des systèmes tiers.

---

## 2. Contexte et objectifs

### 2.1 Contexte

La collecte de renseignements en sources ouvertes est une pratique légitimement utilisée par :

- Les chercheurs en cybersécurité (Bug Bounty, pentesters)
- Les journalistes d'investigation
- Les services de conformité et de vérification d'identité (KYC)
- Les équipes Blue Team (SOC, CERT) dans un cadre défensif
- Les particuliers souhaitant auditer leur propre empreinte numérique

Watch Fox centralise dans un seul outil des vérifications qui nécessiteraient normalement l'usage de dizaines de services en ligne disparates.

### 2.2 Objectifs principaux

| Priorité | Objectif |
|---|---|
| P0 | Fournir un outil CLI unifié d'investigation OSINT multi-vecteurs |
| P0 | Permettre la collecte automatisée d'informations publiques sur une cible |
| P1 | Persister les résultats dans une base SQLite et en fichiers JSON |
| P1 | Afficher les résultats de manière lisible et structurée dans le terminal |
| P2 | Être extensible facilement (ajout de modules ou de sites) |
| P2 | Permettre l'utilisation d'un proxy pour l'anonymisation des requêtes |

### 2.3 Périmètre légal et éthique

Watch Fox est conçu pour être utilisé **uniquement** sur des cibles pour lesquelles l'utilisateur dispose d'une autorisation explicite ou sur des données publiques dans le cadre légal applicable. L'outil ne contourne aucun mécanisme de protection, n'exploite aucune vulnérabilité, et ne réalise aucun accès non autorisé. La responsabilité légale de l'utilisation incombe entièrement à l'opérateur.

---

## 3. Périmètre fonctionnel

### 3.1 Vue d'ensemble des fonctionnalités

```
Watch Fox
├── [1] Investigation téléphonique    → géolocalisation, opérateur, validité
├── [2] Investigation Web/IP          → DNS, géo-IP, ISP, scan de ports rapide
├── [3] Investigation Email           → fuites, réputation, DNS/MX, réseaux sociaux
├── [4] Investigation Username        → présence sur ~60 plateformes classifiées
├── [5] Scan réseau                   → scan de ports multi-cibles, traceroute
└── [0] Quitter
```

### 3.2 Matrice fonctionnelle

| Fonctionnalité | Module | Statut actuel |
|---|---|---|
| Analyse de numéro de téléphone | PhonyNode | ✅ Implémenté |
| Résolution IP / géolocalisation | WebScanner | ✅ Implémenté |
| Scan de ports rapide (web) | WebScanner | ✅ Implémenté |
| Détection de fuites de données email | EmailOSINT | ✅ Implémenté |
| Réputation d'adresse email | EmailOSINT | ✅ Implémenté |
| Vérification DNS/MX | EmailOSINT | ✅ Implémenté |
| Présence sur réseaux sociaux (via email) | EmailOSINT | ✅ Implémenté |
| Recherche de pseudonyme (~60 sites) | UsernameOSINT | ✅ Implémenté |
| Scan de ports multi-IP avec plages | NetworkScanner | ✅ Implémenté |
| Scan de plages CIDR | NetworkScanner | ✅ Implémenté |
| Traceroute (nécessite root) | Traceroute | ✅ Implémenté |
| Sauvegarde JSON par scan | JustradamusModule | ✅ Implémenté |
| Persistance SQLite | JustradamusModule | ✅ Implémenté |
| Support proxy HTTP(S) | Tous modules | ✅ Partiel (param disponible) |
| Scan via base de données sites JSON | OSINTScanner | ✅ Implémenté (data/sites.json) |
| Rotation de User-Agent | config.py | ✅ Implémenté |
| Interface web ou GUI | — | ❌ Non prévu |
| Authentification / gestion utilisateurs | — | ❌ Non prévu |
| Export PDF / CSV | — | ❌ Non prévu (JSON seulement) |
| Notifications / alertes | — | ❌ Non prévu |

---

## 4. Architecture technique

### 4.1 Structure des répertoires

```
Watch_Fox/
│
├── main.py                        # Point d'entrée, boucle principale, menu CLI
│
├── core/                          # Noyau applicatif partagé
│   ├── __init__.py
│   ├── base.py                    # Classe mère JustradamusModule
│   ├── config.py                  # Configuration globale, User-Agents, timeout
│   └── scanner.py                 # OSINTScanner : chargement data/sites.json + scan parallèle
│
├── module/                        # Modules d'investigation spécialisés
│   ├── mail.py                    # EmailOSINT
│   ├── phone.py                   # PhonyNode
│   ├── scan.py                    # NetworkScanner + Traceroute
│   ├── web.py                     # WebScanner
│   └── pseudo.py                  # UsernameOSINT
│
├── utile/                         # Utilitaires transversaux
│   ├── __init__.py
│   └── display.py                 # Console Rich, bannière, IP publique
│
├── data/                          # Données de référence (non présent dans le zip mais référencé)
│   └── sites.json                 # Base des sites pour OSINTScanner (pseudo lookup)
│
├── Justradamus_Reports/           # Rapports JSON générés automatiquement
│   ├── Email_Intel_<cible>.json
│   ├── Phone_Intel_<cible>.json
│   ├── Username_Intel_<cible>.json
│   └── Web_Infra_<cible>.json
│
└── justradamus_intelligence.db    # Base SQLite centralisée de tous les findings
```

### 4.2 Diagramme d'héritage des classes

```
JustradamusModule (core/base.py)
├── PhonyNode          (module/phone.py)
├── WebScanner         (module/web.py)
├── EmailOSINT         (module/mail.py)
└── UsernameOSINT      (module/pseudo.py)

OSINTScanner (core/scanner.py)         [classe indépendante, non héritée de JustradamusModule]

NetworkScanner (module/scan.py)        [classe indépendante]
Traceroute     (module/scan.py)        [classe indépendante]
```

### 4.3 Flux d'exécution principal

```
Lancement (main.py)
    │
    ▼
print_banner()          ← récupère IP publique + hostname machine
    │
    ▼
Menu interactif (choix 1-5 ou 0)
    │
    ├─ Saisie de la cible (IP / domaine / email / pseudo / téléphone)
    │
    ▼
Instanciation du module correspondant
    │
    ▼
run_scan() / scan_infra()
    │
    ├─ Requêtes HTTP(S) vers APIs et sites tiers
    ├─ Résolutions DNS / socket
    ├─ Affichage Rich (live, coloré)
    │
    ▼
save_finding()          ← export JSON + INSERT SQLite
    │
    ▼
Affichage du résumé (Panel Rich)
    │
    ▼
Retour au menu (boucle infinie, Ctrl+C pour quitter)
```

---

## 5. Spécifications détaillées des modules

### 5.1 Module Téléphone — `PhonyNode`

**Fichier** : `module/phone.py`  
**Classe** : `PhonyNode(JustradamusModule)`  
**Dépendance principale** : `phonenumbers`

#### 5.1.1 Description fonctionnelle

Ce module analyse un numéro de téléphone passé en entrée pour en extraire les métadonnées publiques disponibles via la bibliothèque `phonenumbers` (basée sur la libphonenumber de Google).

#### 5.1.2 Comportement d'entrée

- Le numéro est normalisé : le caractère `+` est supprimé puis réajouté automatiquement.
- Format accepté : n'importe quelle représentation textuelle d'un numéro international (ex: `0033620446928`, `+33620446928`, `33620446928`).

#### 5.1.3 Données collectées

| Champ | Source | Description |
|---|---|---|
| `Pays` | `phonenumbers.geocoder` | Nom du pays de rattachement (locale FR) |
| `Operateur` | `phonenumbers.carrier` | Nom de l'opérateur mobile/fixe (locale FR) |
| `Validite` | `phonenumbers.is_valid_number()` | Booléen de validité du numéro selon les standards ITU |
| `Spam_Score` | — | Champ réservé, non implémenté (valeur statique en texte) |

#### 5.1.4 Exemple de rapport généré

```json
{
    "Pays": "France",
    "Operateur": "SFR",
    "Validite": true,
    "Spam_Score": "Recherche de réputation en cours..."
}
```

#### 5.1.5 Limitations et lacunes

- Le champ `Spam_Score` est un placeholder non fonctionnel : aucune API de réputation téléphonique (Numverify, Twilio Lookup, etc.) n'est actuellement intégrée.
- Aucune détection VOIP/VoIP vs numéro physique.
- Aucune recherche de titulaire (CNAM lookup).
- Aucune vérification de portabilité.

---

### 5.2 Module Web/IP — `WebScanner`

**Fichier** : `module/web.py`  
**Classe** : `WebScanner(JustradamusModule)`  
**Dépendances** : `socket`, `urllib.request`, `json`

#### 5.2.1 Description fonctionnelle

Ce module effectue une investigation d'infrastructure sur un domaine ou une adresse IP, en combinant résolution DNS, géolocalisation IP, identification de l'ISP/organisation, et scan basique de ports.

#### 5.2.2 Étapes d'investigation

1. **Résolution DNS** : `socket.gethostbyname(target)` → obtention de l'adresse IPv4.
2. **Géolocalisation IP** : requête vers l'API publique `http://ip-api.com/json/{ip}` avec parsing JSON.
3. **Scan de ports** : tentative de connexion TCP sur 5 ports courants avec un timeout de 0.5 seconde.
4. **Sauvegarde et affichage**.

#### 5.2.3 Données collectées

| Champ | Source | Description |
|---|---|---|
| `IP` | `socket.gethostbyname()` | Adresse IPv4 résolue |
| `Localisation` | ip-api.com | Ville et pays |
| `ISP` | ip-api.com | Fournisseur d'accès Internet |
| `Organisation` | ip-api.com | Organisation propriétaire de l'IP (ASN) |
| `Ports_Ouverts` | socket TCP | Liste des ports ouverts parmi : 21, 22, 80, 443, 8080 |

#### 5.2.4 Exemple de rapport généré

```json
{
    "IP": "151.101.193.55",
    "Localisation": "Montreal, Canada",
    "ISP": "Fastly, Inc.",
    "Organisation": "Fastly, Inc.",
    "Ports_Ouverts": "21, 80, 443"
}
```

#### 5.2.5 Choix techniques notables

- L'utilisation de `urllib.request` (stdlib pure) à la place de `requests` est un choix délibéré pour réduire les dépendances externes sur ce module.
- Les résultats de ports ouverts sont convertis en chaîne (`", ".join(map(str, open_ports))`) avant stockage pour assurer la compatibilité avec la méthode `display_results` de la classe de base.

#### 5.2.6 Limitations

- Scan de ports limité à 5 ports fixes. Pas de scan de plage personnalisée.
- Pas d'analyse de certificats TLS/SSL.
- Pas de résolution DNS inversée (reverse DNS / PTR).
- Pas de détection de sous-domaines.
- Pas d'analyse d'en-têtes HTTP (Server, X-Powered-By, etc.).
- L'API ip-api.com est gratuite avec des limites de taux (45 req/min pour l'usage non commercial).

---

### 5.3 Module Email — `EmailOSINT`

**Fichier** : `module/mail.py`  
**Classe** : `EmailOSINT(JustradamusModule)`  
**Dépendances** : `hashlib`, `requests`, `dns.resolver`, `urllib.parse`

#### 5.3.1 Description fonctionnelle

Ce module est le plus complet de Watch Fox. Il réalise une investigation multi-axes sur une adresse e-mail : détection de fuites dans des bases de données compromises, évaluation de la réputation de l'adresse, vérification de l'infrastructure DNS du domaine, et recherche de présence sur des plateformes sociales à partir du nom d'utilisateur extrait.

#### 5.3.2 Parsing de l'adresse e-mail

Lors de l'initialisation (`__init__`), l'e-mail est décomposé :
- `self.email` : adresse complète normalisée en minuscules
- `self.username` : partie locale (avant `@`)
- `self.domain` : domaine (après `@`)

#### 5.3.3 Checks implémentés par catégorie

**Fuites de données**

| Check | URL cible | Méthode de détection |
|---|---|---|
| Have I Been Pwned | `haveibeenpwned.com/unifiedsearch/{email}` | Parsing JSON, champ `Breaches` |
| LeakCheck | `leakcheck.io/api/public?check={email}` | Parsing JSON, champ `found` |
| Psbdmp.ws | `psbdmp.ws/api/v3/search/{email}` | Parsing JSON, champ `count` |
| BreachDirectory | `breachdirectory.org/api.php?query={email}` | Parsing JSON, champ `found == "true"` |

**Réputation et vérifications**

| Check | URL cible | Méthode de détection |
|---|---|---|
| EmailRep | `emailrep.io/{email}` | Parsing JSON, champs `reputation` et `suspicious` |
| Gravatar | `gravatar.com/avatar/{md5_hash}?d=404` | Code HTTP ≠ 404 |
| DNS/MX | `dns.resolver.resolve(domain, 'MX')` | Résolution DNS MX |

**Réseaux sociaux et tech** (via `username`)

| Plateforme | URL testée | Faux-positifs exclus via |
|---|---|---|
| Twitter/X | `nitter.net/{username}` | "this user does not exist" |
| Reddit | `reddit.com/user/{username}/about.json` | "not found" |
| GitHub | `api.github.com/users/{username}` | HTTP 200 + JSON |
| Medium | `medium.com/@{username}` | "not found", "404" |
| Steam | `steamcommunity.com/id/{username}` | "the specified profile could not be found" |

**Plateformes adultes** (via `username`)

| Plateforme | URL testée |
|---|---|
| OnlyFans | `onlyfans.com/{username}` |
| Fansly | `fansly.com/{username}` |
| Chaturbate | `chaturbate.com/{username}/` |
| ManyVids | `manyvids.com/Profile/{username}/` |

#### 5.3.4 Logique de détection des faux positifs

La méthode `_check_social()` utilise une liste de `not_found_texts`. Quand une réponse HTTP 200 est reçue, le corps de la réponse est analysé (en minuscules) : si l'un des textes d'erreur y figure, la présence est rejetée. Cela pallie le fait que de nombreux sites retournent un code 200 même pour les profils inexistants.

#### 5.3.5 Système d'état interne

Trois listes sont maintenues pendant le scan :
- `self.found` : liste des services où la cible a été trouvée, avec descriptif
- `self.not_found` : liste des services sans résultat
- `self.errors` : liste des services en timeout ou erreur réseau

#### 5.3.6 Exemple de rapport généré

```json
{
    "email": "exemple@gmail.com",
    "username": "exemple",
    "domain": "gmail.com",
    "found": [
        "DNS/MX: Serveurs: alt1.gmail-smtp-in.l.google.com.",
        "Twitter/X: https://nitter.net/exemple"
    ],
    "not_found": ["Have I Been Pwned", "LeakCheck", "Gravatar"],
    "errors": [],
    "total_found": 2
}
```

#### 5.3.7 Limitations

- L'API HIBP gratuite ne retourne plus les résultats détaillés sans clé API depuis 2019 ; la vérification via l'endpoint `unifiedsearch` peut ne plus fonctionner sans en-têtes supplémentaires.
- Nitter (miroir Twitter/X) est instable et peut être hors ligne.
- La détection via username extrait de l'email peut générer de nombreux faux positifs (le username `jean.dupont` peut matcher un profil `jean.dupont` sur Chaturbate qui n'a aucun lien avec l'email).
- Aucune vérification de l'existence réelle du compte email (SMTP VRFY, techniques de rebond).

---

### 5.4 Module Pseudo/Username — `UsernameOSINT`

**Fichier** : `module/pseudo.py`  
**Classe** : `UsernameOSINT(JustradamusModule)`  
**Dépendances** : `re`, `requests`, `rich`

#### 5.4.1 Description fonctionnelle

Ce module est le plus exhaustif de Watch Fox en termes de couverture. Il recherche la présence d'un pseudonyme sur un ensemble de plateformes en ligne couvrant les réseaux sociaux, l'écosystème de développement, le gaming, la création de contenu, les liens biographiques, les plateformes de dons et les sites adultes.

#### 5.4.2 Normalisation de l'entrée

- `self.username` : pseudonyme en minuscules, `@` supprimé
- `self.clean` : version sans caractères spéciaux (`re.sub(r'[^a-zA-Z0-9_-]', '', username)`) — utilisé pour les plateformes qui n'acceptent pas certains caractères

Les URL templates utilisent deux variables : `{username}` (version complète) et `{clean}` (version nettoyée).

#### 5.4.3 Inventaire des plateformes par catégorie

**Réseaux sociaux (11 plateformes)**

| Plateforme | URL template |
|---|---|
| Twitter/X | `nitter.net/{username}` |
| Instagram | `instagram.com/{username}/` |
| TikTok | `tiktok.com/@{username}` |
| Facebook | `facebook.com/{username}` |
| Reddit | `reddit.com/user/{username}/` |
| YouTube | `youtube.com/@{username}` |
| Twitch | `twitch.tv/{username}` |
| Pinterest | `pinterest.com/{username}/` |
| Snapchat | `snapchat.com/add/{username}` |
| Tumblr | `{username}.tumblr.com` |
| Mastodon | `mastodon.social/@{username}` |

**Développement & Tech (13 plateformes)**

| Plateforme | URL template |
|---|---|
| GitHub | `github.com/{username}` |
| GitLab | `gitlab.com/{username}` |
| Bitbucket | `bitbucket.org/{username}/` |
| Dev.to | `dev.to/{username}` |
| Docker Hub | `hub.docker.com/u/{username}` |
| NPM | `npmjs.com/~{username}` |
| PyPI | `pypi.org/user/{username}/` |
| CodePen | `codepen.io/{username}` |
| Replit | `replit.com/@{username}` |
| Kaggle | `kaggle.com/{username}` |
| LeetCode | `leetcode.com/{username}/` |
| HackerRank | `hackerrank.com/{username}` |
| HackTheBox | `app.hackthebox.com/users/{username}` |

**Blog & Contenu (6 plateformes)**

| Plateforme | URL template |
|---|---|
| Medium | `medium.com/@{username}` |
| Substack | `{username}.substack.com` |
| DeviantArt | `deviantart.com/{username}` |
| Vimeo | `vimeo.com/{username}` |
| Flickr | `flickr.com/people/{username}/` |
| Dailymotion | `dailymotion.com/{username}` |

**Gaming & Musique (7 plateformes)**

| Plateforme | URL template |
|---|---|
| Steam | `steamcommunity.com/id/{username}` |
| NameMC (Minecraft) | `namemc.com/profile/{username}` |
| Roblox | `roblox.com/user.aspx?username={username}` |
| Chess.com | `chess.com/member/{username}` |
| Lichess | `lichess.org/@/{username}` |
| Spotify | `open.spotify.com/user/{username}` |
| SoundCloud | `soundcloud.com/{username}` |

**Profils & Bio Links (6 plateformes)**

| Plateforme | URL template |
|---|---|
| About.me | `about.me/{username}` |
| Linktree | `linktr.ee/{username}` |
| Carrd | `{username}.carrd.co` |
| Keybase | `keybase.io/{username}` |
| Gravatar | `gravatar.com/{username}` |
| SlideShare | `slideshare.net/{username}` |

**Dons & Crowdfunding (5 plateformes)**

| Plateforme | URL template |
|---|---|
| Patreon | `patreon.com/{username}` |
| Ko-fi | `ko-fi.com/{username}` |
| BuyMeACoffee | `buymeacoffee.com/{username}` |
| Tipeee | `fr.tipeee.com/{username}` |
| Product Hunt | `producthunt.com/@{username}` |

**Plateformes adultes (9 plateformes)**

| Plateforme | URL template |
|---|---|
| OnlyFans | `onlyfans.com/{username}` |
| Fansly | `fansly.com/{username}` |
| ManyVids | `manyvids.com/Profile/{username}/` |
| Chaturbate | `chaturbate.com/{username}/` |
| Pornhub | `pornhub.com/users/{username}` |
| XVideos | `xvideos.com/profiles/{username}` |
| Cam4 | `cam4.com/{username}` |
| StripChat | `stripchat.com/{username}` |
| BongaCams | `fr.bongacams.com/profile/{username}` |

**Total : 57 plateformes couvertes**

#### 5.4.4 Méthode de vérification générique

La méthode `check_site(site_name, url_template, not_found_texts)` :
1. Formate l'URL avec `{username}` et `{clean}`
2. Exécute une requête GET avec headers aléatoires et proxy optionnel
3. Vérifie le code HTTP 200
4. Si 200, scanne le contenu HTML à la recherche des textes d'erreur fournis
5. Classe le résultat dans `found`, `not_found` ou `errors`

#### 5.4.5 Rapport de sortie

```json
{
    "username": "justradamus",
    "found": [
        {"site": "Twitter/X", "url": "https://nitter.net/justradamus"},
        {"site": "Reddit", "url": "https://www.reddit.com/user/justradamus/"}
    ],
    "not_found": ["Instagram", "TikTok", "Facebook"],
    "errors": [],
    "total_found": 15
}
```

#### 5.4.6 Affichage des résultats

À la fin du scan, les 10 premiers liens trouvés sont affichés en couleur. Si plus de 10 résultats, un message résume le surplus.

#### 5.4.7 Limitations

- Les requêtes sont séquentielles (pas de parallélisation dans ce module, contrairement à `OSINTScanner`). Sur 57 sites avec timeout de 10s, un scan complet peut prendre plusieurs minutes.
- Le taux de faux positifs est variable selon les plateformes et leur comportement d'authentification.
- Nitter peut être hors ligne.
- Certaines plateformes (Instagram, TikTok, Facebook) retournent des résultats non fiables sans cookies de session valides.

---

### 5.5 Module Scan Réseau — `NetworkScanner`

**Fichier** : `module/scan.py`  
**Classe** : `NetworkScanner`  
**Dépendances** : `socket`, `ipaddress`, `threading`

#### 5.5.1 Description fonctionnelle

Ce module réalise un scan de ports TCP sur une ou plusieurs adresses IP. Il est distinct de la classe de base `JustradamusModule` et ne réalise pas de persistance automatique.

#### 5.5.2 Formats d'entrée acceptés

| Format | Exemple | Description |
|---|---|---|
| IP simple | `192.168.1.1` | Scan d'une IP unique |
| Plage tiret (dernier octet) | `192.168.1.1-20` | Scan de 192.168.1.1 à 192.168.1.20 |
| Plage tiret (IP complètes) | `192.168.1.1-192.168.1.50` | Plage complète |
| Notation CIDR | `192.168.1.0/24` | Réseau entier (hôtes uniquement) |

#### 5.5.3 Ports scannés

Liste fixe de 8 ports : **21** (FTP), **22** (SSH), **80** (HTTP), **443** (HTTPS), **445** (SMB), **3306** (MySQL), **3389** (RDP), **8080** (HTTP alternatif).

#### 5.5.4 Mécanisme de parallélisation

- Un thread est lancé pour chaque combinaison (IP × port).
- Les threads sont regroupés par lots de 100 : au-delà, le module attend la fin du lot courant avant de continuer.
- Un verrou (`threading.Lock`) protège l'accès à la liste `self.open_ports` en contexte concurrent.
- Timeout par connexion : **0.4 seconde**.

#### 5.5.5 Affichage

Chaque port ouvert découvert est affiché immédiatement en vert dans la console, avec le format `[+] IP:PORT ouvert !`.

#### 5.5.6 Limitations

- La liste de ports est non configurable par l'utilisateur au runtime.
- Pas de détection de service/bannière (version grabbing).
- Pas de sauvegarde JSON / SQLite des résultats (contrairement aux autres modules).
- Pas de scan UDP.
- Scan séquentiel par lots de 100 : pour des grands réseaux, la performance peut être dégradée.

---

### 5.6 Module Traceroute — `Traceroute`

**Fichier** : `module/scan.py`  
**Classe** : `Traceroute`  
**Dépendances** : `socket`, `time`, `struct`

#### 5.6.1 Description fonctionnelle

Implémente un traceroute en Python pur via des raw sockets ICMP et UDP. La classe est définie mais **non exposée dans le menu principal** (elle n'est pas invoquée depuis `main.py`).

#### 5.6.2 Mécanisme

- Résolution DNS de la cible avec `socket.gethostbyname()`.
- Pour chaque TTL de 1 à `max_hops` (30) :
  - Création d'un socket UDP émetteur + socket RAW ICMP récepteur.
  - Envoi d'un datagramme UDP vide vers la cible sur le port 33434.
  - Attente du message ICMP Time Exceeded en retour.
  - Affichage de l'IP du routeur intermédiaire et du RTT.
- Arrêt quand l'adresse de destination est atteinte.

#### 5.6.3 Contraintes d'exécution

- **Nécessite les privilèges root/administrateur** pour créer des raw sockets ICMP.
- Un `PermissionError` est capturé proprement et notifie l'utilisateur.
- Timeout par saut : **2 secondes**.

#### 5.6.4 Limitations

- Non accessible depuis le menu principal (fonctionnalité orpheline).
- Nécessite `sudo` sous Linux/macOS, ce qui peut être une contrainte opérationnelle.
- Pas de résolution reverse DNS des sauts intermédiaires.

---

## 6. Noyau applicatif — `core`

### 6.1 Classe de base — `JustradamusModule`

**Fichier** : `core/base.py`

#### 6.1.1 Rôle

Classe mère abstraite dont héritent tous les modules d'investigation principaux. Elle fournit les fonctionnalités transversales : initialisation de l'environnement de travail, persistance JSON et SQLite, affichage standardisé.

#### 6.1.2 Constructeur `__init__(target, proxy=None)`

| Paramètre | Type | Description |
|---|---|---|
| `target` | `str` | La cible à investiguer (IP, email, numéro, pseudo, domaine) |
| `proxy` | `str` \| `None` | URL du proxy HTTP(S) optionnel |

Actions à l'initialisation :
1. Stockage de `self.target` et `self.proxy`
2. Définition de `self.results_dir = "Justradamus_Reports"`
3. Définition de `self.db_path = "justradamus_intelligence.db"`
4. Création du répertoire de rapports si inexistant
5. Initialisation de la base SQLite via `_init_db()`

#### 6.1.3 `_init_db()`

Crée la table `findings` si elle n'existe pas :

```sql
CREATE TABLE IF NOT EXISTS findings (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    target    TEXT,
    category  TEXT,
    data      TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

#### 6.1.4 `save_finding(category, data)`

- Sérialise `data` (dict) en JSON indenté dans `Justradamus_Reports/{category}_{target}.json`
- Insère un enregistrement dans `findings` avec la cible, la catégorie et les données en JSON
- Retourne le chemin du fichier JSON créé

Nom de fichier généré : `{category}_{target}.json`  
Exemples : `Email_Intel_exemple@gmail.com.json`, `Phone_Intel_33620446928.json`

#### 6.1.5 `display_results(category, data)`

Génère un tableau Rich (`Table`) avec deux colonnes (clé / valeur) :
- Les valeurs de type `list` sont affichées en chaîne jointe par `, `
- Le tableau est encapsulé dans un `Panel` avec bordure bleue
- Le titre du panel affiche la catégorie en magenta

### 6.2 Scanner OSINT générique — `OSINTScanner`

**Fichier** : `core/scanner.py`

#### 6.2.1 Rôle

Classe utilitaire indépendante (ne hérite pas de `JustradamusModule`) pour le scan de présence de pseudonymes à partir d'une base de données externe (`data/sites.json`). Elle est l'équivalent d'un moteur Sherlock simplifié.

#### 6.2.2 Chargement de la base de données

La méthode `_load_services()` charge `data/sites.json` depuis le répertoire racine du projet. Le fichier est attendu au format :

```json
{
    "NomDuSite": {
        "url": "https://exemple.com/{}",
        "error_body": "texte signalant absence de profil"
    }
}
```

- `{}` est le placeholder pour le nom d'utilisateur
- `error_body` peut être `null` si l'absence ne peut être détectée via le corps de la réponse

#### 6.2.3 `check_site(name, info)`

- Formate l'URL avec `self.target`
- Requête GET avec headers aléatoires, proxy et timeout configurés
- Vérifie HTTP 200
- Si `error_body` est défini et trouvé dans la réponse (case-insensitive), retourne `False`
- Retourne un tuple `(name, url, True/False/None)` — `None` signifie erreur/timeout

#### 6.2.4 `start_scan()`

Exécution parallèle via `ThreadPoolExecutor(max_workers=20)`. Tous les sites de la base sont testés simultanément (dans la limite de 20 threads). Retourne la liste complète des tuples `(name, url, status)`.

**Note** : Cette classe existe dans le code mais n'est pas directement appelée depuis le menu principal. Elle sert de base générique extensible pour le scan de username — le module `UsernameOSINT` implémente sa propre logique de vérification en dur.

### 6.3 Configuration globale — `config.py`

**Fichier** : `core/config.py`

#### 6.3.1 Constantes

| Constante | Valeur | Usage |
|---|---|---|
| `TIMEOUT` | `10` | Timeout en secondes pour toutes les requêtes HTTP |

#### 6.3.2 `USER_AGENTS`

Liste de 3 User-Agent strings représentant Chrome sur Windows, Linux et macOS. Cette rotation vise à réduire la détection de scraping par les serveurs cibles.

#### 6.3.3 `get_random_header()`

Retourne un dictionnaire d'en-têtes HTTP complets avec :
- User-Agent aléatoire parmi les 3 disponibles
- `Accept` : valeurs standard de navigateur
- `Accept-Language` : `en-US,en;q=0.5`
- `DNT: 1` (Do Not Track)
- `Connection: keep-alive`

---

## 7. Utilitaires d'affichage

**Fichier** : `utile/display.py`  
**Dépendances** : `rich`, `urllib.request`, `socket`

### 7.1 Thème personnalisé Rich

Un `Theme` personnalisé est défini avec les correspondances sémantiques suivantes :

| Alias | Style Rich | Usage |
|---|---|---|
| `info` | `bold cyan` | Messages informatifs |
| `warning` | `bold orange1` | Avertissements, scans en cours |
| `error` | `bold red` | Erreurs, cibles non trouvées |
| `success` | `bold green` | Cibles trouvées |
| `target` | `bold magenta` | Affichage de la cible |

La console globale `console` est instanciée une seule fois et importée par tous les modules.

### 7.2 `get_public_ip()`

Interroge `https://api4.ipify.org` avec un timeout de 3 secondes. Retourne l'adresse IPv4 publique de la machine ou `"Indisponible"` en cas d'échec.

### 7.3 `get_hostname()`

Retourne le nom d'hôte de la machine via `socket.gethostname()`.

### 7.4 `print_banner()`

Affiche au lancement un `Panel.fit` Rich avec :
- Titre : `🦊 Watch Fox 🦊`
- Sous-titre : `Intelligence & Investigation Framework`
- Ligne de séparation
- Nom d'hôte de la machine
- IP publique de la machine

Bordure de couleur `orange1`.

---

## 8. Persistance des données

### 8.1 Fichiers JSON

Chaque scan produit un fichier JSON unique dans `Justradamus_Reports/` avec le naming convention :

```
{Category}_{target}.json
```

Les fichiers sont encodés en UTF-8 avec indentation de 4 espaces. `ensure_ascii=False` garantit la bonne représentation des caractères accentués.

### 8.2 Base SQLite — `justradamus_intelligence.db`

Base de données relationnelle centralisée. Toutes les sauvegardes de tous les modules y sont inscrites.

**Schéma de la table `findings`** :

| Colonne | Type | Description |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Identifiant unique |
| `target` | `TEXT` | Cible investigée |
| `category` | `TEXT` | Type de scan (Email_Intel, Phone_Intel, etc.) |
| `data` | `TEXT` | Données JSON sérialisées |
| `timestamp` | `DATETIME DEFAULT CURRENT_TIMESTAMP` | Horodatage automatique |

**Requêtes d'accès courantes** :

```sql
-- Tous les scans sur une cible donnée
SELECT category, data, timestamp FROM findings WHERE target = 'exemple@gmail.com';

-- Historique complet trié par date
SELECT * FROM findings ORDER BY timestamp DESC;

-- Comptage par type de scan
SELECT category, COUNT(*) FROM findings GROUP BY category;
```

### 8.3 Absence de chiffrement

Les données stockées (JSON et SQLite) ne sont pas chiffrées. Toute donnée sensible collectée (présence sur plateformes adultes, numéros de téléphone, fuites de données) est stockée en clair sur le disque. **C'est un risque à prendre en compte dans un contexte professionnel.**

---

## 9. Interfaces d'entrée/sortie

### 9.1 Interface CLI

**Fichier** : `main.py`

Point d'entrée unique. Implémente une **boucle infinie** (`while True`) contenant la fonction `main()`. La sortie normale se fait via `sys.exit()` (choix 0) ou `KeyboardInterrupt` (Ctrl+C).

#### 9.1.1 Menu principal

```
🦊 Watch Fox 🦊
Intelligence & Investigation Framework
──────────────────────────────────────────
Device : [hostname]
IPv4   : [ip publique]

1. 📱 Téléphone
2. 🌐 Web/IP
3. 📧 Email
4. 👤 Pseudo/Username
5. 📡 Scan Réseau (Ports)
0. Quitter

➤ Choix :
➤ Cible (IP/Domain/Email/etc) :
```

#### 9.1.2 Saisie

La cible est saisie via `console.input()` (Rich). Elle est passée directement au constructeur du module correspondant sans validation préalable — les modules gèrent eux-mêmes les erreurs de format.

### 9.2 Sorties

| Type de sortie | Format | Destination |
|---|---|---|
| Affichage temps réel | Rich coloré (tables, panels) | Terminal stdout |
| Rapport par scan | JSON (UTF-8, indenté) | `Justradamus_Reports/` |
| Historique global | SQLite | `justradamus_intelligence.db` |

---

## 10. Dépendances et environnement

### 10.1 Environnement d'exécution

| Critère | Valeur |
|---|---|
| Langage | Python 3.13 (fichiers `.pyc` présents confirment la version) |
| OS testés | Linux (Ubuntu), Windows (compatible), macOS (compatible) |
| Privilèges requis | Standard (root requis uniquement pour Traceroute) |

### 10.2 Dépendances Python (à installer via pip)

| Package | Version minimale recommandée | Usage |
|---|---|---|
| `requests` | ≥ 2.28 | Requêtes HTTP dans mail.py, pseudo.py, scanner.py |
| `rich` | ≥ 13.0 | Affichage terminal coloré (console, tables, panels) |
| `phonenumbers` | ≥ 8.13 | Parsing et géolocalisation numéros de téléphone |
| `dnspython` | ≥ 2.3 | Résolution DNS MX dans mail.py |

### 10.3 Bibliothèques standard utilisées

`socket`, `json`, `os`, `hashlib`, `sqlite3`, `threading`, `ipaddress`, `time`, `struct`, `re`, `urllib.request`, `urllib.parse`, `concurrent.futures`, `sys`, `random`

### 10.4 Fichier `requirements.txt` recommandé

```
requests>=2.28.0
rich>=13.0.0
phonenumbers>=8.13.0
dnspython>=2.3.0
```

### 10.5 Fichier `data/sites.json` manquant

Le fichier `data/sites.json` est référencé dans `core/scanner.py` mais **absent du zip fourni**. La classe `OSINTScanner` affichera un avertissement et retournera un dictionnaire vide si ce fichier est absent. Ce fichier est nécessaire pour exploiter le scanner générique de pseudonymes.

---

## 11. Exigences non fonctionnelles

### 11.1 Performance

| Critère | Valeur cible | Situation actuelle |
|---|---|---|
| Scan Username (57 sites) | < 90 secondes | Séquentiel, ~57 × TIMEOUT max |
| Scan Email (15 checks) | < 30 secondes | Séquentiel |
| Scan réseau (plage /24, 8 ports) | < 120 secondes | Parallèle (lots 100 threads) |
| Réponse affichage (bannière) | < 5 secondes | Dépend d'ipify.org |

### 11.2 Fiabilité

- Toutes les requêtes HTTP sont enveloppées dans des blocs `try/except` — aucun crash dû à un timeout ou une erreur réseau.
- Les erreurs de résolution DNS sont capturées et affichées proprement.
- La création de la base SQLite est idempotente (`CREATE TABLE IF NOT EXISTS`).

### 11.3 Maintenabilité

- Architecture modulaire : chaque module est indépendant et peut être modifié sans impacter les autres.
- La classe de base centralise les fonctions communes, évitant la duplication de code.
- Les nouvelles plateformes dans `UsernameOSINT` peuvent être ajoutées avec une seule ligne (`check_site(...)`) sans modifier la logique de scan.
- La base `data/sites.json` permet d'ajouter des sites à `OSINTScanner` sans toucher au code Python.

### 11.4 Sécurité opérationnelle

- Rotation de User-Agent pour réduire l'empreinte de scraping.
- Support proxy natif sur tous les modules (paramètre `proxy` non encore exposé dans le menu CLI).
- Pas de stockage de credentials ou de clés API dans le code source.
- **Absence de chiffrement des données locales** : risque si la machine de l'opérateur est compromise.

### 11.5 Portabilité

- Compatibilité multi-OS via Python pur et bibliothèques cross-platform.
- Aucune dépendance à des outils système externes (nmap, curl, etc.) — exception : Traceroute nécessite les raw sockets ICMP.
- Les chemins de fichiers utilisent `os.path.join` et `os.path.dirname` pour la portabilité.

---

## 12. Limites actuelles et dette technique

### 12.1 Bugs connus / comportements non idéaux

| Identifiant | Module | Description | Sévérité |
|---|---|---|---|
| BUG-01 | `PhonyNode` | `self.proxy` n'est pas propagé depuis `JustradamusModule` (commentaire dans `mail.py` signale ce pattern comme fix) — risque d'`AttributeError` si `proxy` est utilisé | Moyen |
| BUG-02 | `UsernameOSINT` | Les requêtes sont séquentielles, pas parallèles — scan lent sur 57 sites | Performance |
| BUG-03 | `NetworkScanner` | Aucune sauvegarde des résultats (JSON/SQLite) contrairement aux autres modules | Fonctionnel |
| BUG-04 | `Traceroute` | Classe implémentée mais non exposée dans le menu | Fonctionnel |
| BUG-05 | `EmailOSINT` | Faux positifs élevés sur les réseaux sociaux via username extrait de l'email | Qualité données |
| BUG-06 | `OSINTScanner` | Le fichier `data/sites.json` n'est pas fourni dans le projet | Fonctionnel |
| BUG-07 | `main.py` | Aucune validation de format de la cible avant instanciation du module | Robustesse |
| BUG-08 | `WebScanner` | Ports ouverts stockés en chaîne dans le JSON au lieu d'un tableau | Cohérence données |

### 12.2 Dette technique structurelle

- **Pas de tests unitaires** : aucun fichier de test n'est présent dans le projet.
- **Pas de `requirements.txt`** ni de `setup.py` / `pyproject.toml` : installation manuelle des dépendances nécessaire.
- **Pas de logging** : les erreurs sont affichées dans la console mais non journalisées dans un fichier de log.
- **Pas de configuration externalisée** : le timeout, les ports à scanner, et les User-Agents sont codés en dur dans `config.py`.
- **Proxy non exposé dans l'UI** : le paramètre existe dans la logique mais l'utilisateur ne peut pas le configurer depuis le menu.
- **`Spam_Score` non implémenté** dans `PhonyNode` : champ placeholder.

---

## 13. Pistes d'évolution

### 13.1 Court terme (v1.1)

| Évolution | Priorité | Effort estimé |
|---|---|---|
| Ajouter `requirements.txt` et documentation d'installation | P0 | Faible |
| Exposer le proxy dans le menu CLI (option supplémentaire) | P0 | Faible |
| Paralléliser les requêtes dans `UsernameOSINT` avec `ThreadPoolExecutor` | P1 | Moyen |
| Ajouter la sauvegarde JSON/SQLite dans `NetworkScanner` | P1 | Faible |
| Exposer `Traceroute` dans le menu | P1 | Faible |
| Fournir un `data/sites.json` de base pour `OSINTScanner` | P1 | Moyen |
| Validation de format de la cible dans `main.py` | P1 | Faible |
| Intégrer une API de réputation téléphonique (ex: Numverify) | P2 | Moyen |

### 13.2 Moyen terme (v2.0)

| Évolution | Priorité | Description |
|---|---|---|
| Export multi-format | P1 | CSV, PDF, HTML en plus du JSON |
| Mode batch / fichier de cibles | P1 | Lire une liste de cibles depuis un fichier texte |
| Interface de configuration | P1 | Fichier `config.yaml` pour personnaliser timeout, ports, proxy |
| Clés API optionnelles | P2 | HIBP, Numverify, Shodan — avec fallback gracieux si absent |
| Analyse TLS/SSL | P2 | Certificat, expiration, suite de chiffrement |
| Analyse d'en-têtes HTTP | P2 | Server, X-Powered-By, CSP, HSTS |
| Détection de sous-domaines | P2 | Brute-force + APIs (crt.sh, dnsdumpster) |
| Reverse DNS | P2 | PTR records pour les IPs scannées |
| Mode silencieux / JSON-only | P3 | Output machine-readable uniquement |
| Tests unitaires | P1 | Couverture des modules principaux |

### 13.3 Long terme (v3.0+)

| Évolution | Description |
|---|---|
| Interface web (Flask/FastAPI) | Dashboard de résultats, historique visuel |
| API REST | Intégration dans d'autres outils de sécurité |
| Corrélation multi-cibles | Graphe de relations entre les findings (email → pseudo → IP) |
| Chiffrement des données locales | Protection de la base SQLite avec SQLCipher |
| Plugin système | Architecture de plugins pour ajouter des modules tiers |
| Intégration Maltego | Export de graphes d'entités pour Maltego |
| Mode daemon / scheduling | Surveillance continue et alertes sur changements |

---

## 14. Glossaire

| Terme | Définition |
|---|---|
| **OSINT** | Open Source Intelligence — collecte de renseignements à partir de sources publiques |
| **CLI** | Command Line Interface — interface en ligne de commande |
| **TTL** | Time To Live — compteur de sauts dans un paquet IP, utilisé en traceroute |
| **ICMP** | Internet Control Message Protocol — protocole de contrôle réseau (ping, traceroute) |
| **Raw Socket** | Socket de bas niveau permettant la manipulation directe des paquets IP |
| **CIDR** | Classless Inter-Domain Routing — notation de plage réseau (ex: 192.168.1.0/24) |
| **MX Record** | Mail Exchanger — enregistrement DNS indiquant les serveurs mail d'un domaine |
| **HIBP** | Have I Been Pwned — service de détection de fuites de données |
| **Rich** | Bibliothèque Python pour le rendu de texte formaté dans le terminal |
| **ThreadPoolExecutor** | Gestionnaire de pool de threads Python (concurrent.futures) |
| **User-Agent** | En-tête HTTP identifiant le client effectuant la requête |
| **Faux positif** | Résultat incorrect indiquant la présence d'un profil qui n'existe pas |
| **ASN** | Autonomous System Number — identifiant d'un réseau internet administré |
| **ISP** | Internet Service Provider — fournisseur d'accès internet |
| **PTR** | Pointer Record — enregistrement DNS pour la résolution inverse (IP → nom) |
| **SQLite** | Base de données relationnelle légère stockée dans un fichier |
| **Proxy** | Serveur intermédiaire pour anonymiser ou router les requêtes |
| **Nitter** | Instance alternative open source de Twitter/X, sans authentification requise |

---
