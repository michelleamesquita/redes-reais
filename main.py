import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from random import sample

def load_edgelist(path, directed=True, sep=None, comment='#'):
    """
    Lê lista de arestas (duas colunas: src, dst).
    - directed=True: cria DiGraph; caso contrário Graph.
    """

    df = pd.read_csv(path, sep=sep, comment=comment, header=None, usecols=[0,1], names=['src','dst'], engine='python')
    if directed:
        G = nx.from_pandas_edgelist(df, source='src', target='dst', create_using=nx.DiGraph())
    else:
        G = nx.from_pandas_edgelist(df, source='src', target='dst', create_using=nx.Graph())
    return G

def biggest_component_fraction(G):
    if G.is_directed():
        comps = list(nx.weakly_connected_components(G))
    else:
        comps = list(nx.connected_components(G))
    if not comps:
        return 0.0, set()
    largest = max(comps, key=len)
    return len(largest)/G.number_of_nodes(), largest

def mean_degree(G):
    n, m = G.number_of_nodes(), G.number_of_edges()
    if G.is_directed():
        return {'k_in': m/n, 'k_out': m/n}
    else:
        return {'k': 2*m/n}

def clustering_coeff(G):
    # Para dirigidos, reportar clustering do grafo não-direcionado equivalente
    H = G.to_undirected() if G.is_directed() else G
    return nx.average_clustering(H)

def assortativity(G):
    H = G.to_undirected() if G.is_directed() else G
    try:
        return nx.degree_assortativity_coefficient(H)
    except Exception:
        return np.nan

def estimate_average_distance(G, nodes_sample=100):
    """
    Estima distância média ℓ na maior componente via BFS
    a partir de uma amostra de nós (rápido e razoável p/ grafos grandes).
    """
    if G.is_directed():
        H = G.to_undirected(as_view=True)
    else:
        H = G
    # trabalhar só na maior componente
    comps = list(nx.connected_components(H))
    if not comps:
        return np.nan
    giant_nodes = max(comps, key=len)
    H = H.subgraph(giant_nodes).copy()
    n = H.number_of_nodes()
    k = min(nodes_sample, n)
    seeds = sample(list(H.nodes()), k)
    dists = []
    for s in seeds:
        lengths = nx.single_source_shortest_path_length(H, s)
        if len(lengths) > 1:
            dists.extend(lengths.values())
    if not dists:
        return np.nan
    return float(np.mean(dists))

def summarize_network(G, name, estimate_dist=True):
    n, m = G.number_of_nodes(), G.number_of_edges()
    S, largest = biggest_component_fraction(G)
    deg = mean_degree(G)
    C = clustering_coeff(G)
    r = assortativity(G)
    density = nx.density(G.to_undirected() if G.is_directed() else G)
    summary = {
        'name': name,
        'directed': G.is_directed(),
        'n': n,
        'm': m,
        'density': density,
        **deg,
        'S_largest_component': S,
        'C_avg_clustering': C,
        'r_assortativity': r
    }
    if estimate_dist:
        summary['ell_avg_distance_est'] = estimate_average_distance(G, nodes_sample=100)
    return summary

def compute_degree_summary(G: nx.Graph) -> dict:
    summary = {}
    if G.is_directed():
        in_degs = dict(G.in_degree())
        out_degs = dict(G.out_degree())
        if in_degs:
            max_in_node = max(in_degs, key=in_degs.get)
            summary['max_in_node'] = max_in_node
            summary['max_in_deg'] = in_degs[max_in_node]
        if out_degs:
            max_out_node = max(out_degs, key=out_degs.get)
            summary['max_out_node'] = max_out_node
            summary['max_out_deg'] = out_degs[max_out_node]
    else:
        degs = dict(G.degree())
        if degs:
            max_node = max(degs, key=degs.get)
            summary['max_node'] = max_node
            summary['max_deg'] = degs[max_node]
    return summary

# Atualiza para aceitar resumos de grau e explicar NaN em k_in/k_out
def build_markdown_report(df: pd.DataFrame, degree_info: dict | None = None) -> str:
    lines = []
    lines.append("## Relatório de Métricas de Redes\n")
    lines.append("Este relatório resume métricas básicas calculadas para cada rede, com breves explicações.\n")
    lines.append("\n")
    lines.append("### Métricas e definições\n")
    lines.append("- **name**: nome do dataset.\n")
    lines.append("- **directed**: se a rede é direcionada (True) ou não direcionada (False).\n")
    lines.append("- **n**: número de nós (|V|).\n")
    lines.append("- **m**: número de arestas (|E|).\n")
    lines.append("- **density**: densidade do grafo (fração de pares conectados).\n")
    lines.append("- **k** / **k_in** / **k_out**: grau médio. Em não direcionados: k = 2m/n. Em direcionados: k_in = k_out = m/n.\n")
    lines.append("- **S_largest_component**: fração de nós na maior componente (em dirigidos, componente fracamente conexa).\n")
    lines.append("- **C_avg_clustering**: coeficiente de agrupamento médio (para dirigidos, do grafo não-direcionado equivalente).\n")
    lines.append("- **r_assortatividade**: assortatividade por grau.\n")
    if 'ell_avg_distance_est' in df.columns:
        lines.append("- **ell_avg_distance_est**: estimativa da distância média na maior componente (amostragem).\n")
    lines.append("\n")
    lines.append("### Observações\n")
    lines.append("- Em redes não direcionadas, **k_in** e **k_out** não se aplicam. Por isso, ao combinar resultados com redes dirigidas, essas colunas podem aparecer como NaN — isso é esperado.\n")
    lines.append("- **C = 0** indica ausência de triângulos (vizinhos não se conectam entre si), não necessariamente que um nó não tenha vizinhos.\n")
    lines.append("\n")
    lines.append("### Resultados\n")
    lines.append(df.to_markdown(index=False))
    lines.append("\n")
    lines.append("### Conclusões\n")
    for _, row in df.iterrows():
        name = row['name']
        directed = row['directed']
        C = row.get('C_avg_clustering', np.nan)
        r = row.get('r_assortatividade', np.nan)
        lines.append(f"- **{name}**:")
        if degree_info and name in degree_info:
            d = degree_info[name]
            if directed:
                if 'max_out_node' in d:
                    lines.append(f"  - Maior grau de saída: nó {d['max_out_node']} com {d['max_out_deg']} arestas de saída.")
                if 'max_in_node' in d:
                    lines.append(f"  - Maior grau de entrada: nó {d['max_in_node']} com {d['max_in_deg']} arestas de entrada.")
            else:
                if 'max_node' in d:
                    lines.append(f"  - Maior grau: nó {d['max_node']} com {d['max_deg']} arestas.")
        # Interpretações curtas
        if not np.isnan(C):
            if C == 0:
                lines.append("  - C = 0 sugere baixa coesão local (sem triângulos entre vizinhos).")
            elif C < 0.05:
                lines.append("  - C baixo sugere vizinhanças pouco conectadas (poucas tríades fechadas).")
            else:
                lines.append("  - C moderado/alto indica tendência a comunidades locais (vizinhos conectados entre si).")
        if not np.isnan(r):
            if r < 0:
                lines.append("  - r < 0 (disassortativa): hubs tendem a conectar a nós de baixo grau.")
            elif r > 0:
                lines.append("  - r > 0 (assortativa): nós tendem a conectar a outros de grau similar.")
            else:
                lines.append("  - r ≈ 0: pouca correlação de grau entre nós conectados.")
    lines.append("\n")
    return "\n".join(lines)

WWW_EDGES = 'data/web-NotreDame.txt'   
PPI_EDGES = 'data/yeast.edgelist'         

G_www = load_edgelist(WWW_EDGES, directed=True, sep='\s+') ##direcionada
G_ppi = load_edgelist(PPI_EDGES, directed=False, sep='\s+') ##nao direcionada

res = []
res.append(summarize_network(G_www, 'WWW_nd.edu'))
res.append(summarize_network(G_ppi, 'Protein_Interactions'))

df = pd.DataFrame(res)
# preparar resumos de grau e adicionar colunas ao DataFrame
_degree_info = {
    'WWW_nd.edu': compute_degree_summary(G_www),
    'Protein_Interactions': compute_degree_summary(G_ppi),
}
for col in ['max_in_node','max_in_deg','max_out_node','max_out_deg','max_node','max_deg']:
    df[col] = df['name'].map(lambda nm: _degree_info.get(nm, {}).get(col, np.nan))
print(df)
# salvar
df.to_csv('metrics_newman_benchmarks.csv', index=False)

# preparar resumos de grau para conclusões
_degree_info = {
    'WWW_nd.edu': compute_degree_summary(G_www),
    'Protein_Interactions': compute_degree_summary(G_ppi),
}

# gerar relatório Markdown
report_text = build_markdown_report(df, degree_info=_degree_info)
with open('metrics_report.md', 'w', encoding='utf-8') as f:
    f.write(report_text)
print("Relatório salvo em metrics_report.md")
