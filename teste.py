####################################################
# 1a Atividade de Laboratorio de Circuitos Eletricos II
# Periodo: 2025.1
# Nome dos alunos: COMPLETAR
####################################################

import numpy as np


def criarListaComponentes(netlist):
    componentes = []

    with open(netlist, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("*"):
                continue

            listaLinha = linha.split()
            if not listaLinha: continue

            comp_name = listaLinha[0]
            comp_type = comp_name[0].upper()
            componente = [comp_name]

            if comp_type == 'R':
                componente.extend([int(listaLinha[1]), int(listaLinha[2]), float(listaLinha[3])])
            elif comp_type == 'G':
                componente.extend([int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5])])
            elif comp_type == 'I':
                componente.extend([int(listaLinha[1]), int(listaLinha[2]), float(listaLinha[4])])
            elif comp_type == 'V':
                componente.extend([int(listaLinha[1]), int(listaLinha[2]), float(listaLinha[4])])
            elif comp_type == 'E':
                componente.extend([int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5])])
            elif comp_type == 'F':
                componente.extend([int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5])])
            elif comp_type == 'H':
                componente.extend([int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5])])
            elif comp_type == 'A':
                componente.extend([int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]),
                                   float(listaLinha[5]), float(listaLinha[6]), float(listaLinha[7]), float(listaLinha[8]), float(listaLinha[9])])
            elif comp_type == 'B':
                 componente.extend([int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), int(listaLinha[5]), int(listaLinha[6]),
                                    float(listaLinha[7]), float(listaLinha[8]), float(listaLinha[9]), float(listaLinha[10]), float(listaLinha[11]), float(listaLinha[12]), float(listaLinha[13]), float(listaLinha[14])])
            else:
                 pass

            componentes.append(componente)

    return componentes


def count_mna_info(componentes):
    n_max_node = 0
    mna_counts = {'V': 0, 'E': 0, 'H': 0, 'B': 0, 'F': 0}
    comp_indices = {'V': {}, 'E': {}, 'H': {}, 'B': {}, 'F': {}}

    for componente in componentes:
        comp_name = componente[0]
        comp_type = comp_name[0].upper()

        for param in componente[1:]:
            if isinstance(param, int):
                if param > n_max_node:
                    n_max_node = param

        if comp_type in mna_counts:
             comp_indices[comp_type][comp_name] = mna_counts[comp_type]
             mna_counts[comp_type] += 1

    return n_max_node, mna_counts, comp_indices


def insert_mna_stamps(n_max_node, mna_counts, componentes, comp_indices):
    num_nodes = n_max_node + 1

    num_extra_vars = (mna_counts['V'] + mna_counts['E'] + mna_counts['B'] +
                      mna_counts['F'] + mna_counts['H'] +
                      mna_counts['F'] + mna_counts['H'])

    system_size = num_nodes + num_extra_vars

    A = np.zeros([system_size, system_size])
    b = np.zeros([system_size, 1])

    node_volt_offset = 0

    v_curr_col_offset = num_nodes
    e_curr_col_offset = v_curr_col_offset + mna_counts['V']
    b_ief_curr_col_offset = e_curr_col_offset + mna_counts['E']
    f_src_curr_col_offset = b_ief_curr_col_offset + mna_counts['B']
    h_src_curr_col_offset = f_src_curr_col_offset + mna_counts['F']
    f_ctrl_curr_col_offset = h_src_curr_col_offset + mna_counts['H']
    h_ctrl_curr_col_offset = f_ctrl_curr_col_offset + mna_counts['F']


    kcl_row_offset = 0

    v_constr_row_offset = num_nodes
    e_constr_row_offset = v_constr_row_offset + mna_counts['V']
    b_constr_row_offset = e_constr_row_offset + mna_counts['E']
    f_src_def_row_offset = b_constr_row_offset + mna_counts['B']
    h_src_def_row_offset = f_src_def_row_offset + mna_counts['F']
    f_ctrl_def_row_offset = h_src_def_row_offset + mna_counts['H']
    h_ctrl_def_row_offset = f_ctrl_def_row_offset + mna_counts['F']


    for elemento in componentes:
        comp_name = elemento[0]
        comp_type = comp_name[0].upper()

        if comp_type == 'R':
            n1, n2, valorR = elemento[1], elemento[2], elemento[3]
            condutancia = 1.0 / valorR
            A[n1][n1] += condutancia
            A[n1][n2] -= condutancia
            A[n2][n1] -= condutancia
            A[n2][n2] += condutancia

        elif comp_type == 'I':
            n1, n2, valorI = elemento[1], elemento[2], elemento[3]
            b[n1][0] -= valorI
            b[n2][0] += valorI

        elif comp_type == 'G':
             nI1, nI2, nVp, nVn, gm = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             A[nI1][nVp] += gm
             A[nI1][nVn] -= gm
             A[nI2][nVp] -= gm
             A[nI2][nVn] += gm

        elif comp_type == 'V':
            np, nm, valorV = elemento[1], elemento[2], elemento[3]
            v_idx = comp_indices['V'][comp_name]

            v_curr_var_col = v_curr_col_offset + v_idx
            v_constr_eq_row = v_constr_row_offset + v_idx

            A[np][v_curr_var_col] += 1
            A[nm][v_curr_var_col] -= 1

            A[v_constr_eq_row][np] += 1
            A[v_constr_eq_row][nm] -= 1
            b[v_constr_eq_row][0] += valorV

        elif comp_type == 'E':
             np, nm, nCp, nCn, av = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             e_idx = comp_indices['E'][comp_name]

             e_curr_var_col = e_curr_col_offset + e_idx
             e_constr_eq_row = e_constr_row_offset + e_idx

             A[np][e_curr_var_col] += 1
             A[nm][e_curr_var_col] -= 1

             A[e_constr_eq_row][np] += 1
             A[e_constr_eq_row][nm] -= 1
             A[e_constr_eq_row][nCp] -= av
             A[e_constr_eq_row][nCn] += av

        elif comp_type == 'F':
             nIplus, nIminus, nCc, nCd, beta = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             f_idx = comp_indices['F'][comp_name]

             f_source_curr_var_col = f_src_curr_col_offset + f_idx
             f_control_curr_var_col = f_ctrl_curr_col_offset + f_idx

             f_source_def_row = f_src_def_row_offset + f_idx
             f_control_def_row = f_ctrl_def_row_offset + f_idx

             A[nIplus][f_source_curr_var_col] += 1
             A[nIminus][f_source_curr_var_col] -= 1
             A[nCc][f_control_curr_var_col] -= 1
             A[nCd][f_control_curr_var_col] += 1

             A[f_source_def_row][f_source_curr_var_col] += 1
             A[f_source_def_row][f_control_curr_var_col] -= beta

             A[f_control_def_row][nCc] += 1
             A[f_control_def_row][nCd] -= 1

        elif comp_type == 'H':
             nVplus, nVminus, nCc, nCd, rm = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             h_idx = comp_indices['H'][comp_name]

             h_source_curr_var_col = h_src_curr_col_offset + h_idx
             h_control_curr_var_col = h_ctrl_curr_col_offset + h_idx

             h_source_def_row = h_src_def_row_offset + h_idx
             h_control_def_row = h_ctrl_def_row_offset + h_idx

             A[nVplus][h_source_curr_var_col] += 1
             A[nVminus][h_source_curr_var_col] -= 1
             A[nCc][h_control_curr_var_col] -= 1
             A[nCd][h_control_curr_var_col] += 1

             A[h_source_def_row][nVplus] += 1
             A[h_source_def_row][nVminus] -= 1
             A[h_source_def_row][h_control_curr_var_col] -= rm

             A[h_control_def_row][nCc] += 1
             A[h_control_def_row][nCd] -= 1

        elif comp_type == 'A':
             na, nb, nc, nd, k1, k2, k3, k4, k5 = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5], elemento[6], elemento[7], elemento[8], elemento[9]

             A[na][na] += k1
             A[na][nb] -= k1
             A[na][nc] += k2
             A[na][nd] -= k2
             b[na][0] -= k3

             A[nb][na] -= k1
             A[nb][nb] += k1
             A[nb][nc] -= k2
             A[nb][nd] += k2
             b[nb][0] += k3

             A[nc][na] += k4
             A[nc][nb] -= k4
             A[nc][nc] += k5
             A[nc][nd] -= k5

             A[nd][na] -= k4
             A[nd][nb] += k4
             A[nd][nc] -= k5
             A[nd][nd] += k5

        elif comp_type == 'B':
             na, nb, nc, nd, ne, nf = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5], elemento[6]
             k1, k2, k3, k4, k5, k6, k7, k8 = elemento[7], elemento[8], elemento[9], elemento[10], elemento[11], elemento[12], elemento[13], elemento[14]
             b_idx = comp_indices['B'][comp_name]

             b_ief_var_col = b_ief_curr_col_offset + b_idx
             b_vef_constr_row = b_constr_row_offset + b_idx

             A[na][na] += k1
             A[na][nb] -= k1
             A[na][b_ief_var_col] += k2

             A[nb][na] -= k1
             A[nb][nb] += k1
             A[nb][b_ief_var_col] -= k2

             A[nc][na] += k3
             A[nc][nb] -= k3
             A[nc][nc] += k4
             A[nc][nd] -= k4
             b[nc][0] -= k5

             A[nd][na] -= k3
             A[nd][nb] += k3
             A[nd][nc] -= k4
             A[nd][nd] += k4
             b[nd][0] += k5

             A[ne][b_ief_var_col] += 1

             A[nf][b_ief_var_col] -= 1

             A[b_vef_constr_row][ne] += 1
             A[b_vef_constr_row][nf] -= 1
             A[b_vef_constr_row][na] -= k6
             A[b_vef_constr_row][nb] += k6
             A[b_vef_constr_row][nc] -= k7
             A[b_vef_constr_row][nd] += k7
             b[b_vef_constr_row][0] += k8


    A[0, :] = 0
    A[0, 0] = 1
    b[0, 0] = 0

    return A, b


def main(netlist_filename):
    componentes = criarListaComponentes(netlist_filename)

    n_max_node, mna_counts, comp_indices = count_mna_info(componentes)

    A, b = insert_mna_stamps(n_max_node, mna_counts, componentes, comp_indices)

    x = np.linalg.solve(A, b)

    e_nodais = x[1 : n_max_node + 1]

    return e_nodais.flatten()
