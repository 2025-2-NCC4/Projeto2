# FECAP - Fundação de Comércio Álvares Penteado

<p align="center">
<a href= "https://www.fecap.br/"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhZPrRa89Kma0ZZogxm0pi-tCn_TLKeHGVxywp-LXAFGR3B1DPouAJYHgKZGV0XTEf4AE&usqp=CAU" alt="FECAP - Fundação de Comércio Álvares Penteado" border="0"></a>
</p>

# Dashboard Interativo PicMoney

## Nome do Grupo: **CDKR**

## Integrantes: **Caroliny Rossi Bittencourt**, **Duda Lucena Miguel**, **Isadora Teixeira Santoma**, **Rafael Alves dos Santos Guimarães** 

## Professores Orientadores: **Rodnil Lisboa**, **Mauricio Lopes**, **Lucy Mari**, **Eduardo Savino**

## Descrição

<p align="center">
  <img src="https://github.com/2025-2-NCC4/Projeto2/blob/main/imagens/logo.png?raw=true" 
       alt="CDKR" 
       width="300" 
       border="0">
  <br>
  Logo by CDKR — 
  <a rel="license" href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a>
</p>


O projeto **Dashboard Interativo PicMoney** tem como objetivo consolidar e visualizar informações provenientes das bases de dados da empresa PicMoney — abrangendo players, cupons, lojas e transações — em uma interface analítica interativa.  

Desenvolvido com **Streamlit** (front-end) e **Flask + SQLite** (back-end), o sistema segue o modelo **MVC (Model–View–Controller)**, oferecendo painéis distintos para perfis **CEO** e **CFO**, permitindo análises dinâmicas e geração automática de relatórios em PDF.  

A iniciativa integra conhecimentos de **Ciência de Dados**, **Engenharia de Software** e **Visualização Analítica**, alinhando-se à **ODS 9 – Indústria, Inovação e Infraestrutura**, e aplicando boas práticas de modularização, cacheamento e usabilidade.  
<br><br>

## 🛠 Estrutura de pastas
```sh
📁 Projeto2_extracted/
┗ 📁 Projeto2-main/
   ┣ 📁 documentos/
   ┃  ┣ 📁 Entrega 1/
   ┃  ┃  ┣ 📁 Analise_Inferencial_de_Dados/
   ┃  ┃  ┃  ┗ 📁 bases_de_dados/
   ┃  ┃  ┣ 📁 Contabilidade_e_Financas/
   ┃  ┃  ┃  ┗ 📁 base_de_dados/
   ┃  ┃  ┣ 📁 ES e AS/
   ┃  ┃  ┗ 📁 Projeto_Interdiciplinar_Ciencia_de_Dados/
   ┃  ┃     ┗ 📁 base_de_dados/
   ┃  ┗ 📁 Entrega 2/
   ┃     ┣ 📁 Analise_Inferencial_de_Dados/
   ┃     ┃  ┗ 📁 relatorio/
   ┃     ┣ 📁 Contabilidade_e_Financas/
   ┃     ┃  ┣ 📁 bases/
   ┃     ┃  ┗ 📁 LaTeX/
   ┃     ┣ 📁 ES e AS/
   ┃     ┗ 📁 Projeto_Interdiciplinar_Ciencia_de_Dados/
   ┃        ┣ 📁 bases_originais/
   ┃        ┣ 📁 bases_tratadas/
   ┃        ┗ 📁 relatorio/
   ┣ 📁 imagens/
   ┗ 📁 src/
      ┣ 📁 Entrega 1/
      ┃  ┣ 📁 Backend/
      ┃  ┗ 📁 Frontend/
      ┗ 📁 Entrega_2/
         ┣ 📁 Backend/
         ┃  ┗ 📁 data/
         ┃     ┗ 📁 base_de_dados/
         ┗ 📁 frontend/
            ┣ 📁 .streamlit/
            ┣ 📁 assets/
            ┣ 📁 base_de_dados/
            ┣ 📁 charts/
            ┃  ┣ 📁 KPIs_Base_Lojas/
            ┃  ┣ 📁 KPIs_Base_Players/
            ┃  ┣ 📁 KPIs_Base_Transacoes/
            ┃  ┣ 📁 KPIs_Liquidez/
            ┃  ┃  ┗ 📁 __pycache__/
            ┃  ┣ 📁 KPIs_Transações/
            ┃  ┃  ┗ 📁 __pycache__/
            ┃  ┗ 📁 Repasse/
            ┃     ┗ 📁 __pycache__/
            ┣ 📁 components/
            ┃  ┣ 📁 aba_financeiro/
            ┃  ┃  ┗ 📁 __pycache__/
            ┃  ┣ 📁 aba_liquidez/
            ┃  ┃  ┗ 📁 __pycache__/
            ┃  ┣ 📁 aba_perfil_cupons/
            ┃  ┣ 📁 aba_perfil_players/
            ┃  ┣ 📁 aba_perfil_transacoes/
            ┃  ┗ 📁 aba_repasse/
            ┃     ┗ 📁 __pycache__/
            ┣ 📁 pages/
            ┗ 📁 utils/

```

<b>documentos</b>: documentação geral do projeto.  
<b>imagens</b>: recursos visuais e logotipos.  
<b>src</b>: código-fonte completo (backend e frontend).  

## 🛠 Instalação

Os scripts principais do projeto estão organizados nas seguintes pastas:

-   Backend: src/Entrega_2/Backend
-   Frontend: src/Entrega_1/frontend

Cada parte deve ser executada em um terminal separado, conforme
instruções abaixo:

------------------------------------------------------------------------

💻 Front-end (Streamlit)

Entre na pasta do frontend:

    cd src/Entrega_1/frontend

Instale as dependências e execute o app:

    pip install -r requirements.txt
    streamlit run app.py

------------------------------------------------------------------------

⚙️ Back-end (Flask)

Entre na pasta do backend:

    cd src/Entrega_2/Backend

Instale as dependências e execute o servidor:

    pip install -r requirements.txt
    python app.py


O projeto é executado localmente e acessado via navegador (geralmente em `http://localhost:8501`).
💻 Configuração para Desenvolvimento

Para executar e editar o projeto localmente, é necessário configurar o
ambiente de desenvolvimento com as seguintes ferramentas:

-   Visual Studio Code (VSCode) – IDE recomendada para editar e executar
    o projeto.
-   Python 3.11+ – linguagem base utilizada em todo o sistema.
-   Git – para clonar o repositório e versionar o código.

## 📋 Licença/License

Licença **Creative Commons CC BY 4.0**  
<a href="https://github.com/2025-2-NCC4/Projeto2">DashBoard Interativo</a> © 2025 by <a href="https://github.com/2025-2-NCC4/Projeto2">FECAP, Caroliny Rossi Bittencourt, Duda Lucena Miguel, Isadora Teixeira Santoma, Rafael Alves dos Santos Guimarães</a> is licensed under <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a><img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;"><img src="https://mirrors.creativecommons.org/presskit/icons/by.svg" alt="" style="max-width: 1em;max-height:1em;margin-left: .2em;">

## 🎓 Referências

1. FECAP – Fundação Escola de Comércio Álvares Penteado. *Regulamento das Atividades de Extensão*, 2024.  
2. STREAMLIT INC. *Streamlit Documentation*. Disponível em: <https://docs.streamlit.io/>.  
3. GRINBERG, Miguel. *Flask Web Development: Developing Web Applications with Python.* O’Reilly Media, 2018.  
4. PLOTLY TECHNOLOGIES INC. *Plotly Express User Guide.* Disponível em: <https://plotly.com/python/>.  
5. MCKINNEY, Wes. *Python for Data Analysis.* O’Reilly Media, 2022.  
6. <https://www.toptal.com/developers/gitignore>
