# 📌 Redes Reais com NetworkX

Trabalho da disciplina de Redes Complexas (Semana 0–1).  
Objetivo: selecionar **duas redes reais** dos benchmarks do livro *Newman (2018)*, calcular propriedades básicas usando **NetworkX** e analisar os resultados.  

---

## 📂 Estrutura do Projeto
```
.
├── data/
│   ├── web-NotreDame.txt       # WWW (269k nós, 1.4M arestas)
│   ├── yeast_ppi.txt           # Interações proteína-proteína (2k nós)
├── src/
│   └── main.py                 # Código com NetworkX
├── metrics_newman.csv          # Resultados das métricas
└── README.md
```


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


## 📊 Saída e Relatório

### 🔍 Interpretação rápida
- **n, m**: números de nós e arestas.
- **directed**: indica se a rede é dirigida.
- **k / k_in / k_out**: grau médio. Não dirigidos: `k = 2m/n`. Dirigidos: `k_in = k_out = m/n`.
- **S_largest_component**: fração de nós na maior componente (em dirigidos, componente fracamente conexa).
- **C_avg_clustering**: clustering médio (para dirigidos, no grafo não direcionado equivalente).
- **r_assortatividade**: assortatividade por grau; `r < 0` (disassortativo), `r > 0` (assortativo), `r ≈ 0` (neutro).
- **ell_avg_distance_est**: estimativa da distância média na maior componente.
- **Observação sobre NaN**: Em redes não direcionadas, `k_in` e `k_out` não se aplicam. Ao combinar com redes dirigidas, essas colunas aparecem como **NaN** — isso é esperado.

## RELATÓRIO FINAL

- [Relatório de métricas (Markdown)](./metrics_report.md)
- [CSV com métricas](./metrics_newman_benchmarks.csv)




