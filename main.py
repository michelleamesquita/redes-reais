import pandas as pd
import numpy as np
import networkx as nx
from pathlib import Path
from random import sample
from collections import Counter, defaultdict
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
FIG_DIR = BASE_DIR / 'figs'
FIG_DIR.mkdir(parents=True, exist_ok=True)

def load_edgelist(path, directed=True, sep=None, comment='#'):
    """
    Lê lista de arestas (duas colunas: src, dst) e cria grafo.
    - directed=True cria DiGraph; caso contrário Graph (não dirigido).
    - sep pode ser regex (ex.: '\\s+' para espaços).
    """

    df = pd.read_csv(path, sep=sep, comment=comment, header=None, usecols=[0,1], names=['src','dst'], engine='python')
    if directed:
        G = nx.from_pandas_edgelist(df, source='src', target='dst', create_using=nx.DiGraph())
    else:
        G = nx.from_pandas_edgelist(df, source='src', target='dst', create_using=nx.Graph())
    return G

def biggest_component_fraction(G):
    """Retorna fração de nós na maior componente e o conjunto de nós dessa componente."""
    if G.is_directed():
        comps = list(nx.weakly_connected_components(G))
    else:
        comps = list(nx.connected_components(G))
    if not comps:
        return 0.0, set()
    largest = max(comps, key=len)
    return len(largest)/G.number_of_nodes(), largest

def mean_degree(G):
    """Retorna grau médio: {k} para não dirigidos; {k_in, k_out} para dirigidos."""
    n, m = G.number_of_nodes(), G.number_of_edges()
    if G.is_directed():
        return {'k_in': m/n, 'k_out': m/n}
    else:
        return {'k': 2*m/n}

def clustering_coeff(G):
    """Coeficiente de clusterização médio (usa grafo não dirigido equivalente)."""
    # Para dirigidos, reportar clustering do grafo não-direcionado equivalente
    H = G.to_undirected() if G.is_directed() else G
    return nx.average_clustering(H)

def assortativity(G):
    """Assortatividade por grau (usa grafo não dirigido equivalente)."""
    H = G.to_undirected() if G.is_directed() else G
    try:
        return nx.degree_assortativity_coefficient(H)
    except Exception:
        return np.nan


def plot_degree_distribution(G: nx.Graph, name: str) -> Path:
    """Gera scatter log–log da distribuição de graus e salva em figs/."""
    degrees = [d for _, d in G.degree()]
    counts = Counter(degrees)
    xs = sorted(counts.keys())
    ys = [counts[k] for k in xs]
    plt.figure(figsize=(6,4))
    plt.scatter(xs, ys, s=8, alpha=0.7)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Grau (k)')
    plt.ylabel('Número de nós')
    plt.title(f'Distribuição de grau (log-log) - {name}')
    out = FIG_DIR / f'{name}_degree_loglog.png'
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out

def get_components_info(G: nx.Graph):
    """Lista tamanhos das componentes e retorna também o conjunto de nós da gigante."""
    if G.is_directed():
        comps = list(nx.weakly_connected_components(G))
    else:
        comps = list(nx.connected_components(G))
    sizes = sorted([len(c) for c in comps], reverse=True)
    giant = max(comps, key=len) if comps else set()
    return sizes, giant

def distances_metrics_on_gcc(G: nx.Graph, name: str, max_nodes_exact: int = 20000):
    """Na CCG: calcula distância média exata, diâmetro e salva histograma das distâncias (se pequena)."""
    # trabalhar no grafo não-direcionado equivalente para distâncias/diâmetro
    H = G.to_undirected(as_view=True) if G.is_directed() else G
    sizes, giant = get_components_info(H)
    if not giant:
        return np.nan, np.nan, None
    H_gcc = H.subgraph(giant).copy()
    n_gcc = H_gcc.number_of_nodes()
    if n_gcc > max_nodes_exact:
        return np.nan, np.nan, None
    # distâncias exatas e diâmetro
    ell = nx.average_shortest_path_length(H_gcc)
    diameter = nx.diameter(H_gcc)
    # distribuição das distâncias
    dists = []
    for _, dist_dict in nx.all_pairs_shortest_path_length(H_gcc):
        dists.extend([d for d in dist_dict.values() if d > 0])
    dist_counts = Counter(dists)
    xs = sorted(dist_counts.keys())
    ys = [dist_counts[k] for k in xs]
    plt.figure(figsize=(6,4))
    plt.bar(xs, ys)
    plt.xlabel('Distância geodésica')
    plt.ylabel('Número de pares de nós')
    plt.title(f'Distribuição de distâncias na CCG - {name}')
    out = FIG_DIR / f'{name}_distance_distribution.png'
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return float(ell), int(diameter), out

def plot_clustering_vs_degree(G: nx.Graph, name: str) -> Path:
    """Plota C(k): clusterização média por grau em escala log–log e salva em figs/."""
    H = G.to_undirected() if G.is_directed() else G
    c_local = nx.clustering(H)
    degree_to_c = defaultdict(list)
    for node, c in c_local.items():
        k = H.degree(node)
        degree_to_c[k].append(c)
    ks = sorted(degree_to_c.keys())
    ck = [float(np.mean(degree_to_c[k])) for k in ks]
    plt.figure(figsize=(6,4))
    plt.scatter(ks, ck, s=10, alpha=0.7)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Grau (k)')
    plt.ylabel('Clusterização média C(k)')
    plt.title(f'C(k) - Clusterização média por grau - {name}')
    out = FIG_DIR / f'{name}_clustering_ck.png'
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out

def average_distance_all_components(G: nx.Graph, max_nodes_exact: int = 200000, sample_per_component: int = 100) -> float:
    """Distância média agregada em TODAS as componentes; exata em componentes pequenas e amostrada nas grandes."""
    H = G.to_undirected(as_view=True) if G.is_directed() else G
    comps = list(nx.connected_components(H))
    if not comps:
        return np.nan
    total_sum = 0.0
    total_pairs = 0
    for comp in comps:
        Hc = H.subgraph(comp).copy()
        n = Hc.number_of_nodes()
        if n <= 1:
            continue
        if n <= max_nodes_exact:
            # todas as distâncias
            for _, dist_dict in nx.all_pairs_shortest_path_length(Hc):
                for d in dist_dict.values():
                    if d > 0:
                        total_sum += d
                        total_pairs += 1
        else:
            # amostra por componente
            k = min(sample_per_component, n)
            seeds = sample(list(Hc.nodes()), k)
            for s in seeds:
                lengths = nx.single_source_shortest_path_length(Hc, s)
                vals = [d for d in lengths.values() if d > 0]
                total_sum += float(np.sum(vals))
                total_pairs += len(vals)
    if total_pairs == 0:
        return np.nan
    return total_sum / total_pairs

def summarize_network(G, name, estimate_dist=True):
    """Resumo de métricas básicas para um grafo G identificado por name."""
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
        summary['ell_all_components'] = average_distance_all_components(G)
    return summary

def compute_degree_summary(G: nx.Graph) -> dict:
    """Nó(s) de maior grau (in/out para dirigidos; total para não dirigidos)."""
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

def draw_graph_snapshot(G: nx.Graph, name: str, max_nodes: int = 1000) -> Path | None:
    """
    Desenha um snapshot simples do grafo (amostra de até max_nodes) e salva em figs/.
    Útil para visualização rápida; não é layout de alta qualidade.
    """
    H = G
    if G.number_of_nodes() > max_nodes:
        H = G.subgraph(sample(list(G.nodes()), max_nodes)).copy()
    try:
        pos = nx.spring_layout(H, seed=42, k=None)
    except Exception:
        pos = None
    plt.figure(figsize=(6,5))
    nx.draw_networkx(H, pos=pos, with_labels=False, node_size=5, width=0.2)
    plt.title(f"Snapshot do grafo - {name}")
    out = FIG_DIR / f"{name}_graph_snapshot.png"
    plt.tight_layout()
    plt.savefig(out, dpi=150)
    plt.close()
    return out

# Atualiza para aceitar resumos de grau e explicar NaN em k_in/k_out
def build_markdown_report(df: pd.DataFrame, degree_info: dict | None = None, artifacts: dict | None = None) -> str:
    """
    Gera relatório em Markdown com métricas e artefatos.
    """
    lines = []
    lines.append("## Relatório de Métricas de Redes\n")
    lines.append("Este relatório resume métricas básicas calculadas para cada rede, com breves explicações.\n")
    lines.append("\n")
    lines.append("### Métricas e definições\n")
    lines.append("- **name**: nome do dataset.\n")
    lines.append("- **directed**: se a rede é direcionada (True) ou não direcionada (False).\n")
    lines.append("- **n**: número de nós (|V|).\n")
    lines.append("- **l**: número de arestas (|E|).\n")
    lines.append("- **density**: densidade do grafo (fração de pares conectados).\n")
    lines.append("- **k** / **k_in** / **k_out**: grau médio. Em não direcionados: k = 2m/n. Em direcionados: k_in = k_out = m/n.\n")
    lines.append("- **S_largest_component**: fração de nós na maior componente (em dirigidos, componente fracamente conexa).\n")
    lines.append("- **C_avg_clustering**: coeficiente de agrupamento médio (para dirigidos, do grafo não-direcionado equivalente).\n")
    lines.append("- **r_assortatividade**: assortatividade por grau.\n")
    if 'ell_all_components' in df.columns:
        lines.append("- **ell_all_components**: distância média agregada em TODAS as componentes (exata por componente pequena; amostrada nas grandes).\n")
    if 'ell_gcc_exact' in df.columns:
        lines.append("- **ell_gcc_exact**: distância média exata na CCG (se n_gcc ≤ limite).\n")
    if 'diameter_gcc' in df.columns:
        lines.append("- **diameter_gcc**: diâmetro exato da CCG (se n_gcc ≤ limite).\n")
    lines.append("\n")
    lines.append("### Observações\n")
    lines.append("- Em redes não direcionadas, **k_in** e **k_out** não se aplicam. Por isso, ao combinar resultados com redes dirigidas, essas colunas podem aparecer como NaN — isso é esperado.\n")
    lines.append("- **C = 0** indica ausência de triângulos (vizinhos não se conectam entre si), não necessariamente que um nó não tenha vizinhos.\n")
    lines.append("\n")
    lines.append("### Resultados\n")
    lines.append(df.to_markdown(index=False))
    lines.append("\n")
    if artifacts:
        lines.append("### Figuras\n")
        for name, arts in artifacts.items():
            for label, path in arts.items():
                if path is not None:
                    rel = Path(path).relative_to(BASE_DIR)
                    lines.append(f"![{name} – {label}]({rel})")
        lines.append("\n")
    lines.append("### Conclusões\n")
    for _, row in df.iterrows():
        name = row['name']
        directed = row['directed']
        C = row.get('C_avg_clustering', np.nan)
        r = row.get('r_assortativity', np.nan)
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

WWW_EDGES = 'data/www.edgelist.txt'   
PPI_EDGES = 'data/protein.edgelist.txt'         

G_www = load_edgelist(WWW_EDGES, directed=True, sep='\s+') ##direcionada
G_ppi = load_edgelist(PPI_EDGES, directed=False, sep='\s+') ##nao direcionada

res = []
res.append(summarize_network(G_www, 'WWW'))
res.append(summarize_network(G_ppi, 'Protein_Interactions'))

df = pd.DataFrame(res)
# preparar resumos de grau e adicionar colunas ao DataFrame
_degree_info = {
    'WWW': compute_degree_summary(G_www),
    'Protein_Interactions': compute_degree_summary(G_ppi),
}
for col in ['max_in_node','max_in_deg','max_out_node','max_out_deg','max_node','max_deg']:
    df[col] = df['name'].map(lambda nm: _degree_info.get(nm, {}).get(col, np.nan))


# Componentes e métricas exatas (auto-fallback se CCG muito grande)
artifacts = {}
for name, G in [('WWW', G_www), ('Protein_Interactions', G_ppi)]:
    # figuras
    deg_plot = plot_degree_distribution(G, name)
    ck_plot = plot_clustering_vs_degree(G, name)
    snap_plot = draw_graph_snapshot(G, name)
    sizes, giant = get_components_info(G)
    ell_exact, diam_gcc, dist_plot = distances_metrics_on_gcc(G, name, max_nodes_exact=20000)
    # adicionar colunas por nome
    df.loc[df['name'] == name, 'num_components'] = len(sizes)
    df.loc[df['name'] == name, 'gcc_size'] = (max(sizes) if sizes else 0)
    df.loc[df['name'] == name, 'ell_gcc_exact'] = ell_exact
    df.loc[df['name'] == name, 'diameter_gcc'] = diam_gcc
    # registrar artefatos
    artifacts[name] = {
        'snapshot': snap_plot,
        'degree_loglog': deg_plot,
        'clustering_ck': ck_plot,
        'distance_distribution_gcc': dist_plot
    }

print(df)
# salvar
df.to_csv('metrics_newman_benchmarks.csv', index=False)

# gerar relatório Markdown
report_text = build_markdown_report(df, degree_info=_degree_info, artifacts=artifacts)
with open('metrics_report.md', 'w', encoding='utf-8') as f:
    f.write(report_text)
print("Relatório salvo em metrics_report.md")
