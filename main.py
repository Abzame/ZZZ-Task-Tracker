import flet as ft
import requests
import json
import os

# Configurações de arquivos
ARQUIVO_DADOS = "zzz_agents.json"
ARQUIVO_PROGRESSO = "progresso.json"

class ZZZTrackerMobile:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "ZZZ Task Tracker"
        self.page.bgcolor = "#121212"  
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.scroll = ft.ScrollMode.AUTO  

        self.db_personagens = {}
        self.progresso_salvo = {}
        
        # --- CORREÇÃO AQUI: Mudado para "contain" em string pura ---
        self.img_agente = ft.Image(width=140, height=140, fit="contain")
        
        # --- CORREÇÃO AQUI: Mudado para "bold" em string pura ---
        self.lbl_nome = ft.Text(size=24, weight="bold", color="#ffcc00")
        self.lbl_elemento = ft.Text(size=14, color="#00ffcc", italic=True)
        
        self.col_habilidades = ft.Column()
        self.col_prioridade_hab = ft.Column()
        self.col_checklist = ft.Column()
        self.col_main_stats = ft.Column()
        self.col_sub_stats = ft.Column()

        self.carregar_dados()

    def carregar_dados(self):
        if os.path.exists(ARQUIVO_DADOS):
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                self.db_personagens = json.load(f)
        else:
            self.db_personagens = {"Sem Agentes": {"url_imagem": "", "elemento": "Nenhum", "habilidades": [], "prioridades": []}}

        if os.path.exists(ARQUIVO_PROGRESSO):
            with open(ARQUIVO_PROGRESSO, "r", encoding="utf-8") as f:
                self.progresso_salvo = json.load(f)
        else:
            self.progresso_salvo = {}

        for nome in self.db_personagens:
            if nome not in self.progresso_salvo:
                self.progresso_salvo[nome] = {}

        self.montar_interface()

    def montar_interface(self):
        self.dropdown = ft.Dropdown(
            label="Selecionar Agente",
            label_style=ft.TextStyle(color="#ffffff"),
            border_color="#ffcc00",
            color="#ffffff",
            focused_border_color="#ffcc00",
            options=[ft.dropdown.Option(nome) for nome in self.db_personagens.keys()],
            value=list(self.db_personagens.keys())[0],
            on_change=self.ao_mudar_agente
        )

        card_info = ft.Container(
            content=ft.Column([
                ft.Row([self.img_agente, ft.Column([self.lbl_nome, self.lbl_elemento])], alignment=ft.MainAxisAlignment.START),
                ft.Divider(color="#333333"),
                self.col_prioridade_hab,
                ft.Text("📋 Habilidades:", size=16, weight="bold", color="#ffffff"),
                self.col_habilidades,
            ]),
            padding=15,
            bgcolor="#1a1a1a",
            border_radius=10,
            border=ft.border.all(1, "#333333")
        )

        card_discos = ft.Container(
            content=ft.Column([
                ft.Text("🎯 Status Principais (Slots 4, 5, 6):", size=16, weight="bold", color="#00ffcc"),
                self.col_main_stats,
                ft.Divider(color="#333333"),
                ft.Text("🔍 Sub-status Desejados:", size=16, weight="bold", color="#00ffcc"),
                self.col_sub_stats
            ]),
            padding=15,
            bgcolor="#1a1a1a",
            border_radius=10,
            border=ft.border.all(1, "#333333")
        )

        self.page.add(
            ft.Container(
                content=ft.Column([
                    self.dropdown,
                    card_info,
                    ft.Text("⚔️ Objetivos de Progressão:", size=18, weight="bold", color="#ffffff"),
                    self.col_checklist,
                    card_discos,
                    ft.Container(height=20) 
                ], spacing=15),
                padding=10
            )
        )
        
        self.atualizar_ecran_agente(self.dropdown.value)

    def atualizar_ecran_agente(self, nome_agente):
        dados = self.db_personagens[nome_agente]

        self.lbl_nome.value = nome_agente
        self.lbl_elemento.value = dados.get("elemento", "")
        self.img_agente.src = dados.get("url_imagem", "")

        self.col_prioridade_hab.controls.clear()
        if "prioridade de habiliade" in dados:
            ordem = " ➔ ".join(dados["prioridade de habiliade"])
            self.col_prioridade_hab.controls.append(ft.Text("🔸 Ordem de Upgrade:", weight="bold", color="#ffffff"))
            self.col_prioridade_hab.controls.append(ft.Text(ordem, color="#ff9900", size=13, weight="bold"))

        self.col_habilidades.controls.clear()
        for hab in dados.get("habilidades", []):
            self.col_habilidades.controls.append(ft.Text(f" • {hab}", color="#cccccc", size=13))

        self.col_checklist.controls.clear()
        for tarefa in dados.get("prioridades", []):
            estado_anterior = self.progresso_salvo[nome_agente].get(tarefa, False)
            
            chk = ft.Checkbox(
                label=tarefa,
                value=estado_anterior,
                active_color="#ffcc00",
                check_color="#000000",
                label_style=ft.TextStyle(color="#ffffff", size=14),
                on_change=lambda e, t=tarefa, n=nome_agente: self.salvar_progresso(n, t, e.control.value)
            )
            self.col_checklist.controls.append(chk)

        self.col_main_stats.controls.clear()
        for stat in dados.get("Discos Main stats", []):
            self.col_main_stats.controls.append(ft.Text(f" 💽 {stat}", color="#ffffff", size=13))

        self.col_sub_stats.controls.clear()
        if "Discos Sub-stats" in dados:
            sub_linha = ", ".join(dados["Discos Sub-stats"])
            self.col_sub_stats.controls.append(ft.Text(f" 📀 {sub_linha}", color="#e6e6e6", size=13))

        self.page.update()

# ... (todo o resto do teu código anterior mantém-se igual)

    def salvar_progresso(self, nome_agente, tarefa, valor):
        self.progresso_salvo[nome_agente][tarefa] = valor
        with open(ARQUIVO_PROGRESSO, "w", encoding="utf-8") as f:
            json.dump(self.progresso_salvo, f, indent=4, ensure_ascii=False)

# --- CORREÇÃO DO BLOCO DE INICIALIZAÇÃO AQUI ---
def main(page: ft.Page):
    ZZZTrackerMobile(page)

if __name__ == "__main__":
    ft.app(target=main)