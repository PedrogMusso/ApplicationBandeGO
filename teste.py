####################################################
# 1a Atividade de Laboratorio de Circuitos Eletricos II
# Periodo: 2025.1
# Nome dos alunos: COMPLETAR
####################################################

import numpy as np


def insert_mna_stamps(netlist_filename):
    componentes_local = []
    n_max_node = 0
    mna_counts = {'V': 0, 'E': 0, 'H': 0, 'B': 0, 'F': 0}
    comp_indices = {'V': {}, 'E': {}, 'H': {}, 'B': {}, 'F': {}}

    with open(netlist_filename, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("*"):
                continue

            listaLinha = linha.split()
            if not listaLinha: continue

            comp_name = listaLinha[0]
            comp_type = comp_name[0].upper()
            componente_parsed = [comp_name]

            if comp_type == 'R':
                n1, n2, valorR = int(listaLinha[1]), int(listaLinha[2]), float(listaLinha[3])
                componente_parsed.extend([n1, n2, valorR])
                n_max_node = max(n_max_node, n1, n2)
            elif comp_type == 'G':
                nI1, nI2, nVp, nVn, gm = int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5])
                componente_parsed.extend([nI1, nI2, nVp, nVn, gm])
                n_max_node = max(n_max_node, nI1, nI2, nVp, nVn)
            elif comp_type == 'I':
                n1, n2, valorI = int(listaLinha[1]), int(listaLinha[2]), float(listaLinha[4])
                componente_parsed.extend([n1, n2, valorI])
                n_max_node = max(n_max_node, n1, n2)
            elif comp_type == 'V':
                np_v, nm_v, valorV = int(listaLinha[1]), int(listaLinha[2]), float(listaLinha[4])
                componente_parsed.extend([np_v, nm_v, valorV])
                n_max_node = max(n_max_node, np_v, nm_v)
            elif comp_type == 'E':
                np_e, nm_e, nCp, nCn, av = int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5])
                componente_parsed.extend([np_e, nm_e, nCp, nCn, av])
                n_max_node = max(n_max_node, np_e, nm_e, nCp, nCn)
            elif comp_type == 'F':
                nIplus, nIminus, nCc_f, nCd_f, beta = int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5])
                componente_parsed.extend([nIplus, nIminus, nCc_f, nCd_f, beta])
                n_max_node = max(n_max_node, nIplus, nIminus, nCc_f, nCd_f)
            elif comp_type == 'H':
                nVplus, nVminus, nCc_h, nCd_h, rm = int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5])
                componente_parsed.extend([nVplus, nVminus, nCc_h, nCd_h, rm])
                n_max_node = max(n_max_node, nVplus, nVminus, nCc_h, nCd_h)
            elif comp_type == 'A':
                na_a, nb_a, nc_a, nd_a, k1_a, k2_a, k3_a, k4_a, k5_a = int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), float(listaLinha[5]), float(listaLinha[6]), float(listaLinha[7]), float(listaLinha[8]), float(listaLinha[9])
                componente_parsed.extend([na_a, nb_a, nc_a, nd_a, k1_a, k2_a, k3_a, k4_a, k5_a])
                n_max_node = max(n_max_node, na_a, nb_a, nc_a, nd_a)
            elif comp_type == 'B':
                na_b, nb_b, nc_b, nd_b, ne_b, nf_b, k1_b, k2_b, k3_b, k4_b, k5_b, k6_b, k7_b, k8_b = int(listaLinha[1]), int(listaLinha[2]), int(listaLinha[3]), int(listaLinha[4]), int(listaLinha[5]), int(listaLinha[6]), float(listaLinha[7]), float(listaLinha[8]), float(listaLinha[9]), float(listaLinha[10]), float(listaLinha[11]), float(listaLinha[12]), float(listaLinha[13]), float(listaLinha[14])
                componente_parsed.extend([na_b, nb_b, nc_b, nd_b, ne_b, nf_b, k1_b, k2_b, k3_b, k4_b, k5_b, k6_b, k7_b, k8_b])
                n_max_node = max(n_max_node, na_b, nb_b, nc_b, nd_b, ne_b, nf_b)
            else:
                pass

            if comp_type in mna_counts:
                 comp_indices[comp_type][comp_name] = mna_counts[comp_type]
                 mna_counts[comp_type] += 1

            componentes_local.append(componente_parsed)

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


    for elemento in componentes_local:
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
            np_v, nm_v, valorV = elemento[1], elemento[2], elemento[3]
            v_idx = comp_indices['V'][comp_name]

            v_curr_var_col = v_curr_col_offset + v_idx
            v_constr_eq_row = v_constr_row_offset + v_idx

            A[np_v][v_curr_var_col] += 1
            A[nm_v][v_curr_var_col] -= 1

            A[v_constr_eq_row][np_v] += 1
            A[v_constr_eq_row][nm_v] -= 1
            b[v_constr_eq_row][0] += valorV

        elif comp_type == 'E':
             np_e, nm_e, nCp, nCn, av = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             e_idx = comp_indices['E'][comp_name]

             e_curr_var_col = e_curr_col_offset + e_idx
             e_constr_eq_row = e_constr_row_offset + e_idx

             A[np_e][e_curr_var_col] += 1
             A[nm_e][e_curr_var_col] -= 1

             A[e_constr_eq_row][np_e] += 1
             A[e_constr_eq_row][nm_e] -= 1
             A[e_constr_eq_row][nCp] -= av
             A[e_constr_eq_row][nCn] += av

        elif comp_type == 'F':
             nIplus, nIminus, nCc_f, nCd_f, beta = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             f_idx = comp_indices['F'][comp_name]

             f_source_curr_var_col = f_src_curr_col_offset + f_idx
             f_control_curr_var_col = f_ctrl_curr_col_offset + f_idx

             f_source_def_row = f_src_def_row_offset + f_idx
             f_control_def_row = f_ctrl_def_row_offset + f_idx

             A[nIplus][f_source_curr_var_col] += 1
             A[nIminus][f_source_curr_var_col] -= 1
             A[nCc_f][f_control_curr_var_col] -= 1
             A[nCd_f][f_control_curr_var_col] += 1

             A[f_source_def_row][f_source_curr_var_col] += 1
             A[f_source_def_row][f_control_curr_var_col] -= beta

             A[f_control_def_row][nCc_f] += 1
             A[f_control_def_row][nCd_f] -= 1

        elif comp_type == 'H':
             nVplus, nVminus, nCc_h, nCd_h, rm = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5]
             h_idx = comp_indices['H'][comp_name]

             h_source_curr_var_col = h_src_curr_col_offset + h_idx
             h_control_curr_var_col = h_ctrl_curr_col_offset + h_idx

             h_source_def_row = h_src_def_row_offset + h_idx
             h_control_def_row = h_ctrl_def_row_offset + h_idx

             A[nVplus][h_source_curr_var_col] += 1
             A[nVminus][h_source_curr_var_col] -= 1
             A[nCc_h][h_control_curr_var_col] -= 1
             A[nCd_h][h_control_curr_var_col] += 1

             A[h_source_def_row][nVplus] += 1
             A[h_source_def_row][nVminus] -= 1
             A[h_source_def_row][h_control_curr_var_col] -= rm

             A[h_control_def_row][nCc_h] += 1
             A[h_control_def_row][nCd_h] -= 1

        elif comp_type == 'A':
             na_a, nb_a, nc_a, nd_a, k1_a, k2_a, k3_a, k4_a, k5_a = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5], elemento[6], elemento[7], elemento[8], elemento[9]

             A[na_a][na_a] += k1_a
             A[na_a][nb_a] -= k1_a
             A[na_a][nc_a] += k2_a
             A[na_a][nd_a] -= k2_a
             b[na_a][0] -= k3_a

             A[nb_a][na_a] -= k1_a
             A[nb_a][nb_a] += k1_a
             A[nb_a][nc_a] -= k2_a
             A[nb_a][nd_a] += k2_a
             b[nb_a][0] += k3_a

             A[nc_a][na_a] += k4_a
             A[nc_a][nb_a] -= k4_a
             A[nc_a][nc_a] += k5_a
             A[nc_a][nd_a] -= k5_a

             A[nd_a][na_a] -= k4_a
             A[nd_a][nb_a] += k4_a
             A[nd_a][nc_a] -= k5_a
             A[nd_a][nd_a] += k5_a

        elif comp_type == 'B':
             na_b, nb_b, nc_b, nd_b, ne_b, nf_b, k1_b, k2_b, k3_b, k4_b, k5_b, k6_b, k7_b, k8_b = elemento[1], elemento[2], elemento[3], elemento[4], elemento[5], elemento[6], elemento[7], elemento[8], elemento[9], elemento[10], elemento[11], elemento[12], elemento[13], elemento[14]
             b_idx = comp_indices['B'][comp_name]

             b_ief_var_col = b_ief_curr_col_offset + b_idx
             b_vef_constr_row = b_constr_row_offset + b_idx

             A[na_b][na_b] += k1_b
             A[na_b][nb_b] -= k1_b
             A[na_b][b_ief_var_col] += k2_b

             A[nb_b][na_b] -= k1_b
             A[nb_b][nb_b] += k1_b
             A[nb_b][b_ief_var_col] -= k2_b

             A[nc_b][na_b] += k3_b
             A[nc_b][nb_b] -= k3_b
             A[nc_b][nc_b] += k4_b
             A[nc_b][nd_b] -= k4_b
             b[nc_b][0] -= k5_b

             A[nd_b][na_b] -= k3_b
             A[nd_b][nb_b] += k3_b
             A[nd_b][nc_b] -= k4_b
             A[nd_b][nd_b] += k4_b
             b[nd_b][0] += k5_b

             A[ne_b][b_ief_var_col] += 1

             A[nf_b][b_ief_var_col] -= 1

             A[b_vef_constr_row][ne_b] += 1
             A[b_vef_constr_row][nf_b] -= 1
             A[b_vef_constr_row][na_b] -= k6_b
             A[b_vef_constr_row][nb_b] += k6_b
             A[b_vef_constr_row][nc_b] -= k7_b
             A[b_vef_constr_row][nd_b] += k7_b
             b[b_vef_constr_row][0] += k8_b


    A[0, :] = 0
    A[0, 0] = 1
    b[0, 0] = 0

    return A, b, n_max_node


def main(netlist_filename):
    A, b, n_max_node = insert_mna_stamps(netlist_filename)

    x = np.linalg.solve(A, b)

    e_nodais = x[1 : n_max_node + 1]

    return e_nodais.flatten()

