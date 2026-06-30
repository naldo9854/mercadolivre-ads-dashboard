# =============================================================================
# SCRIPT DE VERIFICAÇÃO E MOCK DO DASHBOARD VISUAL MULTICONTAS (ENTERPRISE)
# =============================================================================

import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

print("⌛ Gerando dados de mock Enterprise...")

# ── CONFIGURAÇÃO DE MULTIPLAS LOJAS ──────────────────────────────────────────
mock_lojas = [
    {
        "id": 1,
        "name": "Alfa Eletro - Loja Oficial",
        "verba_mensal": 6000.0,
        "gasto_ciclo": 2100.0,
        "campanhas": [
            {"name": "Campanha - Smart TV 4K", "status": "active", "budget": 100.0, "clicks": 120, "cost": 85.50, "total_amount": 1200.00, "direct_sales": 2, "indirect_sales": 1, "roas_7d": 14.04, "vendas_7d": 15},
            {"name": "Campanha - Smartphone Pro", "status": "active", "budget": 150.0, "clicks": 210, "cost": 140.20, "total_amount": 2500.00, "direct_sales": 4, "indirect_sales": 1, "roas_7d": 17.83, "vendas_7d": 25},
            {"name": "Campanha - Fone de Ouvido Bluetooth", "status": "active", "budget": 80.0, "clicks": 95, "cost": 45.10, "total_amount": 290.00, "direct_sales": 1, "indirect_sales": 0, "roas_7d": 6.43, "vendas_7d": 8},
            {"name": "Campanha - Carregador Rápido", "status": "active", "budget": 50.0, "clicks": 62, "cost": 22.80, "total_amount": 99.00, "direct_sales": 0, "indirect_sales": 0, "roas_7d": 4.34, "vendas_7d": 4},
            {"name": "Campanha - Suporte Celular Articulado", "status": "active", "budget": 30.0, "clicks": 55, "cost": 15.30, "total_amount": 0.00, "direct_sales": 0, "indirect_sales": 0, "roas_7d": 6.50, "vendas_7d": 6},
            {"name": "Campanha - Capinha Traseira Silicone", "status": "paused", "budget": 20.0, "clicks": 0, "cost": 0.00, "total_amount": 0.00, "direct_sales": 0, "indirect_sales": 0, "roas_7d": None, "vendas_7d": 0},
        ]
    },
    {
        "id": 2,
        "name": "Beta Calçados & Moda",
        "verba_mensal": 5000.0,
        "gasto_ciclo": 4200.0, # Ritmo acelerado!
        "campanhas": [
            {"name": "Campanha - Tênis Corrida Premium", "status": "active", "budget": 120.0, "clicks": 340, "cost": 290.40, "total_amount": 850.00, "direct_sales": 5, "indirect_sales": 2, "roas_7d": 2.93, "vendas_7d": 12}, # Estourado! (ROAS < 4x)
            {"name": "Campanha - Sandália Salto Bloco", "status": "active", "budget": 80.0, "clicks": 180, "cost": 120.00, "total_amount": 420.00, "direct_sales": 2, "indirect_sales": 1, "roas_7d": 3.50, "vendas_7d": 7},  # Estourado! (ROAS < 4x)
            {"name": "Campanha - Chinelo Slides Nuvem", "status": "active", "budget": 50.0, "clicks": 70, "cost": 35.50, "total_amount": 110.00, "direct_sales": 0, "indirect_sales": 0, "roas_7d": 3.10, "vendas_7d": 3},   # Estourado! (ROAS < 4x)
        ]
    },
    {
        "id": 3,
        "name": "Gama Auto Peças",
        "verba_mensal": 8000.0,
        "gasto_ciclo": 1200.0, # Ritmo lento!
        "campanhas": [
            {"name": "Campanha - Kit Coxim Suspensão S10", "status": "active", "budget": 200.0, "clicks": 140, "cost": 90.00, "total_amount": 1950.00, "direct_sales": 8, "indirect_sales": 4, "roas_7d": 21.67, "vendas_7d": 20},  # Saudável!
            {"name": "Campanha - Sensor Pressão Pneus", "status": "active", "budget": 100.0, "clicks": 80, "cost": 45.00, "total_amount": 780.00, "direct_sales": 3, "indirect_sales": 1, "roas_7d": 17.33, "vendas_7d": 10},    # Saudável!
            {"name": "Campanha - Pastilha de Freio Cerâmica", "status": "active", "budget": 120.0, "clicks": 110, "cost": 65.00, "total_amount": 920.00, "direct_sales": 4, "indirect_sales": 0, "roas_7d": 14.15, "vendas_7d": 11},  # Saudável!
        ]
    }
]

DIA_FECHAMENTO = 17

# ── SIMULAÇÃO DO CICLO FINANCEIRO ─────────────────────────────
hoje = datetime(2026, 6, 26, 12, 0, 0)
dia_hoje = hoje.day

if dia_hoje <= DIA_FECHAMENTO:
    mes_ini = hoje.month - 1 if hoje.month > 1 else 12
    ano_ini = hoje.year      if hoje.month > 1 else hoje.year - 1
    inicio  = datetime(ano_ini, mes_ini, DIA_FECHAMENTO + 1)
    fim     = datetime(hoje.year, hoje.month, DIA_FECHAMENTO)
else:
    inicio  = datetime(hoje.year, hoje.month, DIA_FECHAMENTO + 1)
    mes_fim = hoje.month + 1 if hoje.month < 12 else 1
    ano_fim = hoje.year      if hoje.month < 12 else hoje.year + 1
    fim     = datetime(ano_fim, mes_fim, DIA_FECHAMENTO)

dias_totais    = (fim - inicio).days + 1
dias_passados  = max((hoje - inicio).days + 1, 1)
dias_restantes = max((fim - hoje).days, 1)
percentual_tempo = (dias_passados / dias_totais * 100)

lojas_dados = []

# ── LOOP DE PROCESSAMENTO DAS CONTAS ──────────────────────────────────────────
for loja in mock_lojas:
    VERBA_MENSAL = loja["verba_mensal"]
    gasto_ciclo = loja["gasto_ciclo"]
    advertiser_nome = loja["name"]
    store_id = loja["id"]
    
    verba_restante = VERBA_MENSAL - gasto_ciclo
    verba_diaria_resto = verba_restante / dias_restantes
    percentual_gasto = min((gasto_ciclo / VERBA_MENSAL * 100) if VERBA_MENSAL > 0 else 0, 100)
    
    # Lógica de Pacing
    if percentual_gasto > percentual_tempo + 15:
        ritmo_label, ritmo_cor, ritmo_bg = "ACELERADO", "#ef4444", "#fef2f2"
        ritmo_desc = "Consumo acelerado de verba (+15% acima do cronograma). Recomenda-se reduzir orçamentos diários para evitar interrupção antes do fecho do ciclo."
        ritmo_badge = '<span class="status-dot-badge pace-acelerado"><span class="dot"></span>ACELERADO</span>'
    elif percentual_gasto < percentual_tempo - 15:
        ritmo_label, ritmo_cor, ritmo_bg = "LENTO", "#eab308", "#fefce8"
        ritmo_desc = "Consumo abaixo do cronograma (-15% abaixo do tempo decorrido). Recomenda-se aumentar verbas diárias para aproveitar a tração comercial disponível."
        ritmo_badge = '<span class="status-dot-badge pace-lento"><span class="dot"></span>LENTO</span>'
    else:
        ritmo_label, ritmo_cor, ritmo_bg = "SAUDÁVEL", "#10b981", "#f0fdf4"
        ritmo_desc = "Consumo perfeitamente calibrado com o cronograma. Projeção ideal para fechamento de 100% da verba sem sobras ou escassez."
        ritmo_badge = '<span class="status-dot-badge pace-saudavel"><span class="dot"></span>SAUDÁVEL</span>'

    # Processar campanhas
    registros = []
    for c in loja["campanhas"]:
        nome = c["name"]
        status = c["status"]
        orcamento = c["budget"]
        cliques = c["clicks"]
        custo = c["cost"]
        receita = c["total_amount"]
        vendas = c["direct_sales"] + c["indirect_sales"]
        roas_7d = c["roas_7d"]
        vendas_7d = c.get("vendas_7d", 0)
        
        if custo > 0:
            roas_ontem = receita / custo
        elif receita > 0:
            roas_ontem = 9999.0 # Infinito (excelente)
        else:
            roas_ontem = None
        
        # Regras de recomendação baseadas em ROAS 7D e SUSTENTAR
        if vendas == 0 and roas_7d is not None and roas_7d > 5.0:
            rec = "🛡️ SUSTENTAR (Bom histórico)"
        elif cliques > 50 and vendas == 0:
            rec = "⚠️ ALERTA CONVERSÃO"
        elif roas_7d is None:
            rec = "👀 ACOMPANHAR" if cliques > 0 else "👻 FANTASMA"
        elif roas_7d > 8.0:
            rec = "🚀 AUMENTAR ORÇAMENTO"
        elif roas_7d >= 4.0:
            rec = "✅ MANTER"
        else:
            rec = "🔴 REDUZIR / PAUSAR"
            
        registros.append({
            "Campanha": nome, "Status": status, "Orç. Atual": f"R$ {orcamento:,.2f}",
            "Custo": round(custo, 2), "Receita": round(receita, 2),
            "Cliques": cliques, "Vendas": vendas,
            "ROAS Ontem": f"{roas_ontem:.2f}x" if roas_ontem is not None and roas_ontem != 9999.0 else "Excelente" if roas_ontem == 9999.0 else "N/A",
            "ROAS 7D": f"{roas_7d:.2f}x" if roas_7d is not None and roas_7d != 9999.0 else "Excelente" if roas_7d == 9999.0 else "N/A",
            "Recomendação": rec, "Sugestão/dia": "—",
            "_roas_ontem": roas_ontem, "_roas_7d": roas_7d, "_vendas_7d": vendas_7d, "_vendas": vendas, "_custo": custo, "_receita": receita,
        })
        
    # Calcular Métricas Consolidadas de Ontem
    total_custo_d1   = sum(r["_custo"] for r in registros)
    total_receita_d1 = sum(r["_receita"] for r in registros)
    total_vendas_d1  = sum(r["_vendas"] for r in registros)
    total_cliques_d1 = sum(r["Cliques"] for r in registros)
    
    roas_geral = total_receita_d1 / total_custo_d1 if total_custo_d1 > 0 else 0.0
    conversion_rate = (total_vendas_d1 / total_cliques_d1) * 100 if total_cliques_d1 > 0 else 0.0
    cpc_medio = total_custo_d1 / total_cliques_d1 if total_cliques_d1 > 0 else 0.0
    
    # Calcular ROAS 7D Geral da Loja
    roas_7d_list = [c["roas_7d"] for c in loja["campanhas"] if c["roas_7d"] is not None]
    roas_geral_7d = sum(roas_7d_list) / len(roas_7d_list) if roas_7d_list else None
    
    # ── ALOCAÇÃO DINÂMICA DE VERBA COM TETO DE RISCO (MAX/MIN CAP) ──
    sugestoes_grafico = []
    elegiveis = []
    
    for r in registros:
        r["Sugestão/dia"] = "—"
        r["_sugestao_val"] = 0.0
        rec = r["Recomendação"]
        
        # Definir pesos por Tiers de Performance e ROAS/Vendas 7D
        roas_val = r["_roas_7d"] if r["_roas_7d"] is not None else 0.0
        if roas_val == 9999.0:
            roas_val = 50.0
        vendas_7d_val = r["_vendas_7d"] if r.get("_vendas_7d") is not None else 0
        
        weight_score = (roas_val * 2.0) + vendas_7d_val
        
        if "AUMENTAR" in rec or "SUSTENTAR" in rec:
            weight = weight_score * 3.0
            eligible = True
        elif "MANTER" in rec:
            weight = weight_score * 1.5
            eligible = True
        elif "ACOMPANHAR" in rec:
            weight = weight_score * 0.5
            eligible = True
        else:
            weight = 0.0
            eligible = False
            
        if eligible:
            elegiveis.append({"reg": r, "weight": weight, "allocated": 0.0, "capped": False})
            
    n_elegiveis = len(elegiveis)
    if n_elegiveis > 0 and verba_diaria_resto > 0:
        # Definir Piso Mínimo (Min Cap) de R$ 10,00 (ou o máximo possível se a verba for muito baixa)
        piso = 10.0
        if verba_diaria_resto < piso * n_elegiveis:
            piso = verba_diaria_resto / n_elegiveis
            
        for el in elegiveis:
            el["allocated"] = piso
            
        verba_restante_dist = verba_diaria_resto - (piso * n_elegiveis)
        max_cap = 0.35 * verba_diaria_resto
        
        # Loop de distribuição dos pesos com respeito ao teto (Max Cap)
        while verba_restante_dist > 0.01:
            ativas = [el for el in elegiveis if not el["capped"] and el["weight"] > 0]
            if not ativas:
                break
                
            soma_pesos = sum(el["weight"] for el in ativas)
            if soma_pesos == 0:
                break
                
            excesso_verba = 0.0
            distribuido_nesta_rodada = False
            
            for el in ativas:
                share = (el["weight"] / soma_pesos) * verba_restante_dist
                novo_valor = el["allocated"] + share
                if novo_valor >= max_cap:
                    excesso_verba += (novo_valor - max_cap)
                    el["allocated"] = max_cap
                    el["capped"] = True
                    distribuido_nesta_rodada = True
                else:
                    el["allocated"] = novo_valor
                    distribuido_nesta_rodada = True
                    
            if not distribuido_nesta_rodada:
                break
            verba_restante_dist = excesso_verba
            
        # Normalização Matemática e Ajuste Fino de Centavos
        soma_sugerido = sum(el["allocated"] for el in elegiveis)
        diferenca = verba_diaria_resto - soma_sugerido
        
        if abs(diferenca) > 0.01:
            candidatos = [el for el in elegiveis if not el["capped"]]
            if not candidatos:
                candidatos = elegiveis
            candidatos[0]["allocated"] += diferenca
            
        # Gravar de volta nos registros da campanha e no gráfico
        for el in elegiveis:
            val = el["allocated"]
            el["reg"]["Sugestão/dia"] = f"R$ {val:,.2f}"
            el["reg"]["_sugestao_val"] = val
            sugestoes_grafico.append({"Campanha": el["reg"]["Campanha"], "Valor": round(val, 2)})

    # Plotly donut chart
    grafico_html = ""
    if sugestoes_grafico:
        df_graf = pd.DataFrame(sugestoes_grafico).sort_values("Valor", ascending=False).head(10)
        cores = ["#2563eb", "#10b981", "#6366f1", "#f59e0b", "#06b6d4", "#ec4899", "#8b5cf6", "#f43f5e", "#14b8a6", "#64748b"]
        
        fig = go.Figure(data=[go.Pie(
            labels=df_graf["Campanha"], 
            values=df_graf["Valor"], 
            hole=0.65, 
            domain=dict(x=[0, 0.72]),
            marker=dict(colors=cores, line=dict(color="#ffffff", width=2)), 
            textinfo="percent", 
            hovertemplate="<b>%{label}</b><br>Sugerido: R$ %{value:,.2f}<br>%{percent}<extra></extra>"
        )])
        fig.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            showlegend=True, 
            legend=dict(
                font=dict(family='Inter, sans-serif', size=10, color="#475569"), 
                bgcolor='rgba(0,0,0,0)',
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=0.75
            ), 
            font=dict(family='Inter, sans-serif'), 
            annotations=[dict(
                text=f"<span style='font-size:9px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;'>Distribuição</span><br><b style='font-size:16px;color:#0f172a;font-weight:800;'>R$ {verba_diaria_resto:,.0f}</b><br><span style='font-size:9px;color:#64748b;'>/dia</span>", 
                x=0.36, 
                y=0.5, 
                showarrow=False
            )], 
            height=340
        )
        grafico_html = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})

    # Badge colors for recommendations
    def cor_rec(rec):
        if "AUMENTAR"   in rec: return "#f0fdf4", "#16a34a", "#bbf7d0"
        if "MANTER"     in rec: return "#eff6ff", "#1d4ed8", "#bfdbfe"
        if "REDUZIR"    in rec: return "#fef2f2", "#ef4444", "#fecaca"
        if "ALERTA"     in rec: return "#fffbeb", "#d97706", "#fde68a"
        if "ACOMPANHAR" in rec: return "#f0f9ff", "#0284c7", "#b3e5fc"
        if "FANTASMA"   in rec: return "#f8fafc", "#64748b", "#e2e8f0"
        if "SUSTENTAR"  in rec: return "#f5f3ff", "#7c3aed", "#ddd6fe"
        return "#f8fafc", "#475569", "#e2e8f0"

    # Mini cards recommendations count
    dist_rec = {}
    for r in registros:
        dist_rec[r["Recomendação"]] = dist_rec.get(r["Recomendação"], 0) + 1
        
    mini_cards = ""
    for label in ["🚀 AUMENTAR ORÇAMENTO", "✅ MANTER", "🛡️ SUSTENTAR (Bom histórico)", "👀 ACOMPANHAR", "👻 FANTASMA", "🔴 REDUZIR / PAUSAR", "⚠️ ALERTA CONVERSÃO"]:
        if label in dist_rec:
            bg, fg, border = cor_rec(label)
            clean_label = label.replace("🚀 ", "").replace("✅ ", "").replace("🛡️ ", "").replace("👀 ", "").replace("👻 ", "").replace("🔴 ", "").replace("⚠️ ", "")
            mini_cards += f"""
            <div class='mini-card' style='background:{bg};border:1px solid {border};border-left:3px solid {fg};'>
                <span class='mini-val' style='color:{fg};'>{dist_rec[label]}</span>
                <span class='mini-lbl' style='color:{fg};'>{clean_label}</span>
            </div>
            """

    # Linhas da tabela
    linhas_tabela = ""
    for r in registros:
        bg, fg, border = cor_rec(r["Recomendação"])
        status_class = "status-active" if r["Status"].upper() == "ACTIVE" else "status-paused"
        status_label = "ATIVO" if r["Status"].upper() == "ACTIVE" else "PAUSADO"
        linhas_tabela += f"""
        <tr>
            <td class='td-camp'>{r['Campanha']}</td>
            <td style='text-align:center;'>
                <span class="status-dot-badge {status_class}">
                    <span class="dot"></span>{status_label}
                </span>
            </td>
            <td style='text-align:right;'>{r['Orç. Atual']}</td>
            <td style='text-align:right;'>R$ {r['Custo']:,.2f}</td>
            <td style='text-align:right;'>R$ {r['Receita']:,.2f}</td>
            <td style='text-align:right;'>{r['Cliques']:,}</td>
            <td style='text-align:right;'>{r['Vendas']}</td>
            <td style='text-align:right; font-weight: 500;'>{r['ACOS Ontem']}</td>
            <td style='text-align:right; font-weight: 600; color: #1e3a8a;'>{r['ACOS 7D']}</td>
            <td style='text-align:center;'><span class='rec-badge' style='background:{bg};color:{fg};border:1px solid {border};'>{r['Recomendação']}</span></td>
            <td style='text-align:right; font-weight:700; color:#2563eb;'>{r['Sugestão/dia']}</td>
        </tr>
        """

    lojas_dados.append({
        "id": store_id,
        "name": advertiser_nome,
        "gasto_ontem": total_custo_d1,
        "receita_ontem": total_receita_d1,
        "acos_7d_geral": acos_geral_7d,
        "ritmo": ritmo_label,
        "ritmo_cor": ritmo_cor,
        "ritmo_bg": ritmo_bg,
        "ritmo_badge": ritmo_badge,
        "ritmo_desc": ritmo_desc,
        "verba_mensal": VERBA_MENSAL,
        "gasto_ciclo": gasto_ciclo,
        "verba_restante": verba_restante,
        "verba_diaria_resto": verba_diaria_resto,
        "percentual_gasto": percentual_gasto,
        "roas_geral": roas_geral,
        "acos_geral_str": acos_geral_str,
        "conversion_rate": conversion_rate,
        "cpc_medio": cpc_medio,
        "total_vendas_d1": total_vendas_d1,
        "total_cliques_d1": total_cliques_d1,
        "linhas_tabela": linhas_tabela,
        "mini_cards": mini_cards,
        "grafico_html": grafico_html
    })

# ── RENDERIZAR O HTML DE EXPORTAÇÃO MASTER ───────────────────────────────────
lojas_cards_html = ""
tabs_buttons_html = ""
tabs_contents_html = ""

for i, loja in enumerate(lojas_dados):
    acos_7d_val = loja["acos_7d_geral"]
    if acos_7d_val is None:
        border_class = "card-neutral"
        status_farol = "⚪ Sem Dados"
        acos_text = "N/A"
    elif acos_7d_val > 25.0:
        border_class = "card-blown"
        status_farol = "🔴 Estourado"
        acos_text = f"{acos_7d_val:.2f}%"
    else:
        border_class = "card-healthy"
        status_farol = "🟢 Saudável"
        acos_text = f"{acos_7d_val:.2f}%"

    # Card do painel global (Farol)
    lojas_cards_html += f"""
    <div class="client-summary-card {border_class}">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="client-name">{loja['name']}</span>
        <span style="font-size:10px; font-weight:700; text-transform:uppercase;">{status_farol}</span>
      </div>
      <div style="margin-top:6px; display:flex; flex-direction:column; gap:4px;">
        <div class="client-metric-row">
          <span>Gasto Ontem:</span>
          <span class="client-metric-val">R$ {loja['gasto_ontem']:,.2f}</span>
        </div>
        <div class="client-metric-row">
          <span>ACOS 7D Geral:</span>
          <span class="client-metric-val" style="color: {'#ef4444' if acos_7d_val and acos_7d_val > 25.0 else '#10b981' if acos_7d_val else '#64748b'};">{acos_text}</span>
        </div>
        <div class="client-metric-row">
          <span>Pacing:</span>
          <span>{loja['ritmo_badge']}</span>
        </div>
      </div>
    </div>
    """

    # Abas dinâmicas
    active_class = "active" if i == 0 else ""
    tabs_buttons_html += f"""
    <button class="tab-btn {active_class}" onclick="openTab(event, 'client-details-{loja['id']}')">
      {loja['name']}
    </button>
    """

    display_style = "block" if i == 0 else "none"
    tabs_contents_html += f"""
    <div id="client-details-{loja['id']}" class="tab-details-content {active_class}" style="display: {display_style};">
      
      <!-- KPI Grid para esta loja -->
      <div class="kpi-grid" style="margin-bottom: 24px;">
        
        <!-- Card 1 -->
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Orçamento vs Gasto</span>
            <div class="kpi-icon-container">
                <svg viewBox="0 0 24 24" fill="none" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
            </div>
          </div>
          <div>
            <div class="kpi-value" style="color: {loja['ritmo_cor']};">R$ {loja['gasto_ciclo']:,.2f}</div>
            <div class="kpi-meta">de R$ {loja['verba_mensal']:,.2f} Planejados</div>
          </div>
          <div>
            <div class="custom-progress">
              <div class="custom-progress-fill" style="width: {loja['percentual_gasto']:.1f}%; background-color: {loja['ritmo_cor']};"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 10px; color:#94a3b8; font-weight:500;">
              <span>Consumido: {loja['percentual_gasto']:.1f}%</span>
            </div>
          </div>
        </div>
        
        <!-- Card 2 -->
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Saldo Restante</span>
            <div class="kpi-icon-container">
                <svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
            </div>
          </div>
          <div>
            <div class="kpi-value" style="color: #10b981;">R$ {loja['verba_restante']:,.2f}</div>
            <div class="kpi-meta">Saldo para {dias_restantes} dias de ciclo</div>
          </div>
          <div>
            <div class="custom-progress">
              <div class="custom-progress-fill" style="width: {percentual_tempo:.1f}%; background-color: #3b82f6;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 10px; color:#94a3b8; font-weight:500;">
              <span>Tempo decorrido: {percentual_tempo:.1f}% ({dias_passados}/{dias_totais} d)</span>
            </div>
          </div>
        </div>
        
        <!-- Card 3 -->
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Ritmo de Consumo</span>
            <div class="kpi-icon-container">
                <svg viewBox="0 0 24 24" fill="none" stroke="#eab308" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
            </div>
          </div>
          <div style="margin-top: 10px;">
            {loja['ritmo_badge']}
            <p style="font-size: 11px; color: #64748b; margin-top: 10px; line-height: 1.4;">
              {loja['ritmo_desc']}
            </p>
          </div>
          <div style="font-size: 10px; color: #94a3b8; font-weight: 500; border-top: 1px solid #f1f5f9; padding-top: 6px; margin-top: 6px;">
            Desvio Cronograma: {loja['percentual_gasto'] - percentual_tempo:+.1f}%
          </div>
        </div>
        
        <!-- Card 4 -->
        <div class="kpi-card">
          <div class="kpi-header">
            <span class="kpi-title">Métricas de Ontem</span>
            <div class="kpi-icon-container">
                <svg viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path></svg>
            </div>
          </div>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <div style="display: flex; gap: 16px; align-items: center; margin-top: 6px;">
              <div>
                <span style="font-size: 8px; font-weight:700; color:#64748b; text-transform:uppercase;">ROAS Ontem</span>
                <div style="font-size: 20px; font-weight:700; color:#2563eb;">{loja['roas_geral']:.2f}x</div>
              </div>
              <div style="border-left: 1px solid #e2e8f0; padding-left: 16px;">
                <span style="font-size: 8px; font-weight:700; color:#64748b; text-transform:uppercase;">ACOS Ontem</span>
                <div style="font-size: 20px; font-weight:700; color:#0f172a;">{loja['acos_geral_str']}</div>
              </div>
            </div>
          </div>
          <div style="font-size: 10px; color: #64748b; border-top: 1px solid #f1f5f9; padding-top: 6px; margin-top: 6px; display: flex; justify-content: space-between;">
            <span>Custo: R$ {loja['gasto_ontem']:,.2f}</span>
            <span>Fat: R$ {loja['receita_ontem']:,.2f}</span>
          </div>
        </div>
        
      </div>

      <!-- Mini Badges de Recomendação -->
      <div class="mini-grid" style="margin-bottom: 24px;">
        {loja['mini_cards']}
      </div>

      <!-- Layout de Duas Colunas (Gráfico e Funil) -->
      <div class="two-col-layout" style="margin-bottom: 24px;">
        <div class="content-card">
          <div class="section-headline">🍩 Distribuição de Verba Diária</div>
          <div class="section-subtext">Alocação recomendada proporcional à performance (ACOS + volume de vendas)</div>
          {loja['grafico_html'] if loja['grafico_html'] else '<p style="color:#94a3b8;font-size:12px;padding:60px 0;text-align:center">Nenhuma campanha com dados de ontem.</p>'}
        </div>
        
        <div class="content-card">
          <div class="section-headline">📈 Diagnóstico do Funil (Ontem)</div>
          <div class="section-subtext">Visão consolidada do comportamento das campanhas no dia anterior</div>
          
          <div class="yesterday-highlights">
            <div class="highlight-box">
              <span class="h-lbl">ROAS Geral</span>
              <span class="h-val">{loja['roas_geral']:.2f}x</span>
            </div>
            <div class="highlight-box" style="border-left: 1px solid #e2e8f0;">
              <span class="h-lbl">Conversão Geral</span>
              <span class="h-val" style="color:#10b981;">{loja['conversion_rate']:.2f}%</span>
            </div>
          </div>
          
          <div class="metric-row">
            <span class="m-label">💰 Investimento Ontem</span>
            <span class="m-value">R$ {loja['gasto_ontem']:,.2f}</span>
          </div>
          <div class="metric-row">
            <span class="m-label">📦 Faturamento Ontem</span>
            <span class="m-value">R$ {loja['receita_ontem']:,.2f}</span>
          </div>
          <div class="metric-row">
            <span class="m-label">🛒 Vendas Concluídas</span>
            <span class="m-value">{loja['total_vendas_d1']}</span>
          </div>
          <div class="metric-row">
            <span class="m-label">🖱️ Cliques Acumulados</span>
            <span class="m-value">{loja['total_cliques_d1']:,}</span>
          </div>
          <div class="metric-row">
            <span class="m-label">🎯 CPC Médio Real</span>
            <span class="m-value">R$ {loja['cpc_medio']:,.2f}</span>
          </div>
          <div class="metric-row">
            <span class="m-label">⚡ Verba Diária Sugerida (Média)</span>
            <span class="m-value" style="color:#2563eb;">R$ {loja['verba_diaria_resto']:,.2f}</span>
          </div>
        </div>
      </div>

      <!-- Tabela de Diagnóstico Completo -->
      <div class="content-card table-card" style="margin-bottom: 24px;">
        <div class="section-headline">🎯 Diagnóstico Individual de Campanhas — {loja['name']}</div>
        <div class="section-subtext">Auditoria individualizada de ontem com recomendações baseadas em ACOS e volume comercial</div>
        
        <table>
          <thead>
            <tr>
              <th>Campanha</th>
              <th style="text-align:center;">Status</th>
              <th style="text-align:right;">Orç. Atual</th>
              <th style="text-align:right;">Custo</th>
              <th style="text-align:right;">Receita</th>
              <th style="text-align:right;">Cliques</th>
              <th style="text-align:right;">Vendas</th>
              <th style="text-align:right;">ACOS Ontem</th>
              <th style="text-align:right;">ACOS 7D</th>
              <th style="text-align:center;">Ação Recomendada</th>
              <th style="text-align:right;">Sugestão/Dia</th>
            </tr>
          </thead>
          <tbody>
            {loja['linhas_tabela']}
          </tbody>
        </table>
      </div>

    </div>
    """

html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Product Ads Enterprise Intelligence - Master Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a; padding: 24px; }}
  
  /* Wrapper do dashboard */
  .dashboard-container {{ max-width: 1240px; margin: 0 auto; display: flex; flex-direction: column; gap: 24px; }}
  
  /* Header Premium Estilo Agência */
  .header-banner {{ 
    background-color: #0f172a; 
    border-radius: 12px; 
    padding: 24px 32px; 
    display: flex; 
    justify-content: space-between; 
    align-items: center; 
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border: 1px solid #1e293b;
  }}
  .header-title-section h1 {{ color: #ffffff; font-size: 22px; font-weight: 700; letter-spacing: -0.025em; }}
  .header-title-section p {{ color: #94a3b8; font-size: 12px; margin-top: 4px; font-weight: 400; }}
  .header-date-badge {{ 
    background: #1e293b; 
    border: 1px solid #334155; 
    color: #cbd5e1; 
    padding: 6px 14px; 
    border-radius: 6px; 
    font-size: 11px; 
    font-weight: 500;
    letter-spacing: 0.02em;
  }}

  /* Painel Global de Clientes (Enterprise) */
  .enterprise-title {{
    font-size: 14px;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .enterprise-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 20px;
    margin-bottom: 16px;
  }}
  .client-summary-card {{
    background: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: all 0.2s ease;
  }}
  .client-summary-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px -2px rgba(0,0,0,0.05);
  }}
  .card-healthy {{
    border: 1.5px solid #86efac !important;
    background-color: #f0fdf4;
  }}
  .card-blown {{
    border: 1.5px solid #fca5a5 !important;
    background-color: #fef2f2;
  }}
  .card-neutral {{
    border: 1.5px solid #cbd5e1 !important;
    background-color: #ffffff;
  }}
  .client-name {{
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
  }}
  .client-metric-row {{
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #475569;
    padding: 2px 0;
  }}
  .client-metric-val {{
    font-weight: 700;
    color: #0f172a;
  }}

  /* Navegação de Abas */
  .enterprise-tabs-nav {{
    display: flex;
    gap: 8px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 2px;
    margin-top: 12px;
    flex-wrap: wrap;
  }}
  .tab-btn {{
    background: none;
    border: none;
    padding: 10px 20px;
    border-radius: 6px 6px 0 0;
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    color: #64748b;
    border-bottom: 3px solid transparent;
    transition: all 0.15s ease;
  }}
  .tab-btn:hover {{
    color: #0f172a;
    background-color: #f1f5f9;
  }}
  .tab-btn.active {{
    color: #2563eb;
    border-bottom-color: #2563eb;
    font-weight: 700;
  }}
  .tab-details-content {{
    display: none;
    margin-top: 24px;
  }}
  .tab-details-content.active {{
    display: block;
  }}

  /* KPI Grid */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }}
  .kpi-card {{ 
    background: #ffffff; 
    border: 1px solid #e2e8f0; 
    border-radius: 12px; 
    padding: 22px; 
    box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 160px;
    position: relative;
  }}
  .kpi-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
  .kpi-title {{ font-size: 10px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }}
  .kpi-icon-container {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    background-color: #f1f5f9;
  }}
  .kpi-icon-container svg {{ width: 16px; height: 16px; }}
  
  .kpi-value {{ font-size: 22px; font-weight: 700; color: #0f172a; margin-top: 10px; margin-bottom: 4px; letter-spacing: -0.02em; }}
  .kpi-meta {{ font-size: 11px; color: #64748b; font-weight: 400; }}
  
  /* Progress Bars */
  .custom-progress {{ width: 100%; height: 5px; background-color: #f1f5f9; border-radius: 9999px; margin: 12px 0 6px 0; overflow: hidden; }}
  .custom-progress-fill {{ height: 100%; border-radius: 9999px; }}
  
  /* Badges de Status */
  .status-dot-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    border-width: 1px;
    border-style: solid;
  }}
  .status-dot-badge .dot {{ width: 5px; height: 5px; border-radius: 50%; }}
  
  /* Variações de Pacing */
  .pace-acelerado {{ background-color: #fef2f2; color: #ef4444; border-color: #fecaca; }}
  .pace-acelerado .dot {{ background-color: #ef4444; }}
  .pace-lento {{ background-color: #fefce8; color: #b45309; border-color: #fde68a; }}
  .pace-lento .dot {{ background-color: #b45309; }}
  .pace-saudavel {{ background-color: #f0fdf4; color: #16a34a; border-color: #bbf7d0; }}
  .pace-saudavel .dot {{ background-color: #16a34a; }}

  /* Variações de Status de Campanha */
  .status-active {{ background-color: #f0fdf4; color: #16a34a; border-color: #bbf7d0; }}
  .status-active .dot {{ background-color: #16a34a; }}
  .status-paused {{ background-color: #f8fafc; color: #64748b; border-color: #e2e8f0; }}
  .status-paused .dot {{ background-color: #64748b; }}
  
  /* Mini Grid de Recomendações */
  .mini-grid {{ display: flex; gap: 10px; flex-wrap: wrap; }}
  .mini-card {{ 
    border-radius: 6px; 
    padding: 10px 14px; 
    display: flex; 
    align-items: center; 
    gap: 8px; 
    min-width: 150px;
    box-shadow: 0 1px 1px rgba(0,0,0,0.01);
  }}
  .mini-val {{ font-size: 16px; font-weight: 700; }}
  .mini-lbl {{ font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.02em; }}

  /* Estrutura de Duas Colunas */
  .two-col-layout {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  .content-card {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.01);
  }}
  .section-headline {{ font-size: 12px; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }}
  .section-subtext {{ font-size: 11px; color: #94a3b8; margin-bottom: 18px; }}
  
  /* Ontem Detalhes */
  .metric-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f1f5f9;
  }}
  .metric-row:last-child {{ border-bottom: none; }}
  .m-label {{ font-size: 12px; color: #475569; font-weight: 500; }}
  .m-value {{ font-size: 13px; font-weight: 700; color: #0f172a; }}

  /* Grid ontem de destaque */
  .yesterday-highlights {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 14px;
  }}
  .highlight-box {{ display: flex; flex-direction: column; align-items: center; text-align: center; }}
  .h-lbl {{ font-size: 9px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px; }}
  .h-val {{ font-size: 20px; font-weight: 700; color: #2563eb; }}

  /* Tabela de Campanhas */
  .table-card {{ overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; }}
  thead th {{
    background-color: #f8fafc;
    color: #475569;
    font-weight: 600;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 12px 14px;
    border-bottom: 2px solid #e2e8f0;
  }}
  tbody tr {{ transition: background-color 0.1s ease; }}
  tbody tr:hover {{ background-color: #f8fafc; }}
  tbody td {{ padding: 12px 14px; border-bottom: 1px solid #f1f5f9; color: #334155; vertical-align: middle; }}
  .td-camp {{ font-weight: 600; color: #0f172a; max-width: 240px; word-wrap: break-word; }}
  
  .rec-badge {{
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    white-space: nowrap;
  }}

  /* Footer */
  .dashboard-footer {{
    text-align: center;
    font-size: 11px;
    color: #94a3b8;
    padding: 20px 0;
    border-top: 1px solid #e2e8f0;
    margin-top: 10px;
  }}
</style>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>

<div class="dashboard-container">
  
  <!-- Banner do Cabeçalho -->
  <div class="header-banner">
    <div class="header-title-section">
      <h1>📊 Product Ads Enterprise Intelligence</h1>
      <p>Painel de Monitoramento Consolidado Multicontas (Agência Master)</p>
    </div>
    <div class="header-date-badge">
      📅 Gerado em {hoje.strftime('%d/%m/%Y às %H:%M')}
    </div>
  </div>

  <!-- Painel Global (Farol de Alertas) -->
  <div>
    <h2 class="enterprise-title">🌐 Visão Consolidada de Clientes (Farol de Alertas)</h2>
    <div class="enterprise-grid">
      {lojas_cards_html}
    </div>
  </div>

  <!-- Navegação de Abas Detalhadas -->
  <div>
    <h2 class="enterprise-title" style="margin-top: 20px;">🔍 Diagnóstico Individual por Cliente</h2>
    <div class="enterprise-tabs-nav">
      {tabs_buttons_html}
    </div>
  </div>

  <!-- Conteúdo de Abas Detalhadas -->
  <div class="enterprise-tabs-content">
    {tabs_contents_html}
  </div>
  
  <!-- Footer do Dashboard -->
  <div class="dashboard-footer">
    Product Ads Enterprise Master Intelligence · Desenvolvido para Gestão Multi-Contas · {hoje.strftime('%d/%m/%Y %H:%M:%S')}
  </div>
  
</div>

<script>
  function openTab(evt, tabId) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tab-details-content");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
      tabcontent[i].classList.remove("active");
    }
    tablinks = document.getElementsByClassName("tab-btn");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].classList.remove("active");
    }
    document.getElementById(tabId).style.display = "block";
    document.getElementById(tabId).classList.add("active");
    evt.currentTarget.classList.add("active");
  }
</script>

</body>
</html>
"""

# Salva o arquivo localmente para visualização
output_path = os.path.join(os.path.dirname(__file__), "dashboard_preview.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard Enterprise gerado com sucesso em: {output_path}")
