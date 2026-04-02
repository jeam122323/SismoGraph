"""
=============================================================
 SismoGraph — Análise de Impacto Sísmico na Ásia
 Universidade Presbiteriana Mackenzie
 Faculdade de Computação e Informática
 Disciplina: Teoria dos Grafos — Turma 6G
 Professor: Dr. Ivan Carlos Alcântara de Oliveira
=============================================================
 Integrantes:
   Luiz Fernando Ferrari Batistela  — RA: 10427397
   Henrique Jeam Lima               — RA: 10277156
=============================================================
 Descrição:
   Aplicação que modela a propagação e o impacto de terremotos
   na Ásia Oriental, Sudeste Asiático e Ásia Central usando
   Teoria dos Grafos. Os vértices representam cidades e
   epicentros de terremotos reais; as arestas representam
   a intensidade sísmica sentida (escala MMI) entre dois pontos.

 ODS contemplados:
   ODS 11 — Cidades e Comunidades Sustentáveis
   ODS 13 — Ação Climática

 Histórico de alterações:
   2026-03-31 | Luiz Fernando   | Criação inicial do programa
   2026-03-31 | Henrique Jeam   | Revisão e testes do menu
=============================================================
"""

import os
import math
from collections import defaultdict, deque


# ─────────────────────────────────────────────────────────────
# ESTRUTURA DO GRAFO (Lista de Adjacência)
# Baseada no modelo apresentado em aula, adaptada ao projeto
# ─────────────────────────────────────────────────────────────

class Grafo:
    """
    Representa um grafo usando lista de adjacência.
    Suporta os tipos 0 a 7 conforme especificado no enunciado.
    """

    def __init__(self):
        self.tipo        = 0       # tipo do grafo (0-7)
        self.vertices    = {}      # id -> {"rotulo": str, "peso": float}
        self.adj         = defaultdict(list)  # id -> [(vizinho, peso_aresta)]
        self.num_arestas = 0

    def adicionar_vertice(self, vid, rotulo="", peso=0.0):
        """Insere um vértice com rótulo e peso opcionais."""
        if vid in self.vertices:
            print(f"  [!] Vértice {vid} já existe.")
            return False
        self.vertices[vid] = {"rotulo": rotulo, "peso": float(peso)}
        return True

    def remover_vertice(self, vid):
        """Remove o vértice e todas as arestas conectadas a ele."""
        if vid not in self.vertices:
            print(f"  [!] Vértice {vid} não encontrado.")
            return False
        # Remove arestas que envolvem este vértice
        for vizinho, _ in list(self.adj[vid]):
            self.adj[vizinho] = [(v, p) for v, p in self.adj[vizinho] if v != vid]
            self.num_arestas -= 1
        del self.adj[vid]
        del self.vertices[vid]
        return True

    def adicionar_aresta(self, u, v, peso=1.0):
        """Insere uma aresta (e seu inverso se não direcionado)."""
        if u not in self.vertices or v not in self.vertices:
            print(f"  [!] Vértice {u} ou {v} não encontrado.")
            return False
        # Verifica duplicidade
        if any(viz == v for viz, _ in self.adj[u]):
            print(f"  [!] Aresta {u}-{v} já existe.")
            return False
        self.adj[u].append((v, float(peso)))
        if not self._eh_direcionado():
            self.adj[v].append((u, float(peso)))
        self.num_arestas += 1
        return True

    def remover_aresta(self, u, v):
        """Remove a aresta entre u e v."""
        if u not in self.vertices or v not in self.vertices:
            print(f"  [!] Vértice {u} ou {v} não encontrado.")
            return False
        antes = len(self.adj[u])
        self.adj[u] = [(viz, p) for viz, p in self.adj[u] if viz != v]
        if not self._eh_direcionado():
            self.adj[v] = [(viz, p) for viz, p in self.adj[v] if viz != u]
        if len(self.adj[u]) < antes:
            self.num_arestas -= 1
            return True
        print(f"  [!] Aresta {u}-{v} não encontrada.")
        return False

    def _eh_direcionado(self):
        return self.tipo in (4, 5, 6, 7)

    def _tem_peso_vertice(self):
        return self.tipo in (1, 3, 5, 7)

    def _tem_peso_aresta(self):
        return self.tipo in (2, 3, 6, 7)


# ─────────────────────────────────────────────────────────────
# LEITURA E GRAVAÇÃO DO ARQUIVO grafo.txt
# ─────────────────────────────────────────────────────────────

def ler_arquivo(grafo, caminho="grafo.txt"):
    """Lê o arquivo grafo.txt e monta o grafo na memória."""
    if not os.path.exists(caminho):
        print(f"  [!] Arquivo '{caminho}' não encontrado.")
        return False
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [l.strip() for l in f if l.strip()]

        idx = 0
        grafo.__init__()  # reinicia o grafo

        grafo.tipo = int(linhas[idx]); idx += 1
        n = int(linhas[idx]); idx += 1

        for _ in range(n):
            partes = linhas[idx].split('"')
            vid    = int(partes[0].strip())
            rotulo = partes[1] if len(partes) > 1 else ""
            peso   = float(partes[3]) if len(partes) > 3 else 0.0
            grafo.adicionar_vertice(vid, rotulo, peso)
            idx += 1

        m = int(linhas[idx]); idx += 1
        for _ in range(m):
            nums = linhas[idx].split()
            u, v = int(nums[0]), int(nums[1])
            peso = float(nums[2]) if len(nums) > 2 else 1.0
            grafo.adj[u].append((v, peso))
            if not grafo._eh_direcionado():
                grafo.adj[v].append((u, peso))
            grafo.num_arestas += 1
            idx += 1

        print(f"  [✔] Grafo carregado: {n} vértices, {grafo.num_arestas} arestas.")
        return True
    except Exception as e:
        print(f"  [!] Erro ao ler arquivo: {e}")
        return False


def gravar_arquivo(grafo, caminho="grafo.txt"):
    """Grava o grafo da memória RAM para o arquivo grafo.txt."""
    try:
        linhas = []
        linhas.append(str(grafo.tipo))
        linhas.append(str(len(grafo.vertices)))
        for vid in sorted(grafo.vertices):
            v = grafo.vertices[vid]
            linhas.append(f'{vid} "{v["rotulo"]}" "{v["peso"]}"')

        # Conta arestas sem duplicar (para não direcionado)
        arestas_gravadas = set()
        lista_arestas = []
        for u in sorted(grafo.adj):
            for viz, peso in grafo.adj[u]:
                if grafo._eh_direcionado():
                    lista_arestas.append((u, viz, peso))
                else:
                    chave = (min(u, viz), max(u, viz))
                    if chave not in arestas_gravadas:
                        arestas_gravadas.add(chave)
                        lista_arestas.append((u, viz, peso))

        linhas.append(str(len(lista_arestas)))
        for u, v, p in lista_arestas:
            linhas.append(f"{u} {v} {p}")

        with open(caminho, "w", encoding="utf-8") as f:
            f.write("\n".join(linhas))
        print(f"  [✔] Grafo gravado em '{caminho}' com sucesso.")
        return True
    except Exception as e:
        print(f"  [!] Erro ao gravar arquivo: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# EXIBIÇÃO
# ─────────────────────────────────────────────────────────────

def mostrar_conteudo(grafo):
    """Exibe o conteúdo do grafo de forma visual e atraente (opção g)."""
    TIPOS = {
        0: "Não orientado — sem peso",
        1: "Não orientado — peso no vértice",
        2: "Não orientado — peso na aresta",
        3: "Não orientado — peso em vértices e arestas",
        4: "Orientado — sem peso",
        5: "Orientado — peso no vértice",
        6: "Orientado — peso na aresta",
        7: "Orientado — peso em vértices e arestas",
    }
    sep = "─" * 60
    print(f"\n{'═'*60}")
    print(f"  SismoGraph — Conteúdo do Grafo")
    print(f"{'═'*60}")
    print(f"  Tipo   : {grafo.tipo} → {TIPOS.get(grafo.tipo,'?')}")
    print(f"  Vértices: {len(grafo.vertices)}")
    print(f"  Arestas : {grafo.num_arestas}")
    print(f"{sep}")

    # Vértices
    print(f"  {'ID':<5} {'Rótulo':<25} {'Tipo':<12} {'Peso'}")
    print(f"  {'-'*5} {'-'*25} {'-'*12} {'-'*6}")
    for vid in sorted(grafo.vertices):
        v   = grafo.vertices[vid]
        tp  = "Epicentro" if vid >= 40 else "Cidade"
        pw  = f"{v['peso']}" if grafo._tem_peso_vertice() else "—"
        print(f"  {vid:<5} {v['rotulo']:<25} {tp:<12} {pw}")

    # Arestas (primeiras 20 para não poluir)
    print(f"\n{sep}")
    print(f"  Arestas (exibindo primeiras 20 de {grafo.num_arestas}):")
    print(f"  {'Origem':<6} {'Destino':<6} {'MMI (peso)'}")
    print(f"  {'-'*6} {'-'*6} {'-'*10}")
    exibidas = set()
    count = 0
    for u in sorted(grafo.adj):
        for viz, peso in grafo.adj[u]:
            chave = (min(u,viz), max(u,viz))
            if chave not in exibidas:
                exibidas.add(chave)
                ru = grafo.vertices[u]["rotulo"][:14]
                rv = grafo.vertices[viz]["rotulo"][:14]
                print(f"  {ru:<16} ↔  {rv:<16}  {peso}")
                count += 1
                if count >= 20:
                    print(f"  ... (e mais {grafo.num_arestas - 20} arestas no grafo.txt)")
                    break
        if count >= 20:
            break
    print(f"{'═'*60}\n")


def mostrar_grafo(grafo):
    """Exibe o grafo como lista de adjacência (opção h)."""
    print(f"\n{'═'*60}")
    print(f"  Lista de Adjacência — SismoGraph")
    print(f"{'═'*60}")
    for vid in sorted(grafo.vertices):
        rotulo = grafo.vertices[vid]["rotulo"]
        vizinhos = grafo.adj[vid]
        if vizinhos:
            viz_str = ", ".join(
                f"{grafo.vertices[v]['rotulo'][:12]}({p})"
                for v, p in sorted(vizinhos, key=lambda x: -x[1])[:5]
            )
            if len(vizinhos) > 5:
                viz_str += f" ... +{len(vizinhos)-5}"
        else:
            viz_str = "—"
        print(f"  [{vid:>2}] {rotulo:<20} → {viz_str}")
    print(f"{'═'*60}\n")


# ─────────────────────────────────────────────────────────────
# CONEXIDADE
# ─────────────────────────────────────────────────────────────

def _bfs(grafo, inicio, visitados):
    """BFS para percorrer componentes."""
    fila = deque([inicio])
    visitados.add(inicio)
    componente = [inicio]
    while fila:
        u = fila.popleft()
        for v, _ in grafo.adj[u]:
            if v not in visitados:
                visitados.add(v)
                fila.append(v)
                componente.append(v)
    return componente


def _dfs_ordem(grafo, u, visitados, pilha, adj_usado=None):
    """DFS para ordenação topológica (Kosaraju)."""
    visitados.add(u)
    adj = adj_usado if adj_usado else grafo.adj
    for v, _ in adj[u]:
        if v not in visitados:
            _dfs_ordem(grafo, v, visitados, pilha, adj_usado)
    pilha.append(u)


def _grafo_transposto(grafo):
    """Retorna a lista de adjacência do grafo transposto."""
    trans = defaultdict(list)
    for u in grafo.adj:
        for v, p in grafo.adj[u]:
            trans[v].append((u, p))
    return trans


def conexidade(grafo):
    """
    Analisa a conexidade do grafo (opção i).
    - Não direcionado: conexo ou desconexo + componentes
    - Direcionado: C0/C1/C2/C3 + grafo reduzido via Kosaraju
    """
    print(f"\n{'═'*60}")
    print(f"  Análise de Conexidade — SismoGraph")
    print(f"{'═'*60}")
    ids = list(grafo.vertices.keys())

    if not grafo._eh_direcionado():
        # ── Grafo não direcionado ──────────────────────────────
        visitados = set()
        componentes = []
        for vid in ids:
            if vid not in visitados:
                comp = _bfs(grafo, vid, visitados)
                componentes.append(comp)

        if len(componentes) == 1:
            print(f"  Resultado : CONEXO")
            print(f"  O grafo possui uma única componente com {len(ids)} vértices.")
        else:
            print(f"  Resultado : DESCONEXO")
            print(f"  Componentes conexas encontradas: {len(componentes)}")
            for i, comp in enumerate(componentes):
                rotulos = [grafo.vertices[v]["rotulo"] for v in comp[:4]]
                mais = f" ... +{len(comp)-4}" if len(comp) > 4 else ""
                print(f"  Componente {i+1} ({len(comp)} vértices): {', '.join(rotulos)}{mais}")
    else:
        # ── Grafo direcionado — Kosaraju (FCONEX) ─────────────
        # Passo 1: DFS no grafo original → pilha de finalização
        visitados = set()
        pilha = []
        for vid in ids:
            if vid not in visitados:
                _dfs_ordem(grafo, vid, visitados, pilha)

        # Passo 2: DFS no grafo transposto na ordem inversa da pilha
        trans = _grafo_transposto(grafo)
        visitados2 = set()
        sccs = []
        while pilha:
            u = pilha.pop()
            if u not in visitados2:
                comp = []
                _dfs_ordem_lista(trans, u, visitados2, comp)
                sccs.append(comp)

        # Classifica conexidade
        tem_scc_maior_1 = any(len(s) > 1 for s in sccs)
        if len(sccs) == 1:
            cat = "C3 — Fortemente conexo"
        elif all(len(s) == 1 for s in sccs):
            cat = "C1 — Fracamente conexo (sem SCC com mais de 1 vértice)"
        elif tem_scc_maior_1:
            cat = "C2 — Unilateralmente conexo"
        else:
            cat = "C0 — Não conexo"

        print(f"  Categoria  : {cat}")
        print(f"  SCCs encontradas: {len(sccs)}")
        print(f"\n  Grafo Reduzido (cada SCC = 1 super-nó):")
        for i, scc in enumerate(sccs[:10]):
            rotulos = [grafo.vertices[v]["rotulo"][:10] for v in scc[:3]]
            mais = f"+{len(scc)-3}" if len(scc) > 3 else ""
            print(f"  SCC-{i}: {{{', '.join(rotulos)}{mais}}}")
        if len(sccs) > 10:
            print(f"  ... e mais {len(sccs)-10} SCCs")

    print(f"{'═'*60}\n")


def _dfs_ordem_lista(adj, u, visitados, resultado):
    """DFS iterativa para o grafo transposto (evita recursão profunda)."""
    pilha = [u]
    while pilha:
        v = pilha[-1]
        if v not in visitados:
            visitados.add(v)
            resultado.append(v)
        expandiu = False
        for viz, _ in adj.get(v, []):
            if viz not in visitados:
                pilha.append(viz)
                expandiu = True
                break
        if not expandiu:
            pilha.pop()


# ─────────────────────────────────────────────────────────────
# MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────

def menu_inserir_vertice(grafo):
    print("\n── Inserir Vértice ──")
    try:
        vid    = int(input("  ID do vértice: "))
        rotulo = input("  Rótulo (nome): ").strip()
        peso   = float(input("  Peso (0 se não aplicável): ") or 0)
        if grafo.adicionar_vertice(vid, rotulo, peso):
            print(f"  [✔] Vértice '{rotulo}' (ID {vid}) inserido.")
    except ValueError:
        print("  [!] Entrada inválida.")


def menu_inserir_aresta(grafo):
    print("\n── Inserir Aresta ──")
    try:
        u    = int(input("  ID vértice origem : "))
        v    = int(input("  ID vértice destino: "))
        peso = float(input("  Peso da aresta (MMI): ") or 1.0)
        if grafo.adicionar_aresta(u, v, peso):
            print(f"  [✔] Aresta {u} ↔ {v} (peso {peso}) inserida.")
    except ValueError:
        print("  [!] Entrada inválida.")


def menu_remover_vertice(grafo):
    print("\n── Remover Vértice ──")
    try:
        vid = int(input("  ID do vértice a remover: "))
        if grafo.remover_vertice(vid):
            print(f"  [✔] Vértice {vid} removido.")
    except ValueError:
        print("  [!] Entrada inválida.")


def menu_remover_aresta(grafo):
    print("\n── Remover Aresta ──")
    try:
        u = int(input("  ID vértice origem : "))
        v = int(input("  ID vértice destino: "))
        if grafo.remover_aresta(u, v):
            print(f"  [✔] Aresta {u} ↔ {v} removida.")
    except ValueError:
        print("  [!] Entrada inválida.")


def exibir_menu():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║       SismoGraph — Análise de Impacto Sísmico na Ásia        ║
║   Luiz Fernando Ferrari Batistela  ·  RA 10427397            ║
║   Henrique Jeam Lima               ·  RA 10277156            ║
╠══════════════════════════════════════════════════════════════╣
║  a) Ler dados do arquivo grafo.txt                           ║
║  b) Gravar dados no arquivo grafo.txt                        ║
║  c) Inserir vértice                                          ║
║  d) Inserir aresta                                           ║
║  e) Remover vértice                                          ║
║  f) Remover aresta                                           ║
║  g) Mostrar conteúdo do arquivo                              ║
║  h) Mostrar grafo (lista de adjacência)                      ║
║  i) Apresentar conexidade e grafo reduzido                   ║
║  j) Encerrar aplicação                                       ║
╚══════════════════════════════════════════════════════════════╝""")


def main():
    grafo = Grafo()
    while True:
        exibir_menu()
        opcao = input("  Opção: ").strip().lower()

        if opcao == 'a':
            caminho = input("  Caminho do arquivo [grafo.txt]: ").strip() or "grafo.txt"
            ler_arquivo(grafo, caminho)

        elif opcao == 'b':
            caminho = input("  Caminho do arquivo [grafo.txt]: ").strip() or "grafo.txt"
            gravar_arquivo(grafo, caminho)

        elif opcao == 'c':
            menu_inserir_vertice(grafo)

        elif opcao == 'd':
            menu_inserir_aresta(grafo)

        elif opcao == 'e':
            menu_remover_vertice(grafo)

        elif opcao == 'f':
            menu_remover_aresta(grafo)

        elif opcao == 'g':
            if not grafo.vertices:
                print("  [!] Grafo vazio. Use a opção 'a' para carregar o arquivo.")
            else:
                mostrar_conteudo(grafo)

        elif opcao == 'h':
            if not grafo.vertices:
                print("  [!] Grafo vazio. Use a opção 'a' para carregar o arquivo.")
            else:
                mostrar_grafo(grafo)

        elif opcao == 'i':
            if not grafo.vertices:
                print("  [!] Grafo vazio. Use a opção 'a' para carregar o arquivo.")
            else:
                conexidade(grafo)

        elif opcao == 'j':
            print("\n  Encerrando SismoGraph. Até logo!\n")
            break

        else:
            print("  [!] Opção inválida. Digite uma letra de 'a' a 'j'.")


if __name__ == "__main__":
    main()
