# 📌 Redes Reais com NetworkX

Trabalho da disciplina de Redes Complexas (Semana 0–1).  
Objetivo: selecionar **duas redes reais** dos benchmarks do livro *Newman (2018)*, calcular propriedades básicas usando **NetworkX** e analisar os resultados.  

---

## 📂 Estrutura do Projeto

.
├── data/
│   ├── web-NotreDame.txt       # WWW (269k nós, 1.4M arestas)
│   ├── yeast_ppi.txt           # Interações proteína-proteína (2k nós)
├── src/
│   └── main.py                 # Código com NetworkX
├── metrics_newman.csv          # Resultados das métricas
└── README.md


🔗 Datasets Utilizados

1. **WWW (Notre Dame)**  
   - Fonte: [SNAP – Stanford Network Analysis Project](https://snap.stanford.edu/data/web-NotreDame.html)  
   - Arquivo: `web-NotreDame.txt.gz`  
   - **Nós (n):** 269 504  
   - **Arestas (m):** 1 497 135  
   - Grafo **direcionado**

2. **Protein–Protein Interaction (Yeast)**  
   - Fonte: [Kaggle – Yeast PPI dataset](https://www.kaggle.com/datasets/alexandervc/yeast-proteinprotein-interaction-network)  
   - Arquivo: `yeast_ppi.txt`  
   - **Nós (n):** ~2 115  
   - **Arestas (m):** ~2 240  
   - Grafo **não direcionado**



⚙️ Instalação

```pip install -r requirements.txt```


▶️ Execução

```python main.py```




