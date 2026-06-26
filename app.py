# =============================================================================
# MONITOR DE PRODUCT ADS — MERCADO LIVRE (Versão Streamlit para Hospedagem Online)
# =============================================================================

import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from urllib.parse import urlencode

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Product Ads Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização básica do Streamlit para combinar com o visual de Agência
st.markdown("""
<style>
    .reportview-container {
        background: #f8fafc;
    }
    /* Ocultar elementos padrão do Streamlit para visual mais limpo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── INICIALIZAÇÃO DE ESTADOS NA SESSÃO ─────────────────────────
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "advertiser_lista" not in st.session_state:
    st.session_state.advertiser_lista = []
if "selected_advertiser" not in st.session_state:
    st.session_state.selected_advertiser = None

# ── BARRA LATERAL (CONFIGURAÇÃO E AUTENTICAÇÃO) ─────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
st.sidebar.title("Configurações & Acesso")
st.sidebar.markdown("---")

# inputs da verba e ciclo
verba_mensal_input = st.sidebar.number_input("📌 Verba Mensal (R$):", min_value=1.0, value=3000.0, step=100.0)
dia_fechamento_input = st.sidebar.slider("📌 Dia de Fechamento do Ciclo:", min_value=1, max_value=31, value=17)

st.sidebar.markdown("### Credenciais Mercado Livre")
client_id = st.sidebar.text_input("📌 CLIENT ID:", type="password")
client_secret = st.sidebar.text_input("📌 CLIENT SECRET:", type="password")
redirect_uri = "https://httpbin.org/get"

# Gerar URL de autorização se as chaves forem preenchidas
if client_id and client_secret:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
    }
    auth_url = "https://auth.mercadolivre.com.br/authorization?" + urlencode(params)
    
    st.sidebar.markdown(f"""
    <a href="{auth_url}" target="_blank" style="text-decoration:none;">
        <div style="background-color:#2563eb;color:white;padding:10px 14px;border-radius:6px;text-align:center;font-weight:600;margin-top:10px;font-size:13px;box-shadow:0 1px 2px rgba(0,0,0,0.05);">
            🔑 Passo 1: Autorizar no Mercado Livre
        </div>
    </a>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("<small style='color:#64748b;'>Clique no botão acima, faça login na sua conta do ML e copie o código 'code' que aparecer na URL da página de destino.</small>", unsafe_allow_html=True)
    
    auth_code = st.sidebar.text_input("📌 Cole aqui o Código de Autorização:", type="password")
    
    if st.sidebar.button("🔓 Passo 2: Conectar e Carregar Token") and auth_code:
        with st.spinner("Conectando à API do Mercado Livre..."):
            token_resp = requests.post("https://api.mercadolibre.com/oauth/token", data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": auth_code,
                "redirect_uri": redirect_uri,
            })
            
            if token_resp.status_code == 200:
                st.session_state.access_token = token_resp.json()["access_token"]
                st.sidebar.success("✅ Conectado com sucesso!")
            else:
                st.sidebar.error(f"❌ Erro na conexão: {token_resp.json().get('message', 'Erro desconhecido')}")

# Se já tivermos o token de acesso
if st.session_state.access_token:
    h1 = {"Authorization": f"Bearer {st.session_state.access_token}", "Api-Version": "1"}
    h2 = {"Authorization": f"Bearer {st.session_state.access_token}", "api-version": "2"}
    
    # Buscar lista de anunciantes
    if not st.session_state.advertiser_lista:
        adv_resp = requests.get("https://api.mercadolibre.com/advertising/advertisers?product_id=PADS", headers=h1)
        if adv_resp.status_code == 200:
            st.session_state.advertiser_lista = adv_resp.json().get("advertisers", [])
        else:
            st.session_state.access_token = None # Forçar reautenticação se expirar
            st.sidebar.error("Sua sessão expirou ou ocorreu um erro. Faça login novamente.")

    if st.session_state.advertiser_lista:
        advertisers_names = [a.get("advertiser_name", f"ID: {a.get('advertiser_id')}") for a in st.session_state.advertiser_lista]
        selecionado = st.sidebar.selectbox("📌 Selecione a Conta:", advertisers_names)
        
        idx = advertisers_names.index(selecionado)
        st.session_state.selected_advertiser = st.session_state.advertiser_lista[idx]
        
        st.sidebar.info(f"Anunciante ativo: {selecionado}")

# ── PAINEL CENTRAL (DASHBOARD VISUAL) ──────────────────────────
if not st.session_state.access_token or not st.session_state.selected_advertiser:
    # Tela de Onboarding (Boas-vindas)
    st.markdown("""
    <div style="max-width: 800px; margin: 80px auto; padding: 40px; background-color: white; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); text-align: center;">
        <img src="https://img.icons8.com/fluency/144/combo-chart.png" style="margin-bottom: 20px;"/>
        <h1 style="font-size: 28px; font-weight: 800; color: #0f172a; letter-spacing: -0.025em; margin-bottom: 10px;">Product Ads Intelligence</h1>
        <p style="color: #64748b; font-size: 15px; line-height: 1.6; margin-bottom: 24px;">
            Plataforma executiva para análise de ciclo financeiro dinâmico, monitoramento de performance com base em ACOS e ROAS e sugestão automática de distribuição de verbas no Mercado Livre.
        </p>
        <div style="background-color: #f8fafc; border-radius: 8px; padding: 16px; border: 1px solid #f1f5f9; text-align: left;">
            <h3 style="font-size: 14px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 8px; letter-spacing: 0.02em;">Como iniciar:</h3>
            <ol style="color: #64748b; font-size: 13px; padding-left: 20px; line-height: 1.8;">
                <li>Insira sua <b>Verba Mensal</b> e o <b>Dia de Fechamento</b> na barra lateral.</li>
                <li>Preencha seu <b>Client ID</b> e <b>Client Secret</b> (gerados no portal de desenvolvedores do Mercado Livre).</li>
                <li>Clique em <b>Autorizar</b> e insira o código retornado na URL.</li>
                <li>Conecte sua conta para gerar o dashboard interativo instantaneamente.</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Executar a lógica de negócios
    with st.spinner("Processando e renderizando dados do dashboard..."):
        advertiser_id = st.session_state.selected_advertiser["advertiser_id"]
        advertiser_nome = st.session_state.selected_advertiser.get("advertiser_name", "Minha Conta")
        
        # Lógica do ciclo financeiro
        hoje = datetime.now()
        dia_hoje = hoje.day

        if dia_hoje <= dia_fechamento_input:
            mes_ini = hoje.month - 1 if hoje.month > 1 else 12
            ano_ini = hoje.year      if hoje.month > 1 else hoje.year - 1
            inicio  = datetime(ano_ini, mes_ini, dia_fechamento_input + 1)
            fim     = datetime(hoje.year, hoje.month, dia_fechamento_input)
        else:
            inicio  = datetime(hoje.year, hoje.month, dia_fechamento_input + 1)
            mes_fim = hoje.month + 1 if hoje.month < 12 else 1
            ano_fim = hoje.year      if hoje.month < 12 else hoje.year + 1
            fim     = datetime(ano_fim, mes_fim, dia_fechamento_input)

        dias_totais    = (fim - inicio).days + 1
        dias_passados  = max((hoje - inicio).days + 1, 1)
        dias_restantes = max((fim - hoje).days, 1)
        data_ini_ciclo = inicio.strftime("%Y-%m-%d")
        data_hoje_str  = hoje.strftime("%Y-%m-%d")
        data_ontem_str = (hoje - timedelta(days=1)).strftime("%Y-%m-%d")

        # Buscar campanhas da API
        metricas = "clicks,prints,cost,acos,direct_units_quantity,indirect_units_quantity,total_amount,direct_amount,indirect_amount"

        def buscar_campanhas_api(data_ini, data_fim):
            resp = requests.get(
                f"https://api.mercadolibre.com/advertising/advertisers/{advertiser_id}/product_ads/campaigns"
                f"?date_from={data_ini}&date_to={data_fim}&metrics={metricas}&limit=100&offset=0",
                headers=h2
            )
            if resp.status_code != 200:
                return []
            return resp.json().get("results", [])

        camp_ciclo  = buscar_campanhas_api(data_ini_ciclo, data_hoje_str)
        gasto_ciclo = sum(float(c.get("metrics", {}).get("cost", 0) or 0) for c in camp_ciclo)
        camp_ontem  = buscar_campanhas_api(data_ontem_str, data_ontem_str)

        # Cálculos Financeiros
        verba_diaria_ref   = verba_mensal_input / dias_totais
        verba_restante     = verba_mensal_input - gasto_ciclo
        verba_diaria_resto = verba_restante / dias_restantes
        media_diaria_gasta = gasto_ciclo / dias_passados
        percentual_gasto   = min((gasto_ciclo / verba_mensal_input * 100) if verba_mensal_input > 0 else 0, 100)
        percentual_tempo   = (dias_passados / dias_totais * 100)

        if percentual_gasto > percentual_tempo + 15:
            ritmo_label, ritmo_cor, ritmo_bg = "ACELERADO", "#ef4444", "#fef2f2"
            ritmo_desc = "Consumo acelerado de verba (+15% acima do cronograma). Recomenda-se reduzir orçamentos diários para evitar interrupção antes do fecho do ciclo."
            ritmo_badge_html = f"""
            <span class="status-dot-badge pace-acelerado">
                <span class="dot"></span>ACELERADO
            </span>
            """
        elif percentual_gasto < percentual_tempo - 15:
            ritmo_label, ritmo_cor, ritmo_bg = "LENTO", "#eab308", "#fefce8"
            ritmo_desc = "Consumo abaixo do cronograma (-15% abaixo do tempo decorrido). Recomenda-se aumentar verbas diárias para aproveitar a tração comercial disponível."
            ritmo_badge_html = f"""
            <span class="status-dot-badge pace-lento">
                <span class="dot"></span>LENTO
            </span>
            """
        else:
            ritmo_label, ritmo_cor, ritmo_bg = "SAUDÁVEL", "#10b981", "#f0fdf4"
            ritmo_desc = "Consumo perfeitamente calibrado com o cronograma. Projeção ideal para fechamento de 100% da verba sem sobras ou escassez."
            ritmo_badge_html = f"""
            <span class="status-dot-badge pace-saudavel">
                <span class="dot"></span>SAUDÁVEL
            </span>
            """

        # Montar registros
        registros = []
        for c in camp_ontem:
            nome      = c.get("name", f"Campanha {c.get('id')}")
            status    = c.get("status", "")
            orcamento = float(c.get("budget", 0) or 0)
            m         = c.get("metrics", {})
            cliques   = int(m.get("clicks", 0) or 0)
            custo     = float(m.get("cost", 0) or 0)
            receita   = float(m.get("total_amount", 0) or 0)
            vendas    = int((m.get("direct_units_quantity", 0) or 0) + (m.get("indirect_units_quantity", 0) or 0))
            acos_api  = m.get("acos")

            if acos_api is not None and float(acos_api) > 0:
                acos = float(acos_api)
            elif receita > 0:
                acos = (custo / receita) * 100
            else:
                acos = None

            if cliques > 50 and vendas == 0:
                rec = "⚠️ ALERTA CONVERSÃO"
            elif acos is None:
                if cliques > 0:
                    rec = "👀 ACOMPANHAR"
                else:
                    rec = "👻 FANTASMA"
            elif acos < 10:
                rec = "🚀 AUMENTAR ORÇAMENTO"
            elif acos <= 25:
                rec = "✅ MANTER"
            else:
                rec = "🔴 REDUZIR / PAUSAR"

            registros.append({
                "Campanha": nome, "Status": status, "Orç. Atual": f"R$ {orcamento:,.2f}",
                "Custo": round(custo, 2), "Receita": round(receita, 2),
                "Cliques": cliques, "Vendas": vendas,
                "ACOS": f"{acos:.2f}%" if acos is not None else "N/A",
                "Recomendação": rec, "Sugestão/dia": "—",
                "_acos": acos, "_vendas": vendas, "_custo": custo, "_receita": receita,
            })

        # Distribuição de orçamento
        com_dados = [r for r in registros if r["_acos"] is not None or r["_vendas"] > 0]
        sugestoes_grafico = []

        if com_dados and verba_diaria_resto > 0:
            for r in com_dados:
                acos_val = r["_acos"] if r["_acos"] is not None else 999
                r["_score"] = (1 / (acos_val + 0.1)) * 10 + r["_vendas"]
            
            total_score = sum(r.get("_score", 0) for r in com_dados)
            
            for r in registros:
                if "_score" in r and total_score > 0:
                    val = r["_score"] / total_score * verba_diaria_resto
                    r["Sugestão/dia"] = f"R$ {val:,.2f}"
                    sugestoes_grafico.append({"Campanha": r["Campanha"], "Valor": round(val, 2)})

        total_custo_d1   = sum(r["_custo"] for r in registros)
        total_receita_d1 = sum(r["_receita"] for r in registros)
        total_vendas_d1  = sum(r["_vendas"] for r in registros)
        total_cliques_d1 = sum(r["Cliques"] for r in registros)

        roas_geral = total_receita_d1 / total_custo_d1 if total_custo_d1 > 0 else 0.0
        acos_geral_str = "{:.2f}%".format((total_custo_d1 / total_receita_d1) * 100) if total_receita_d1 > 0 else "0.00%"
        conversion_rate = (total_vendas_d1 / total_cliques_d1) * 100 if total_cliques_d1 > 0 else 0.0
        cpc_medio = total_custo_d1 / total_cliques_d1 if total_cliques_d1 > 0 else 0.0

        # Plotly Donut Chart
        grafico_html = ""
        if sugestoes_grafico:
            df_graf = pd.DataFrame(sugestoes_grafico).sort_values("Valor", ascending=False).head(10)
            cores = ["#2563eb", "#10b981", "#6366f1", "#f59e0b", "#06b6d4", "#ec4899", "#8b5cf6", "#f43f5e", "#14b8a6", "#64748b"]

            fig = go.Figure(data=[go.Pie(
                labels=df_graf["Campanha"], 
                values=df_graf["Valor"], 
                hole=0.65, 
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
                    font=dict(family='Inter, sans-serif', size=11, color="#475569"), 
                    bgcolor='rgba(0,0,0,0)',
                    orientation="h",
                    yanchor="bottom",
                    y=-0.22,
                    xanchor="center",
                    x=0.5
                ), 
                font=dict(family='Inter, sans-serif'), 
                annotations=[dict(
                    text=f"<span style='font-size:10px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;'>Distribuição</span><br><b style='font-size:18px;color:#0f172a;font-weight:800;'>R$ {verba_diaria_resto:,.0f}</b><br><span style='font-size:10px;color:#64748b;'>/dia</span>", 
                    x=0.5, 
                    y=0.5, 
                    showarrow=False
                )], 
                height=300
            )
            grafico_html = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})

        # Cores pastéis e de agência para as recomendações
        def cor_rec(rec):
            if "AUMENTAR"   in rec: return "#f0fdf4", "#16a34a", "#bbf7d0"
            if "MANTER"     in rec: return "#eff6ff", "#1d4ed8", "#bfdbfe"
            if "REDUZIR"    in rec: return "#fef2f2", "#ef4444", "#fecaca"
            if "ALERTA"     in rec: return "#fffbeb", "#d97706", "#fde68a"
            if "ACOMPANHAR" in rec: return "#f0f9ff", "#0284c7", "#b3e5fc"
            if "FANTASMA"   in rec: return "#f8fafc", "#64748b", "#e2e8f0"
            return "#f8fafc", "#475569", "#e2e8f0"

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
                <td style='text-align:right; font-weight: 600;'>{r['ACOS']}</td>
                <td style='text-align:center;'><span class='rec-badge' style='background:{bg};color:{fg};border:1px solid {border};'>{r['Recomendação']}</span></td>
                <td style='text-align:right; font-weight:700; color:#2563eb;'>{r['Sugestão/dia']}</td>
            </tr>
            """

        mini_cards = ""
        for label in ["🚀 AUMENTAR ORÇAMENTO", "✅ MANTER", "👀 ACOMPANHAR", "👻 FANTASMA", "🔴 REDUZIR / PAUSAR", "⚠️ ALERTA CONVERSÃO"]:
            if label in dist_rec:
                bg, fg, border = cor_rec(label)
                clean_label = label.replace("🚀 ", "").replace("✅ ", "").replace("👀 ", "").replace("👻 ", "").replace("🔴 ", "").replace("⚠️ ", "")
                mini_cards += f"""
                <div class='mini-card' style='background:{bg};border:1px solid {border};border-left:3px solid {fg};'>
                    <span class='mini-val' style='color:{fg};'>{dist_rec[label]}</span>
                    <span class='mini-lbl' style='color:{fg};'>{clean_label}</span>
                </div>
                """

        html = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
          
          /* Progress Bars Finas e Elegantes */
          .custom-progress {{ width: 100%; height: 5px; background-color: #f1f5f9; border-radius: 9999px; margin: 12px 0 6px 0; overflow: hidden; }}
          .custom-progress-fill {{ height: 100%; border-radius: 9999px; }}
          
          /* Badges de Status Modernos com Ponto (Estilo Linear) */
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
          .status-dot-badge .dot {{
            width: 5px;
            height: 5px;
            border-radius: 50%;
          }}
          
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
        </head>
        <body>

        <div class="dashboard-container">
          
          <!-- Banner do Cabeçalho -->
          <div class="header-banner">
            <div class="header-title-section">
              <h1>📊 Product Ads Intelligence</h1>
              <p>Anunciante: {advertiser_nome} &nbsp;·&nbsp; Ciclo Financeiro: Fechamento todo o dia {dia_fechamento_input}</p>
            </div>
            <div class="header-date-badge">
              📅 Gerado em {hoje.strftime('%d/%m/%Y às %H:%M')}
            </div>
          </div>
          
          <!-- KPI Grid (Reconfigurado) -->
          <div class="kpi-grid">
            
            <!-- Card 1: Verba Mensal vs Gasto Atual com Progresso -->
            <div class="kpi-card">
              <div class="kpi-header">
                <span class="kpi-title">Orçamento vs Gasto</span>
                <div class="kpi-icon-container">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
                </div>
              </div>
              <div>
                <div class="kpi-value" style="color: {ritmo_cor};">R$ {gasto_ciclo:,.2f}</div>
                <div class="kpi-meta">de R$ {verba_mensal_input:,.2f} Planejados</div>
              </div>
              <div>
                <div class="custom-progress">
                  <div class="custom-progress-fill" style="width: {percentual_gasto:.1f}%; background-color: {ritmo_cor};"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 10px; color:#94a3b8; font-weight:500;">
                  <span>Consumido: {percentual_gasto:.1f}%</span>
                </div>
              </div>
            </div>
            
            <!-- Card 2: Saldo Restante e Dias Restantes -->
            <div class="kpi-card">
              <div class="kpi-header">
                <span class="kpi-title">Saldo Restante</span>
                <div class="kpi-icon-container">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
                </div>
              </div>
              <div>
                <div class="kpi-value" style="color: #10b981;">R$ {verba_restante:,.2f}</div>
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
            
            <!-- Card 3: Ritmo do Ciclo -->
            <div class="kpi-card">
              <div class="kpi-header">
                <span class="kpi-title">Ritmo de Consumo</span>
                <div class="kpi-icon-container">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#eab308" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                </div>
              </div>
              <div style="margin-top: 10px;">
                {ritmo_badge_html}
                <p style="font-size: 11px; color: #64748b; margin-top: 10px; line-height: 1.4;">
                  {ritmo_desc}
                </p>
              </div>
              <div style="font-size: 10px; color: #94a3b8; font-weight: 500; border-top: 1px solid #f1f5f9; padding-top: 6px; margin-top: 6px;">
                Desvio Cronograma: {percentual_gasto - percentual_tempo:+.1f}%
              </div>
            </div>
            
            <!-- Card 4: Ontem no PADS (Destaques de ROAS/ACOS) -->
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
                    <div style="font-size: 20px; font-weight:700; color:#2563eb;">{roas_geral:.2f}x</div>
                  </div>
                  <div style="border-left: 1px solid #e2e8f0; padding-left: 16px;">
                    <span style="font-size: 8px; font-weight:700; color:#64748b; text-transform:uppercase;">ACOS Ontem</span>
                    <div style="font-size: 20px; font-weight:700; color:#0f172a;">{acos_geral_str}</div>
                  </div>
                </div>
              </div>
              <div style="font-size: 10px; color: #64748b; border-top: 1px solid #f1f5f9; padding-top: 6px; margin-top: 6px; display: flex; justify-content: space-between;">
                <span>Custo: R$ {total_custo_d1:,.2f}</span>
                <span>Fat: R$ {total_receita_d1:,.2f}</span>
              </div>
            </div>
            
          </div>
          
          <!-- Mini Badges de Recomendação -->
          <div class="mini-grid">
            {mini_cards}
          </div>

          <!-- Layout de Duas Colunas (Gráfico e Funil de Performance) -->
          <div class="two-col-layout">
            
            <!-- Coluna 1: Gráfico de Distribuição da Verba -->
            <div class="content-card">
              <div class="section-headline">🍩 Distribuição de Verba Diária</div>
              <div class="section-subtext">Alocação recomendada proporcional à performance (ACOS + volume de vendas)</div>
              {grafico_html if grafico_html else '<p style="color:#94a3b8;font-size:12px;padding:60px 0;text-align:center">Nenhuma campanha com dados de ontem para distribuição de verba.</p>'}
            </div>
            
            <!-- Coluna 2: Detalhes do Funil de Ontem -->
            <div class="content-card">
              <div class="section-headline">📈 Diagnóstico do Funil (Ontem)</div>
              <div class="section-subtext">Visão consolidada do comportamento das campanhas no dia anterior</div>
              
              <!-- Caixa de Destaque -->
              <div class="yesterday-highlights">
                <div class="highlight-box">
                  <span class="h-lbl">ROAS Geral</span>
                  <span class="h-val">{roas_geral:.2f}x</span>
                </div>
                <div class="highlight-box" style="border-left: 1px solid #e2e8f0;">
                  <span class="h-lbl">Conversão Geral</span>
                  <span class="h-val" style="color:#10b981;">{conversion_rate:.2f}%</span>
                </div>
              </div>
              
              <!-- Detalhes do Funil -->
              <div class="metric-row">
                <span class="m-label">💰 Investimento Ontem</span>
                <span class="m-value">R$ {total_custo_d1:,.2f}</span>
              </div>
              <div class="metric-row">
                <span class="m-label">📦 Faturamento Ontem</span>
                <span class="m-value">R$ {total_receita_d1:,.2f}</span>
              </div>
              <div class="metric-row">
                <span class="m-label">🛒 Vendas Concluídas</span>
                <span class="m-value">{total_vendas_d1}</span>
              </div>
              <div class="metric-row">
                <span class="m-label">🖱️ Cliques Acumulados</span>
                <span class="m-value">{total_cliques_d1:,}</span>
              </div>
              <div class="metric-row">
                <span class="m-label">🎯 CPC Médio Real</span>
                <span class="m-value">R$ {cpc_medio:,.2f}</span>
              </div>
              <div class="metric-row">
                <span class="m-label">⚡ Verba Diária Sugerida (Média)</span>
                <span class="m-value" style="color:#2563eb;">R$ {verba_diaria_resto:,.2f}</span>
              </div>
              
            </div>
            
          </div>

          <!-- Tabela de Diagnóstico Completo -->
          <div class="content-card table-card">
            <div class="section-headline">🎯 Diagnóstico Individual de Campanhas</div>
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
                  <th style="text-align:right;">ACOS</th>
                  <th style="text-align:center;">Ação Recomendada</th>
                  <th style="text-align:right;">Sugestão/Dia</th>
                </tr>
              </thead>
              <tbody>
                {linhas_tabela}
              </tbody>
            </table>
          </div>
          
          <!-- Footer do Dashboard -->
          <div class="dashboard-footer">
            Product Ads Executive Intelligence · Gerado dinamicamente para o Mercado Livre · {hoje.strftime('%d/%m/%Y %H:%M:%S')}
          </div>
          
        </div>

        </body>
        </html>
        """
        
        # Renderizar o HTML em um iframe no Streamlit
        components.html(html, height=1400, scrolling=True)

        # Exportar CSV no Streamlit
        cols_csv = ["Campanha","Status","Orç. Atual","Custo","Receita","Cliques","Vendas","ACOS","Recomendação","Sugestão/dia"]
        df_csv = pd.DataFrame(registros)[cols_csv]
        csv_data = df_csv.to_csv(index=False, encoding="utf-8-sig", sep=";").encode("utf-8-sig")
        
        st.download_button(
            label="⬇️ Baixar Relatório das Campanhas em CSV",
            data=csv_data,
            file_name=f"relatorio_product_ads_{hoje.strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
