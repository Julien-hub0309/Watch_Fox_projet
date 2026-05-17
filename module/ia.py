import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
from utile.display import console

class IADetector:
    def __init__(self, file_path):
        self.file_path = file_path.replace('"', '').replace("'", "")
        self.model_id = "gpt2"

    def calculate_ai_score(self, text, model, tokenizer):
        encodings = tokenizer(text, return_tensors="pt")
        max_length = model.config.n_positions
        stride = 512
        nlls = []
        for i in range(0, encodings.input_ids.size(1), stride):
            begin_loc = max(i + stride - max_length, 0)
            end_loc = min(i + stride, encodings.input_ids.size(1))
            trg_len = end_loc - i
            input_ids = encodings.input_ids[:, begin_loc:end_loc]
            target_ids = input_ids.clone()
            target_ids[:, :-trg_len] = -100
            with torch.no_grad():
                outputs = model(input_ids, labels=target_ids)
                neg_log_likelihood = outputs.loss * trg_len
            nlls.append(neg_log_likelihood)
        return torch.exp(torch.stack(nlls).sum() / end_loc).item()

    def run_scan(self):
        if not os.path.exists(self.file_path):
            console.print("[bold red]❌ Fichier introuvable.[/bold red]")
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            console.print(f"[bold red]❌ Erreur de lecture : {e}[/bold red]")
            return

        console.print("[bold blue][*] Chargement du modèle et analyse...[/bold blue]")
        model = GPT2LMHeadModel.from_pretrained(self.model_id)
        tokenizer = GPT2Tokenizer.from_pretrained(self.model_id)
        score = self.calculate_ai_score(content, model, tokenizer)

        console.print(f"\n[bold]Score de Perplexité : {score:.2f}[/bold]")
        if score < 25:
            console.print("[bold red]VERDICT : Très probablement généré par une IA.[/bold red]")
        elif score < 50:
            console.print("[bold yellow]VERDICT : Suspicions de contenu assisté par IA.[/bold yellow]")
        else:
            console.print("[bold green]VERDICT : Probablement écrit par un humain.[/bold green]")