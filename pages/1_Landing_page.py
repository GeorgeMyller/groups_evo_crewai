import streamlit as st

st.set_page_config(page_title='Group Management & Scheduling App', layout='wide')

# Inject custom CSS for a modern, elegant design with Google Fonts and Font Awesome
st.markdown(
    """
    <style>
    /* ...existing imports and styles... */

    /* Hero background com gradiente mais vivo */
    body { 
        background: linear-gradient(135deg, #fbc2eb 0%, #a18cd1 100%);
    }

    /* Animação suave ao passar o cursor */
    .title:hover {
        text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        transform: scale(1.03);
        transition: transform 0.3s ease, text-shadow 0.3s ease;
    }

    /* Seção principal com destaque */
    .content {
      max-width: 900px;
      margin: auto;
      padding: 50px 30px;
      background: rgba(255, 255, 255, 0.75); /* fundo levemente translúcido */
      border-radius: 10px;
      box-shadow: 0 8px 30px rgba(0,0,0,0.2);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .content:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }

    /* Botões de ação */
    .cta-button {
        background: linear-gradient(45deg, #ff9966, #ff5e62);
        border: none;
        border-radius: 8px;
        color: #fff;
        margin-top: 40px;
    }

    /* Ajusta tipografia em geral */
    .tab-content p, .tab-content ul {
        font-size: 1.1em;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Landing page content using tabs to support both Portuguese and English
st.markdown('<h1 class="title">Bem-vindo ao WhatsApp Group Resumer App</h1>', unsafe_allow_html=True)

# Tabs for languages
tabs = st.tabs(["Versão em Português", "English Version"])

with tabs[0]:
    st.markdown('<p class="subtitle">Uma experiência centrada no usuário para gerenciar grupos e agendar resumos de forma prática.</p>', unsafe_allow_html=True)
    st.markdown('''
    <div class="tab-content">
        <h3>O que o Programa Faz?</h3>
        <p>Este programa permite que você visualize detalhes dos grupos, agende a geração de resumos automáticos e os envie para grupos ou contatos pessoais. Nossa interface intuitiva foi desenvolvida para oferecer uma experiência agradável e eficiente.</p>
        <h3>Como Funciona?</h3>
        <p>Após carregar os dados dos grupos e você pode selecionar um grupo específico, visualizar suas informações e configurar o agendamento do resumo. Escolha entre agendamentos diários ou uma execução única, e o sistema cuida do restante automaticamente.</p>
        
    </div>
    ''', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<p class="subtitle">A user-centered experience to manage groups and schedule automated summaries effortlessly.</p>', unsafe_allow_html=True)
    st.markdown('''
    <div class="tab-content">
        <h3>What Does This Program Do?</h3>
        <p>This program allows you to view detailed group information, schedule automated summary generation, and send these summaries to groups or personal contacts. Our intuitive interface is designed to provide an efficient and enjoyable experience.</p>
        <h3>How It Works?</h3>
        <p>After loading group data and you can select a specific group, view its details, and configure summary scheduling. Choose between daily or one-time tasks, and the system automatically handles the rest.</p>
       
    </div>
    ''', unsafe_allow_html=True)