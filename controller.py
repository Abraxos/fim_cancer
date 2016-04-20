from fp_growth import fp_growth
from cgpb_finder import cgpb_finder 
import csv

class controller():
	def __read(self,file,d):
		rows = []
		with open(file, 'r') as f:
			reader = csv.reader(f, dialect='excel', delimiter=d)
			for row in reader:
				rows.append(row)
                return rows

	def __pull_transaction_data(self,file):
		rows = self.__read(file,',')
		proteins = rows[0][2:]
		patients = []
		transactions = []
		for row in rows[1:]:
			transactions.append(map(float,row[2:]))
			patients.append(row[0])

		return {'transactions':transactions,'proteins':proteins,'patients':patients}

	def __expand_proteins(self,proteins,transactions):
		number_of_copies = len(transactions[0])/len(proteins)
		expanded_proteins = []
		for x in range(0,number_of_copies):
			for protein in proteins:
				expanded_proteins.append(protein+'_'+str(x))
		return expanded_proteins

	def __produce_expression_table(self,transactions,proteins,patients):
		discrete_expressions_table=[]
		proteins.insert(0,'id')
		discrete_expressions_table.append(proteins)
		for idx,transaction in enumerate(transactions):
			transaction.insert(0,patients[idx])
			discrete_expressions_table.append(map(str,transaction))
		return discrete_expressions_table

	def __produce_clinical_table(self,file):
		rows = self.__read(file,'\t')
		id_idx = rows[0].index("Patient ID")
		status_idx = rows[0].index("Overall Survival Status")

		reduced_clinical_table = []
		reduced_clinical_table.append(["id","survival"])
		for row in rows[1:]:
			entry = [row[id_idx],row[status_idx]]
			reduced_clinical_table.append(entry)
		return reduced_clinical_table
	
	def __convert_indexs_to_actuals(self,solutions_index,proteins):
		solutions_actual = {}
		for threshold,set in solutions_index.iteritems():
			solutions_actual[threshold]=[]
			for freq_set in set:
				l=list(freq_set)
				for idx,item in enumerate(l):
					actual=proteins[item]
					l[idx]=actual
				solutions_actual[threshold].append(l)	
		return solutions_actual

	def __preliminary_find(self,clinic_table,express_table):
		prelim_finder = cgpb_finder.cgpb_finder.from_tables(clinic_table,express_table)
		alive_transactions = []
		dead_transactions = []
		for key,values in prelim_finder.get_dictionary().iteritems():
			alive_transaction = []
			dead_transaction = []
			for protein,pair in values.iteritems():
				if(pair[1]==1):
					alive_transaction.append(float(pair[0]))
				elif(pair[1]==0):
					dead_transaction.append(float(pair[0]))
			if(len(alive_transaction)):
				alive_transactions.append(alive_transaction)
			if(len(dead_transaction)):
				dead_transactions.append(dead_transaction)
		return [alive_transactions,dead_transactions]

	def __init__(self,file_expr,file_clinic,thresholds_alive,thresholds_dead,override_set=None):
		print("starting...")
		print("controller - pulling transaction data(1)...")
		res =  self.__pull_transaction_data(file_expr)
		print("controller - produce clinical and non discretized expression table")
		clinic_table = self.__produce_clinical_table(file_clinic)
		express_table = self.__produce_expression_table(res['transactions'],res['proteins'],res['patients'])
		
		print("preliminary finder - start")
		groups = self.__preliminary_find(clinic_table,express_table)

		print("controller - pulling transaction data(2)...")
                res =  self.__pull_transaction_data(file_expr)
		for i,group in enumerate(groups):
			thresholds = []
			if i == 0:
				status = True
				filename = "ranks_for_alive.txt"
				thresholds = thresholds_alive
			else:
				thresholds = thresholds_dead
				filename = "ranks_for_dead.txt"
				status = False

			print('this is group ' + str(i)) 
			print(group)
			print("fim - start")
			fim = fp_growth.FrequentItemsetMiner()
			fim.initialize(group,fp_growth.discretize_on_avg)
			proteins = self.__expand_proteins(res['proteins'],fim.discretized_transactions)

			print("fim - finding solutions...")
			solutions_index = fim.run(thresholds)

			print("controller - converting to actuals...")
			solutions_actual = self.__convert_indexs_to_actuals(solutions_index,proteins)

			print("controller - producing discretized expression table")
			express_table = self.__produce_expression_table(fim.discretized_transactions,proteins,res['patients'])

			print("finder - start")
			finder = cgpb_finder.cgpb_finder.from_tables(clinic_table,express_table)
			ranks = []

			if override_set is None:
				for idx_t,threshold in enumerate(thresholds):
					for idx_f,freq_set in enumerate(solutions_actual[threshold]):
						if(len(freq_set)> 0):
							result = finder.confirm_cgpb(freq_set,status)
							string ="("+ ','.join(freq_set)+")\t"+str(result["z-score"])
							ranks.append(string)
							print("checked:("+str(threshold)+","+str(idx_f)+") "+string)
			else:
				for idx_f,freq_set in enumerate(override_set):
					if(len(freq_set)>0):
						result = finder.confirm_cgpb(freq_set,status)
						string = "("+','.join(freq_set)+")\t"+str(result["z-score"])
						ranks.append(string)
						print("checked:("+str(idx_f)+") "+string)

			with open(filename, 'w') as f:
				for s in ranks:
					f.write(s + '\n')		

class controller_test():
	# integration tests
	def test_constructor_with_override():
		c = controller('examples/data/TCGA-THCA-L3-S54_reduced.csv','examples/data/thca_tcga_clinical_data.tsv',[4])
	def test_constructor_without_override():
		c = controller('examples/data/TCGA-THCA-L3-S54_reduced.csv','examples/data/thca_tcga_clinical_data.tsv',[4])

	# unit tests
	def test_convert_indexs_to_actuals():
		print("-")
	
	def test_produce_clinical_table():
		print("-")

	def test_produce_expression_table():
		print("-")

	def test_expand_proteins():
		print("-")

	def test_pull_transactions_data():
		print("-")

	def test_read():
		print("-")

c = controller('examples/data/TCGA-THCA-L3-S54_reduced.csv','examples/data/thca_tcga_clinical_data.tsv',range(15,30),range(2,15))
#c = controller('examples/data/TCGA-THCA-L3-S54.csv','examples/data/thca_tcga_clinical_Data.tsv',[20])
