# AG-Capacitated-Warehouse-Location

Algoritmo Genético para o problema Capacitated Warehouse Location desenvolvido para a disciplina de Pesquisa Operacional, cursada em 2024.2 na Universidade Federal Fluminense.

O Problema de Localização de Depósitos Capacitado tem como objetivo a minimização de custos na logística de localização de depósitos que devem atender a um conjunto de clientes. Esse problema é classificado NP-difícil e pode ser modelado com base nos seguintes parâmetros:

- **C**: um conjunto de clientes que devem ser atendidos.
- **D**: um conjunto de depósitos que podem atender aos clientes.

Nesse contexto, $D$ e $C$ definem os vértices de um grafo bipartido. Nesse grafo, cada aresta $(d, c)$ indica que o depósito $d \in D$ é apto a atender ao cliente $c \in C$. A fim de mensurar demais custos e restrições do problema, são considerados os seguintes parâmetros:

- **$\text{Capacidade}_d$**: a quantidade máxima de recursos para atendimento que o depósito $d \in D$ possui.
- **$\text{Demanda}_c$**: a quantidade de recursos demandados pelo cliente $c \in C$.
- **$\text{Custo-Atendimento}_{dc}$**: o custo para que o depósito $d \in D$ supra integralmente a demanda do cliente $c \in C$.
- **$\text{Custo-Construção}_d$**: o custo de construção de um depósito $d \in D$.

É importante ressaltar que o problema como posto no artigo *An algorithm for solving large capacitated warehouse location problems* permite que um número maior do que um depósito seja necessário para suprir a demanda de um cliente. Nesse contexto, o $Custo\text{-}Atendimento_{dc}$ é contabilizado em função da porção de recursos providos por $d$. Logo, caso um cliente $c$ tenha demanda suprida por mais de um depósito, não se pagará o $\text{Custo-Atendimento}_{dc}$ integralmente para cada um deles, mas o valor equivalente à proporção associada provida por cada um deles.

 Dadas as restrições de que os depósitos não podem ter capacidade excedida e de que cada cliente deve ter sua demanda suprida, busca-se determinar a quantidade de recursos providos pelo depósito $d \in D$ ao cliente $c \in C$, $x_{dc}$, de modo que os custos totais sejam minimizados. Como consequência, decide-se também quais depósitos devem ser construídos, dado que na maioria das vezes não é vantajoso contruir todos. 

Formalmente, considerando que $x_{dc}$ é a variável para a qual deve-se definir valores ótimos nesse problema, a função objetivo é definida do seguinte modo:

$$
\text{Minimizar:} \quad
\text{Função-Objetivo} = \sum_{j=1}^{n_{\text{depósitos}}} \text{Custo-Construção}_j \cdot \text{Depósito-Aberto}_j + \sum_{i=1}^{n_{\text{clientes}}} \sum_{j=1}^{n_{\text{depósitos}}} 
\text{Custo-Atendimento}_{ji} \cdot \frac{x_{ij}}{\text{Demanda}_i}
$$



$$
Depósito\text{-}Aberto_j = 
\begin{cases} 
1, & \text{se, para o j-ésimo depósito, } \sum_{i=1}^{n_{\text{clientes}}} x_{ij} > 0, \\
0, & \text{caso contrário}.
\end{cases}
$$
## Instâncias utilizadas

As instâncias `.txt` foram coletadas da [OR Library](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/capinfo.html). O ótimo associado a elas está presente no arquivo `gabarito.txt`.

## Colaboradores

O trabalho foi realizado em dupla com [Thiago Serra](https://github.com/ThiagoAnorian).
