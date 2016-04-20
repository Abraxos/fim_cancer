

protein_data_file_path = 'TCGA-LUSC-L3-S51.csv'
clinical_data_file_path = 'lusc_tcga_clinical_data.csv'

with open(protein_data_file_path,'r') as protein_data_file:
    with open(clinical_data_file_path,'r') as clinical_data_file:
        P = {}
        Pn = []
        C = {}
        Cn = []
        first = True
        for line in protein_data_file:
            line = line.replace('"','')
            line = line.replace('\n','')
            line = line.split(',')
            if first:
               Pn = line[0:1] + line[2:]
               first = False
            else: P[line[0]] = line[2:]
        first = True
        for line in clinical_data_file:
            line = line.replace('"','')
            line = line.replace('\n','')
            line = line.split(',')
            if first:
                Cn = line[0:]
                first = False
            else: C[line[0]] = line
        D = [Pn + Cn]
        for patient_id in P:
            #if patient_id in C:
                line = [patient_id]
                line.extend(P[patient_id])
                line.extend(C[patient_id])
                D.append(line)
        print(D[0])
        print(D[1])
        with open('lusc_tcga_data.csv','w+') as data_file:
            str = []
            for line in D:
                str.append(','.join(line))
            str = '\n'.join(str)
            data_file.write(str)
