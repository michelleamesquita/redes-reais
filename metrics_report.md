## Relatório de Métricas de Redes

Este relatório resume métricas básicas calculadas para cada rede, com breves explicações.



### Métricas e definições

- **name**: nome do dataset.

- **directed**: se a rede é direcionada (True) ou não direcionada (False).

- **n**: número de nós (|V|).

- **m**: número de arestas (|E|).

- **density**: densidade do grafo (fração de pares conectados).

- **k** / **k_in** / **k_out**: grau médio. Em não direcionados: k = 2m/n. Em direcionados: k_in = k_out = m/n.

- **S_largest_component**: fração de nós na maior componente (em dirigidos, componente fracamente conexa).

- **C_avg_clustering**: coeficiente de agrupamento médio (para dirigidos, do grafo não-direcionado equivalente).

- **r_assortatividade**: assortatividade por grau.

- **ell_avg_distance_est**: estimativa da distância média na maior componente (amostragem).



### Observações

- Em redes não direcionadas, **k_in** e **k_out** não se aplicam. Por isso, ao combinar resultados com redes dirigidas, essas colunas podem aparecer como NaN — isso é esperado.

- **C = 0** indica ausência de triângulos (vizinhos não se conectam entre si), não necessariamente que um nó não tenha vizinhos.



### Resultados

| name                 | directed   |      n |       m |     density |      k_in |     k_out |   S_largest_component |   C_avg_clustering |   r_assortativity |   ell_avg_distance_est |         k |   max_in_node |   max_in_deg |   max_out_node |   max_out_deg |   max_node |   max_deg |
|:---------------------|:-----------|-------:|--------:|------------:|----------:|----------:|----------------------:|-------------------:|------------------:|-----------------------:|----------:|--------------:|-------------:|---------------:|--------------:|-----------:|----------:|
| WWW_nd.edu           | True       | 325729 | 1497134 | 2.10664e-05 |   4.59626 |   4.59626 |              1        |           0.234624 |        -0.0526126 |                6.95404 | nan       |           nan |          nan |            nan |           nan |        nan |       nan |
| Protein_Interactions | False      |   2018 |    2930 | 0.0014397   | nan       | nan       |              0.816155 |           0.046194 |        -0.0550781 |                5.7954  |   2.90387 |           nan |          nan |            nan |           nan |        nan |       nan |


### Conclusões

- **WWW_nd.edu**:
  - C moderado/alto indica tendência a comunidades locais (vizinhos conectados entre si).
- **Protein_Interactions**:
  - C baixo sugere vizinhanças pouco conectadas (poucas tríades fechadas).

