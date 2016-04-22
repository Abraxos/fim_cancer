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

	def __produce_clinical_table(self,file,clinic_attr):
		rows = self.__read(file,'\t')
		id_idx = rows[0].index("Patient ID")
		status_idx = rows[0].index(clinic_attr)

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
		
	def __init__(self,file_expr,file_clinic,thresholds,status,clinic_attr,discrete_func,override_set=None):
	
		print("controller - pulling transactions")
		res =  self.__pull_transaction_data(file_expr)
				
		print("controller initalizing fim")
		fim = fp_growth.FrequentItemsetMiner(duplicate_solutions=False)
		fim.initialize(res['transactions'],discretization_function=discrete_func)

		print(fim.discretized_transactions)

		print("controller - expanding proteins list")
		proteins = self.__expand_proteins(res['proteins'],fim.discretized_transactions)
		
		print("fim - run")
		solutions_index = fim.run(thresholds)
		
		print("controller - map index to actuals")
		solutions_actual = self.__convert_indexs_to_actuals(solutions_index,proteins)

		print("controller - produce clinical and expression tables")
		clinic_table = self.__produce_clinical_table(file_clinic,clinic_attr)
		express_table = self.__produce_expression_table(fim.discretized_transactions,proteins,res['patients'])

		print("controller - initalize finder")
		finder = cgpb_finder.cgpb_finder.from_tables(clinic_table,express_table)
		print("finder - run confirmer for all freq_sets")
		ranks = []
		if override_set is None:
			for threshold in thresholds:
				for freq_set in solutions_actual[threshold]:
					if(len(freq_set)> 0):
						result = finder.confirm_cgpb(freq_set,status)
						string ="("+ ','.join(freq_set)+")\t"+str(result["z-score"])
						ranks.append(string)
						print("checked:("+str(threshold)+","+str(freq_set)+") "+string)
		else:
			for freq_set in override_set:
				if(len(freq_set)>0):
					result = finder.confirm_cgpb(freq_set,status)
					string = "("+','.join(freq_set)+")\t"+str(result["z-score"])
					ranks.append(string)
					print("checked:("+str(freq_set)+") "+string)

		print("controller - save the logs!")
		with open('ranks.txt', 'w') as f:
				for s in ranks:
					f.write(s + '\n')		

class controller_test():
	# integration tests
	def test_constructor_with_override():
		print("-")
	def test_constructor_without_override():
		print("-")

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

def discretize_on_avg(column, name=None):
	name = name if name else None
	avg = float(sum(column)) / len(column)
	high_column = []
	low_column = []
	for c in column:
		if c >= avg:
			high_column.append(1)
			low_column.append(0)
		else:
			high_column.append(0)
			low_column.append(1)
	if name:
		return [high_column, low_column],[name + '_high', name + '_low']
	else:
		return [high_column, low_column]

def discretize_on_sd(column, name=None):
	name = name if name else None
	avg = float(sum(column)) / len(column)
	squared = []
	high_column = []
	mid_column = []
	low_column = []

	for entry in column:
		squared.append(entry ** 2)

	variance = float(sum(squared))/len(column)
	standard_deviation = variance ** .5
	max_sd = avg + standard_deviation
	min_sd = avg - standard_deviation
	for c in column:
		if c >= max_sd:
			high_column.append(1)
			mid_column.append(0)
			low_column.append(0)
		elif c <= min_sd:
            		high_column.append(0)
			mid_column.append(0)
            		low_column.append(1)
		else:
			high_column.append(0)
			mid_column.append(1)
			low_column.append(0)

	if name:
		return [high_column, mid_column, low_column],[name + '_high', name + '_mid', name + '_low']
	else:
		return [high_column, mid_column, low_column]

c = controller('examples/data/TCGA-LUSC-L3-S51.csv','examples/data/lusc_tcga_clinical_data.tsv',range(110,140),False,'Overall Survival Status',discretize_on_sd)
