import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import json
import io
import os
import flet as ft


# Se quiser usar o arquivo local que criamos no Passo 1:
ARQUIVO_DADOS = "zzz_agents.json"
ARQUIVO_PROGRESSO = "progresso.json"

class AppZZZPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZZZ Task Tracker")
        self.geometry("850x600")
        self.configure(bg="#121212")

        self.db_personagens = {}
        self.progresso_salvo = {}

        self.carregar_dados_e_progresso()

    def carregar_dados_e_progresso(self):
        # 1. Carrega a base de dados dos personagens
        if os.path.exists(ARQUIVO_DADOS):
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                self.db_personagens = json.load(f)
        else:
            # Caso o arquivo não exista, cria um exemplo básico para não quebrar
            messagebox.showwarning("Aviso", f"Arquivo {ARQUIVO_DADOS} não encontrado! Criando um modelo básico.")
            self.db_personagens = {"Exemplo": {"url_imagem": "", "elemento": "Nenhum", "habilidades": [], "prioridades": []}}

        # 2. Carrega o progresso antigo do usuário (se existir)
        if os.path.exists(ARQUIVO_PROGRESSO):
            with open(ARQUIVO_PROGRESSO, "r", encoding="utf-8") as f:
                self.progresso_salvo = json.load(f)
        else:
            self.progresso_salvo = {}

        # Garante que todo personagem do banco tenha um espaço no progresso
        for nome in self.db_personagens:
            if nome not in self.progresso_salvo:
                self.progresso_salvo[nome] = {}

        self.criar_interface()
        if self.db_personagens:
            self.carregar_personagem(list(self.db_personagens.keys())[0])

    def criar_interface(self):
        # --- TOPO ---
        frame_topo = tk.Frame(self, bg="#1a1a1a", height=60)
        frame_topo.pack(side="top", fill="x", padx=15, pady=(15, 0))
        
        lbl_selecao = tk.Label(frame_topo, text="Selecionar Agente:", font=("Helvetica", 12, "bold"), bg="#1a1a1a", fg="#ffffff")
        lbl_selecao.pack(side="left", padx=15, pady=15)
        
        self.combo_personagens = ttk.Combobox(frame_topo, values=list(self.db_personagens.keys()), state="readonly", font=("Helvetica", 11))
        self.combo_personagens.current(0)
        self.combo_personagens.pack(side="left", padx=10, pady=15)
        self.combo_personagens.bind("<<ComboboxSelected>>", lambda e: self.carregar_personagem(self.combo_personagens.get()))

        # --- CORPO ---
        frame_corpo = tk.Frame(self, bg="#121212")
        frame_corpo.pack(fill="both", expand=True)

        self.frame_esquerda = tk.Frame(frame_corpo, bg="#1a1a1a", bd=2, relief="groove")
        self.frame_esquerda.pack(side="left", fill="both", expand=True, padx=15, pady=15)

        self.frame_direita = tk.Frame(frame_corpo, bg="#121212")
        self.frame_direita.pack(side="right", fill="both", expand=True, padx=15, pady=15)

    def carregar_personagem(self, nome_agente):
        for w in self.frame_esquerda.winfo_children(): w.destroy()
        for w in self.frame_direita.winfo_children(): w.destroy()

        dados = self.db_personagens[nome_agente]

        # Cabeçalho
        tk.Label(self.frame_esquerda, text=nome_agente, font=("Helvetica", 18, "bold"), bg="#1a1a1a", fg="#ffcc00").pack(pady=5)
        tk.Label(self.frame_esquerda, text=dados["elemento"], font=("Helvetica", 10, "italic"), bg="#1a1a1a", fg="#00ffcc").pack(pady=(0, 10))

        # Imagem via URL
        lbl_foto = tk.Label(self.frame_esquerda, bg="#1a1a1a")
        lbl_foto.pack(pady=5)
        
        if dados.get("url_imagem"):
            try:
                res = requests.get(dados["url_imagem"], timeout=5)
                img = Image.open(io.BytesIO(res.content)).resize((160, 160), Image.Resampling.LANCZOS)
                foto_tk = ImageTk.PhotoImage(img)
                lbl_foto.config(image=foto_tk)
                lbl_foto.image = foto_tk
            except:
                lbl_foto.config(text="[ Erro ao carregar imagem da Web ]", fg="red", bg="#1a1a1a")
        else:
            lbl_foto.config(text="[ Sem imagem definida ]", fg="#888888", bg="#1a1a1a")

        # Habilidades
        tk.Label(self.frame_esquerda, text="Habilidades: ", font=("Helvetica", 12, "bold"), bg="#1a1a1a", fg="#ffffff").pack(pady=(15, 5), anchor="w", padx=15)
        for hab in dados["habilidades"]:
            tk.Label(self.frame_esquerda, text=f"• {hab}", font=("Helvetica", 10), bg="#1a1a1a", fg="#cccccc", anchor="w").pack(fill="x", padx=20, pady=2)

        # Prioridades (Checklist)
        tk.Label(self.frame_direita, text="Ordem de Prioridade & Progresso", font=("Helvetica", 14, "bold"), bg="#121212", fg="#ffffff").pack(pady=10, anchor="w")
        
        # Estilo Checkbox
        style = ttk.Style()
        style.configure("TCheckbutton", font=("Helvetica", 11), background="#121212", foreground="#ffffff")

        self.checkbox_vars = []
        for tarefa in dados["prioridades"]:
            estado_anterior = self.progresso_salvo[nome_agente].get(tarefa, False)
            var = tk.BooleanVar(value=estado_anterior)
            
            chk = ttk.Checkbutton(
                self.frame_direita, text=tarefa, variable=var, style="TCheckbutton",
                command=lambda v=var, t=tarefa, n=nome_agente: self.salvar_progresso_local(n, t, v)
            )
            chk.pack(anchor="w", pady=10, fill="x")
            self.checkbox_vars.append(var)

        # Divisor visual básico
        canvas_linha = tk.Canvas(self.frame_direita, height=2, bg="#ffcc00", highlightthickness=0)
        canvas_linha.pack(fill="x", pady=15)

        #Status dos Discos (Main e Sub)
        frame_discos = tk.Frame(self.frame_direita, bg="#1a1a1a", bd=1, relief="solid")
        frame_discos.pack(fill="both", expand=True, pady=5)

        #Discos Main Stats
        if "Discos Main stats" in dados:
            tk.Label(frame_discos, text="🎯 Status Principais (Slots 4, 5, 6):", font=("Helvetica", 11, "bold"), bg="#1a1a1a", fg="#00ffcc").pack(pady=(8, 2), anchor="w", padx=10)
            for stat in dados["Discos Main stats"]: 
                tk.Label(frame_discos, text=f"  {stat}", font=("Helvetica", 10), bg="#1a1a1a", fg="#ffffff", anchor="w").pack(fill="x", padx=10)
        

        #Discos Sub-stats
        if "Discos Sub-stats" in dados:
            tk.Label(frame_discos, text="🔍 Sub-status Desejados (Sub-stats):", font=("Helvetica", 11, "bold"), bg="#1a1a1a", fg="#00ffcc").pack(pady=(10, 2), anchor="w", padx=10)
            # Transforma a lista de sub-stats numa única linha separada por vírgulas
            sub_stats_linha = ", ".join(dados["Discos Sub-stats"])
            tk.Label(frame_discos, text=f"  {sub_stats_linha}", font=("Helvetica", 10), bg="#1a1a1a", fg="#e6e6e6", anchor="w").pack(fill="x", padx=10, pady=(0, 8))

        # Divisor visual básico
        canvas_linha = tk.Canvas(self.frame_direita, height=2, bg="#ffcc00", highlightthickness=0)
        canvas_linha.pack(fill="x", pady=15)

        #Sets discos
        frame_discos_set = tk.Frame(self.frame_direita, bg="#1a1a1a", bd=1, relief="solid")
        frame_discos_set.pack(fill="both", expand=True, pady=5)
        if "Discos" in dados:
            tk.Label(frame_discos, text="💽 Set de Discos", font=("Helvetica", 11, "bold"), bg="#1a1a1a", fg="#00ffcc").pack(pady=(10, 2), anchor="w", padx=10)
             # Transforma a lista de sub-stats numa única linha separada por vírgulas
            Discos_set_linha = ", ".join(dados["Discos"])
            tk.Label(frame_discos, text=f"  {Discos_set_linha}", font=("Helvetica", 10), bg="#1a1a1a", fg="#e6e6e6", anchor="w").pack(fill="x", padx=10, pady=(0, 8))
    

    #Salvamento local
    def salvar_progresso_local(self, nome_agente, tarefa, var):
        # Atualiza a memória
        self.progresso_salvo[nome_agente][tarefa] = var.get()
        # Salva direto no arquivo físico json
        with open(ARQUIVO_PROGRESSO, "w", encoding="utf-8") as f:
            json.dump(self.progresso_salvo, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    app = AppZZZPro()
    app.mainloop()
    