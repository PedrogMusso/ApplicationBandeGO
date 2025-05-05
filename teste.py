# --- Função para extrair info MNA da lista de componentes ---
def count_mna_info(componentes):
    """
    Percorre a lista de componentes para determinar o número máximo de nó
    e contar as ocorrências de cada tipo de componente que adiciona
    variáveis MNA, além de mapeá-las.

    Args:
        componentes (list): Lista de componentes retornada por criarListaComponentes.
        Assume-se que os dados já estão nos tipos corretos (int para nós, float para valores).

    Returns:
        tuple: (n_max_node, mna_counts, comp_indices)
               - n_max_node (int): O maior número de nó encontrado.
               - mna_counts (dict): Contagens de {'V': NV, 'E': NE, 'H': NH, 'B': NB, 'F': NF}.
                                    Estas contagens determinam o número de variáveis/equações MNA extras.
               - comp_indices (dict): Mapeamento {tipo: {nome_comp: indice_nesse_tipo}}.
    """
    n_max_node = 0
    # Contadores para componentes que adicionam variáveis ou equações de restrição/definição MNA
    mna_counts = {'V': 0, 'E': 0, 'H': 0, 'B': 0, 'F': 0}
    # Mapeamento para saber qual instância de um tipo de componente estamos tratando (0, 1, 2...)
    comp_indices = {'V': {}, 'E': {}, 'H': {}, 'B': {}, 'F': {}}

    for componente in componentes:
        comp_name = componente[0]
        comp_type = comp_name[0].upper()

        # 1. Encontrar o nó máximo
        # Percorre todos os parâmetros após o nome
        for param in componente[1:]:
            if isinstance(param, int): # Se o parâmetro é um número inteiro, é um nó
                if param > n_max_node:
                    n_max_node = param

        # 2. Contar componentes MNA e mapear índices
        if comp_type in mna_counts:
             # Componentes que adicionam variáveis MNA ou restrições diretas
             comp_indices[comp_type][comp_name] = mna_counts[comp_type]
             mna_counts[comp_type] += 1

    # Contamos V, E, B, F, H. Cada F ou H adiciona 2 variáveis/equações extras (fonte + controle)
    # As contagens em mna_counts já são o número de fontes de cada tipo.

    return n_max_node, mna_counts, comp_indices


# --- Função para construir Matriz e Vetor MNA ---
def insert_mna_stamps(n_max_node, mna_counts, componentes, comp_indices):
    """
    Constrói a matriz MNA (A) e o vetor RHS (b) do sistema de equações MNA.

    Args:
        n_max_node (int): O maior número de nó.
        mna_counts (dict): Contagens de tipos de componentes MNA (V,E,H,B,F).
                           Usado para calcular o tamanho do sistema e offsets.
        componentes (list): Lista de componentes retornada por criarListaComponentes.
        comp_indices (dict): Mapeamento de nomes de componentes para índices dentro de seus tipos.

    Returns:
        tuple: (A, b)
               - A (numpy.ndarray): A matriz MNA.
               - b (numpy.ndarray): O vetor RHS MNA.
    """
    num_nodes = n_max_node + 1 # Total de nós incluindo o nó 0

    # --- Calcula o número total de variáveis e o tamanho do sistema ---
    # Variáveis = Tensões de nó (num_nodes) + Correntes MNA
    # Correntes MNA = Correntes de fontes V, E, B(ief), F_src, H_src, F_ctrl, H_ctrl
    # Número de correntes: NV + NE + NB + NF + NH + NF + NH
    num_extra_vars = (mna_counts['V'] + mna_counts['E'] + mna_counts['B'] +
                      mna_counts['F'] + mna_counts['H'] + # Correntes das fontes V, E, B(ief), F, H
                      mna_counts['F'] + mna_counts['H']) # Correntes de controle (F e H) - uma por F/H

    system_size = num_nodes + num_extra_vars

    # Inicializa a matriz MNA e o vetor RHS
    A = np.zeros([system_size, system_size])
    b = np.zeros([system_size, 1])

    # --- Define os offsets para os blocos da matriz A e b e para os tipos de variáveis/equações ---
    # Estes offsets definem onde cada tipo de variável (coluna) e cada tipo de equação (linha) começa
    # no sistema A*x = b.
    # Ordem das variáveis em x: [V_0...V_n_max, I_V1..., I_E1..., I_B_ief1..., I_F_src1..., I_H_src1..., I_F_ctrl1..., I_H_ctrl1...]
    # Ordem das equações (linhas): [KCL@0...KCL@n_max, V_constr1..., E_constr1..., B_constr1..., F_src_def1..., H_src_def1..., F_ctrl_def1..., H_ctrl_def1...]

    node_volt_offset = 0 # Tensões de nó V0 a Vn_max estão nas primeiras `num_nodes` posições/equações

    # Offsets de Colunas (Variáveis MNA extras no vetor solução x)
    v_curr_col_offset = num_nodes
    e_curr_col_offset = v_curr_col_offset + mna_counts['V']
    b_ief_curr_col_offset = e_curr_col_offset + mna_counts['E']
    f_src_curr_col_offset = b_ief_curr_col_offset + mna_counts['B']
    h_src_curr_col_offset = f_src_curr_col_offset + mna_counts['F']
    f_ctrl_curr_col_offset = h_src_curr_col_offset + mna_counts['H']
    h_ctrl_curr_col_offset = f_ctrl_curr_col_offset + mna_counts['F'] # Offset + #F_cc (que é igual a #F)


    # Offsets de Linhas (Equações MNA extras na matriz A / vetor b)
    kcl_row_offset = 0 # Equações KCL para nós 0 a n_max_node estão nas primeiras `num_nodes` linhas

    # Offsets das linhas de restrição/definição:
    v_constr_row_offset = num_nodes # Equações para V(n+)-V(n-)=Value
    e_constr_row_offset = v_constr_row_offset + mna_counts['V'] # Equações para V(n+)-V(n-)=Av*V_control
    b_constr_row_offset = e_constr_row_offset + mna_counts['E'] # Equações para V(ne)-V(nf)=... (B)
    f_src_def_row_offset = b_constr_row_offset + mna_counts['B'] # Equações para I_F_src - Beta*I_control = 0
    h_src_def_row_offset = f_src_def_row_offset + mna_counts['F'] # Equações para V_H_src - Rm*I_control = 0
    f_ctrl_def_row_offset = h_src_def_row_offset + mna_counts['H'] # Equações para V(nCc)-V(nCd)=0 (para F)
    h_ctrl_def_row_offset = f_ctrl_def_row_offset + mna_counts['F'] # Equações para V(nCc)-V(nCd)=0 (para H)


    # --- Insere as Estampas MNA para cada componente ---
    for elemento in componentes:
        comp_name = elemento[0]
        comp_type = comp_name[0].upper()

        # Note: Índices de nó (0 a n_max_node) correspondem diretamente aos índices de linha/coluna
        # no bloco de tensões de nó da matriz/vetor MNA (offsets 0 a num_nodes-1).

        if comp_type == 'R': # R<id> n1 n2 valorR
            n1, n2, valorR = elemento[1], elemento[2], elemento[3]
            # Não verifica R=0 aqui, deixa para np.linalg.solve falhar se causar singularidade

            condutancia = 1.0 / valorR
            # Estampa NA no bloco G (top-left A) - KCL rows
            A[n1][n1] += condutancia
            A[n1][n2] -= condutancia
            A[n2][n1] -= condutancia
            A[n2][n2] += condutancia

        elif comp_type == 'I': # I<id> n1 n2 valorI (ignora 'DC')
            n1, n2, valorI = elemento[1], elemento[2], elemento[3] # Valor está na posição 3
            # Estampa NA no vetor I_s (top-right b) - KCL rows
            # Corrente saindo de n1 (+) e entrando em n2 (-) na netlist -> injeta em n2, drena de n1
            b[n1][0] -= valorI # RHS da KCL em n1
            b[n2][0] += valorI # RHS da KCL em n2

        elif comp_type == 'G': # G<id> nI1 nI2 nVp nVn Gm
             nI1, nI2, nVp, nVn, gm = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             # Estampa VCCS no bloco G (top-left A) - KCL rows
             # Corrente Gm*(V(nVp) - V(nVn)) saindo de nI1 (entrando em nI2)
             A[nI1][nVp] += gm
             A[nI1][nVn] -= gm
             A[nI2][nVp] -= gm
             A[nI2][nVn] += gm

        elif comp_type == 'V': # V<id> n+ n- valorV (ignora 'DC')
            np, nm, valorV = elemento[1], elemento[2], elemento[3] # Valor na posição 3
            v_idx = comp_indices['V'][comp_name] # Índice desta fonte V (0, 1, 2...)

            # Índice da variável de corrente desta fonte V (na parte das correntes MNA do vetor x)
            v_curr_var_col = v_curr_col_offset + v_idx
            # Índice da linha da equação de restrição de tensão para esta fonte V
            v_constr_eq_row = v_constr_row_offset + v_idx

            # Estampa MNA para fonte de tensão V (KCL rows e Constraint row)
            # KCL em n+: Adiciona +1 na coluna da corrente da fonte V (corrente saindo do nó)
            A[np][v_curr_var_col] += 1
            # KCL em n-: Adiciona -1 na coluna da corrente da fonte V (corrente entrando no nó)
            A[nm][v_curr_var_col] -= 1

            # Equação de Restrição de Tensão: V(n+) - V(n-) = ValorV. Linha é v_constr_eq_row
            A[v_constr_eq_row][np] += 1 # Coeficiente para V(n+)
            A[v_constr_eq_row][nm] -= 1 # Coeficiente para V(n-)
            b[v_constr_eq_row][0] += valorV # RHS é o valor da fonte

        elif comp_type == 'E': # E<id> n+ n- nCp nCn Av
             np, nm, nCp, nCn, av = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             e_idx = comp_indices['E'][comp_name] # Índice desta fonte E

             # Índice da variável de corrente desta fonte E e linha da restrição
             e_curr_var_col = e_curr_col_offset + e_idx
             e_constr_eq_row = e_constr_row_offset + e_idx

             # Estampa MNA para VCVS E (KCL rows e Constraint row)
             # KCL em n+: Adiciona +1 na coluna da corrente da fonte E
             A[np][e_curr_var_col] += 1
             # KCL em n-: Adiciona -1 na coluna da corrente da fonte E
             A[nm][e_curr_var_col] -= 1

             # Equação de Restrição de Tensão: V(n+) - V(n-) - Av * (V(nCp) - V(nCn)) = 0. Linha é e_constr_eq_row
             A[e_constr_eq_row][np] += 1
             A[e_constr_eq_row][nm] -= 1
             A[e_constr_eq_row][nCp] -= av
             A[e_constr_eq_row][nCn] += av

        elif comp_type == 'F': # F<id> nI+ nI- nCc nCd B (Beta)
             nIplus, nIminus, nCc, nCd, beta = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             f_idx = comp_indices['F'][comp_name] # Índice desta fonte F

             # Índices das duas variáveis MNA extras para esta fonte F (corrente da fonte F e corrente de controle i_CD)
             f_source_curr_var_col = f_src_curr_col_offset + f_idx
             f_control_curr_var_col = f_ctrl_curr_col_offset + f_idx

             # Índices das duas linhas de equação de restrição para esta fonte F
             # 1) Definição da fonte F: I_source - Beta * I_control = 0
             f_source_def_row = f_src_def_row_offset + f_idx
             # 2) Definição da corrente de controle (V(nCc) - V(nCd) = 0 para o curto)
             f_control_def_row = f_ctrl_def_row_offset + f_idx


             # Estampa MNA para CCCS F
             # KCL em nI+: Adiciona +1 na coluna da corrente da fonte F
             A[nIplus][f_source_curr_var_col] += 1
             # KCL em nI-: Adiciona -1 na coluna da corrente da fonte F
             A[nIminus][f_source_curr_var_col] -= 1
             # KCL em nCc: Adiciona -1 na coluna da corrente de controle (corrente saindo de nCc)
             A[nCc][f_control_curr_var_col] -= 1
             # KCL em nCd: Adiciona +1 na coluna da corrente de controle (corrente entrando em nCd)
             A[nCd][f_control_curr_var_col] += 1

             # Equação 1 (Definição da Fonte F): I_source - Beta * I_control = 0. Linha é f_source_def_row
             A[f_source_def_row][f_source_curr_var_col] += 1 # Coeficiente para I_source
             A[f_source_def_row][f_control_curr_var_col] -= beta # Coeficiente para I_control

             # Equação 2 (Definição da Corrente de Controle): V(nCc) - V(nCd) = 0. Linha é f_control_def_row
             A[f_control_def_row][nCc] += 1 # Coeficiente para V(nCc)
             A[f_control_def_row][nCd] -= 1 # Coeficiente para V(nCd)


        elif comp_type == 'H': # H<id> nV+ nV- nCc nCd Rm
             nVplus, nVminus, nCc, nCd, rm = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             h_idx = comp_indices['H'][comp_name] # Índice desta fonte H

             # Índices das duas variáveis MNA extras para esta fonte H (corrente da fonte H e corrente de controle i_CD)
             h_source_curr_var_col = h_src_curr_col_offset + h_idx
             h_control_curr_var_col = h_ctrl_curr_col_offset + h_idx

             # Índices das duas linhas de equação de restrição para esta fonte H
             # 1) Definição da fonte H: V_source - Rm * I_control = 0
             h_source_def_row = h_src_def_row_offset + h_idx
             # 2) Definição da corrente de controle (V(nCc) - V(nCd) = 0 para o curto)
             h_control_def_row = h_ctrl_def_row_offset + h_idx

             # Estampa MNA para CCVS H
             # KCL em nV+: Adiciona +1 na coluna da corrente da fonte H
             A[nVplus][h_source_curr_var_col] += 1
             # KCL em nV-: Adiciona -1 na coluna da corrente da fonte H
             A[nVminus][h_source_curr_var_col] -= 1
             # KCL em nCc: Adiciona -1 na coluna da corrente de controle
             A[nCc][h_control_curr_var_col] -= 1
             # KCL em nCd: Adiciona +1 na coluna da corrente de controle
             A[nCd][h_control_curr_var_col] += 1

             # Equação 1 (Definição da Fonte H): V(nV+) - V(nV-) - Rm * I_control = 0. Linha é h_source_def_row
             A[h_source_def_row][nVplus] += 1
             A[h_source_def_row][nVminus] -= 1
             A[h_source_def_row][h_control_curr_var_col] -= rm # Coeficiente para I_control

             # Equação 2 (Definição da Corrente de Controle): V(nCc) - V(nCd) = 0. Linha é h_control_def_row
             A[h_control_def_row][nCc] += 1
             A[h_control_def_row][nCd] -= 1

        elif comp_type == 'A': # A<id> na nb nc nd k1 k2 k3 k4 k5 (4 terminais)
             na, nb, nc, nd, k1, k2, k3, k4, k5 = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5], elemento[6], elemento[7], elemento[8], elemento[9]

             # Arbitrário A não adiciona variáveis/equações MNA extras por si só.
             # Suas equações contribuem para as linhas KCL dos nós a,b,c,d.
             # Equações: i_ab = k1*v_ab + k2*v_cd + k3 ; i_cd = k4*v_ab + k5*v_cd
             # v_ab = V(na) - V(nb) ; v_cd = V(nc) - V(nd)
             # i_ab sai na, entra nb ; i_cd sai nc, entra nd

             # KCL em na (+i_ab): +(k1(Va-Vb) + k2(Vc-Vd) + k3) ... = 0
             A[na][na] += k1
             A[na][nb] -= k1
             A[na][nc] += k2
             A[na][nd] -= k2
             b[na][0] -= k3 # k3 termo constante no RHS

             # KCL em nb (-i_ab): -(k1(Va-Vb) + k2(Vc-Vd) + k3) ... = 0
             A[nb][na] -= k1
             A[nb][nb] += k1
             A[nb][nc] -= k2
             A[nb][nd] += k2
             b[nb][0] += k3 # -k3 termo constante no RHS

             # KCL em nc (+i_cd): +(k4(Va-Vb) + k5(Vc-Vd)) ... = 0
             A[nc][na] += k4
             A[nc][nb] -= k4
             A[nc][nc] += k5
             A[nc][nd] -= k5
             # Não tem termo constante na equação i_cd

             # KCL em nd (-i_cd): -(k4(Va-Vb) + k5(Vc-Vd)) ... = 0
             A[nd][na] -= k4
             A[nd][nb] += k4
             A[nd][nc] -= k5
             A[nd][nd] += k5
             # Não tem termo constante na equação i_cd

        elif comp_type == 'B': # B<id> na nb nc nd ne nf k1 k2 k3 k4 k5 k6 k7 k8 (6 terminais)
             na, nb, nc, nd, ne, nf = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5], elemento[6]
             k1, k2, k3, k4, k5, k6, k7, k8 = elemento[7], elemento[8], elemento[9], elemento[10], elemento[11], elemento[12], elemento[13], elemento[14]
             b_idx = comp_indices['B'][comp_name] # Índice desta fonte B

             # Índice da variável MNA extra para esta fonte B (corrente i_ef)
             b_ief_var_col = b_ief_curr_col_offset + b_idx
             # Índice da linha de equação de restrição para esta fonte B (v_ef definição)
             b_vef_constr_row = b_constr_row_offset + b_idx

             # Equações:
             # 1) i_ab = k1*v_ab + k2*i_ef  (i_ab sai na, entra nb)
             # 2) i_cd = k3*v_ab + k4*v_cd + k5 (i_cd sai nc, entra nd)
             # 3) v_ef = k6*v_ab + k7*v_cd + k8 (v_ef = V(ne) - V(nf))
             # v_ab = V(na) - V(nb) ; v_cd = V(nc) - V(nd) ; i_ef = I_B_ief_var

             # KCL em na (+i_ab): +(k1(Va-Vb) + k2*I_B_ief_var) ... = 0
             A[na][na] += k1
             A[na][nb] -= k1
             A[na][b_ief_var_col] += k2 # Coeficiente para i_ef variável

             # KCL em nb (-i_ab): -(k1(Va-Vb) + k2*I_B_ief_var) ... = 0
             A[nb][na] -= k1
             A[nb][nb] += k1
             A[nb][b_ief_var_col] -= k2

             # KCL em nc (+i_cd): +(k3(Va-Vb) + k4(Vc-Vd) + k5) ... = 0
             A[nc][na] += k3
             A[nc][nb] -= k3
             A[nc][nc] += k4
             A[nc][nd] -= k4
             b[nc][0] -= k5 # k5 termo constante no RHS

             # KCL em nd (-i_cd): -(k3(Va-Vb) + k4(Vc-Vd) + k5) ... = 0
             A[nd][na] -= k3
             A[nd][nb] += k3
             A[nd][nc] -= k4
             A[nd][nd] += k4
             b[nd][0] += k5 # -k5 termo constante no RHS

             # KCL em ne (+i_ef): +I_B_ief_var ... = 0
             A[ne][b_ief_var_col] += 1 # Coeficiente para i_ef variável

             # KCL em nf (-i_ef): -I_B_ief_var ... = 0
             A[nf][b_ief_var_col] -= 1 # Coeficiente para i_ef variável

             # Equação de Restrição (v_ef definição): v_ef = k6*v_ab + k7*v_cd + k8
             # (V(ne) - V(nf)) = k6(V(na) - V(nb)) + k7(V(nc) - V(nd)) + k8
             # V(ne) - V(nf) - k6*V(na) + k6*V(nb) - k7*V(nc) + k7*V(nd) = k8. Linha é b_vef_constr_row
             A[b_vef_constr_row][ne] += 1
             A[b_vef_constr_row][nf] -= 1
             A[b_vef_constr_row][na] -= k6
             A[b_vef_constr_row][nb] += k6
             A[b_vef_constr_row][nc] -= k7
             A[b_vef_constr_row][nd] += k7
             b[b_vef_constr_row][0] += k8 # k8 termo constante no RHS


    A[0, :] = 0
    A[0, 0] = 1
    b[0, 0] = 0

    return A, b


def main(netlist_filename):
    """
    Função principal para simular um circuito DC descrito em um arquivo netlist
    usando Análise Nodal Modificada (MNA) e retornar as tensões dos nós
    (exceto o terra).

    Args:
        netlist_filename (str): O nome do arquivo de texto contendo a netlist do circuito.

    Returns:
        numpy.ndarray: Um array do numpy com as tensões nodais calculadas.
                       O elemento na posição i corresponde à tensão do Nó i+1.
                       Retorna None em caso de erro no parseamento ou resolução.
    """
    try:
        componentes = criarListaComponentes(netlist_filename)

    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"ERRO na leitura ou parseamento da netlist: {e}")
        return None

    try:
        n_max_node, mna_counts, comp_indices = count_mna_info(componentes)

    except Exception as e:
        print(f"ERRO inesperado durante a contagem de informações MNA: {e}")
        return None

    try:
        A, b = insert_mna_stamps(n_max_node, mna_counts, componentes, comp_indices)

    except ValueError as e:
         print(f"ERRO de validação durante a construção da matriz MNA: {e}")
         return None
    except Exception as e:
        print(f"ERRO inesperado durante a construção da matriz MNA: {e}")
        return None

    try:
        x = np.linalg.solve(A, b)

    except np.linalg.LinAlgError as e:
        print(f"\nERRO ao resolver o sistema linear MNA: {e}")
        print("Verifique a validade do circuito (singularidades, como loops de V, cortes de I) ou erros na montagem da matriz.")
        return None
    except Exception as e:
         print(f"ERRO inesperado durante a resolução do sistema: {e}")
         return None

    e_nodais = x[1 : n_max_node + 1]

    return e_nodais.flatten()