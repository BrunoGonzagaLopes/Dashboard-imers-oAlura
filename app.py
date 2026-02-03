import pandas as pd 
import plotly.express as px
import streamlit as st

st.markdown("""
    <style>
    div[data-baseweb="select"] span {
        background-color: #000 !important;  
        color: white !important;              
    }
    </style>
""", unsafe_allow_html=True)


#Configuração da página#
#Define o titulo da pagin, o icone e o layout para acompanhar a largura inteira
st.set_page_config(
    page_title='Dashboard de Salários na Area de Dados',
    page_icon='🗽',
    layout='wide' #deixa a pagina larga
)

#carregamento de dados
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

#criando a barra lateral 
st.sidebar.header('🍳Filtros') # <- dando um titulo para a barra lateral criada

# --- Criando os filtro --- #
#FIltro de Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect('Ano', anos_disponiveis, default=anos_disponiveis)

#FIltro de Senioridade 
senioridades = df['senioridade'].unique()
senioridade_selecionado = st.sidebar.multiselect('Senioridade', senioridades, default=senioridades)

#FIltro de tipo de contrato 
contratos = df['contrato'].unique()
contrato_selecionado = st.sidebar.multiselect('Tipo de Contratos', contratos, default=contratos)

#FIltro de tipo de trabalho 
tipos_trabalho = df['remoto'].unique()
tipo_selecionado = st.sidebar.multiselect('Tipo de Trabalho', tipos_trabalho, default=tipos_trabalho)


# ---   Agora vamos filtrar os Df --- #
#cria um DataFrame de acordo com as seleções feitas na barra lateral 
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) & 
    (df['senioridade'].isin(senioridade_selecionado))&
    (df['contrato'].isin(contrato_selecionado)) &
    (df['remoto'].isin(tipo_selecionado))
]

# --- Main --- # 

st.title("⚜️Dashboard de análise salarial na área de dados⚜️") # <- Titulos do conteudo principal
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros no menu lateral para refinar sua busca")


# -- Metricas Gerais --# 
st.subheader('Metricas gerais (Salário anual em USD)')
if not df_filtrado.empty:
    total_registro = df_filtrado.shape[0]
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    salario_minimo = df_filtrado['usd'].min()
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
    modalidade_mais_frequente = df_filtrado['remoto'].mode()[0]
else:
    total_registro, salario_medio, salario_maximo, salario_minimo, cargo_mais_frequente, modalidade_mais_frequente = 0
st.markdown(f'Total de registros encontrados: {total_registro}' )
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric('Sálario Medio', f"${salario_medio:,.0f}")
col2.metric('Sálario Máximo', f"${salario_maximo:,.0f}")
col3.metric('Sálario mínimo', f"${salario_minimo:,.0f}")
col4.metric('Cargo mais Frequente', f"{cargo_mais_frequente}")
col5.metric('Modalidade de trabalho mais frequente ', f"{modalidade_mais_frequente}")
st.markdown('---')

 # --- Cargos com maior media - quantidade variavels---#
colunaGrafico, colunaParamentro = st.columns([9,1])

if not df_filtrado.empty:
    #coluna para perguntar qauntos cargos devem aparecer nos graficos#
    with colunaParamentro:
        max =len(df_filtrado['cargo'].unique())
        
        maioresRegistros = st.number_input(label='Selecione a quantidade de registros',
                                           value=10,
                                           min_value= 5,
                                           max_value=max)
    #coluna do grafico
    with colunaGrafico:
        if not df_filtrado.empty:
            st.subheader('Média Salarial por cargos')
            top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(maioresRegistros).sort_values(ascending=False).reset_index()
            graficoCargos = px.bar(top_cargos,
                y='cargo',
                x='usd',
                title=f"Top {maioresRegistros} cargos por média salarial",
                labels={'usd': 'Media Salarial' , 'cargo': '' }
            )
            graficoCargos.update_layout(title_x = 0.1, yaxis = {'categoryorder':'total ascending'})
            st.plotly_chart(graficoCargos, use_container_width=True)
        else:
            st.warning('Nenhum dado para exibir no gráfico')
    st.markdown('---')
    
    
    # --- Media de cargos e senioridade --- #
    colunaGraficoDisco, colunaGrafico_MediaPorSenioridade, colunaSideBar = st.columns([5,5,3])
    mapa_cores = {
    "junior": "#00fff2",
    "pleno": "#006fd6",
    "senior": "#000d7e",
    "executivo": "#10011f"
}
    # coluna dos cargos #
    with colunaSideBar:
        cargosmaisFrequentes = df_filtrado['cargo'].value_counts().nlargest(maioresRegistros).index.tolist()
        cargo_selecionado = st.multiselect('Cargo', cargosmaisFrequentes, default=cargosmaisFrequentes)

        df_limpo_para_Cargos = df_filtrado[(df_filtrado['cargo'].isin(cargo_selecionado))]
    #grafico de pizza que facilita na visualização da relação entre cargo e senioridade pelos cargos definidos acima, mostra em porcentagem, numeros 
    with colunaGraficoDisco:
        
        df_relacao_senioridade_cargo =  (df_limpo_para_Cargos['senioridade'].value_counts().reset_index())
        df_relacao_senioridade_cargo.columns = ['senioridade', 'contagem']
       
        graficoPizza = px.pie(
            df_relacao_senioridade_cargo,
            names="senioridade",         
            values="contagem",     
            hole=0.5, 
            color="senioridade",                            
            title="Distribuição de senioridade por cargos",
            color_discrete_map=mapa_cores
        )
        graficoPizza.update_traces(textinfo='label+percent')
        st.plotly_chart(graficoPizza, use_container_width=True)
    
    #grafico de media salarial de determinados cargos divididas por senioridade 
    with colunaGrafico_MediaPorSenioridade:
        df_media_por_senioridade = df_limpo_para_Cargos.groupby(['senioridade'])['usd'].mean().sort_values(ascending=False).reset_index()
        graficoMediaPorSenioridade = px.bar(
            df_media_por_senioridade,
            x='senioridade',
            y='usd',
            color='senioridade',
            color_discrete_map=mapa_cores,
            title="Média salarial por senioridade",
            labels={'usd': "Média Salarial ", 'senioridade':'Senioridade'},
            text_auto='.2f'   
        )
     

        graficoMediaPorSenioridade.update_layout(bargap=0.01)
        st.plotly_chart(graficoMediaPorSenioridade, use_container_width=True)
    st.markdown('---')
    
    # --- Mapa da media salarial entre paises ---#
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'].isin(cargo_selecionado)]
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='Cividis',
            title='Salário médio por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(width=1500, height=900)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.") 
else:
     st.warning('Nenhum dado para exibir no gráfico')
# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)
        
        
        
        
        
        
        

        
