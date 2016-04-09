from fp_growth import fp_growth
from cgpb_finder import cgpb_finder 
import csv

class controller:
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


	def __produce_expression_table(self,transactions,proteins,patients):
		discrete_expressions_table = []
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
	
	def __convert_indexs_to_actuals(self,solutions_index):
		solutions_actual = []
		for threshold,set in solutions_index.iteritems():
			for freq_set in set:
				solutions_actual.insert(0,[])
				for item in set:
					solutions_actual[0].append(item)
		return solutions_actual

		
	def __init__(self,file_expr,file_clinic,thresholds):
		res =  self.__pull_transaction_data(file_expr)
		fim = fp_growth.FrequentItemsetMiner()
		fim.initialize(res['transactions'],fp_growth.discretize_on_avg)
		solutions_index = fim.run(thresholds)
		solutions_actual = self.__convert_indexs_to_actuals(solutions_index)
		print(solutions_actual)

		clinic_table = self.__produce_clinical_table(file_clinic)
		express_table = self.__produce_expression_table(res['transactions'],res['proteins'],res['patients'])

		# initialize finder
		finder = cgpb_finder.cgpb_finder.from_tables(clinic_table,express_table)		

c = controller('examples/data/TCGA-THCA-L3-S54_reduced.csv','examples/data/thca_tcga_clinical_data.tsv',[4])
