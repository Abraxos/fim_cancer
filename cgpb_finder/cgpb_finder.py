import csv
import math
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

class cgpb_finder():
	__dict = {}

	def __init__(self,dict):
		self.__dict = dict

	@classmethod
	def __create_dict(self,e_rows,c_rows):
		# initialize the dictionary using expression data
		dict = { row[0]:{e_rows[0][i]:[row[i],0] for i in range(1,len(e_rows[0]))} for row in e_rows[1:] }
		# read clinical data and mark the liveliness...
		for row in c_rows[1:]:
			patient = row[0]
			alive = row[1]
			if patient in dict and (alive == "LIVING" or alive == "DiseaseFree"):
				for protein in dict[patient].keys():
					dict[patient][protein][1] = 1
			elif patient in dict and (alive == "DECEASED" or alive == "Recurred/Progressed"):
				for protein in dict[patient].keys():
					dict[patient][protein][1] = 0
			elif patient in dict and (alive != "LIVING" or alive != "DECEASED" or alive != "DiseaseFree" or alive != "Recurred/Progressed"):
				del dict[patient]

		# dictionary format
		#   |p1|p2|p3|p4|p5|
		# ------------------
		# t1|e |..|..|..|  |
		# t2|. |  |  |  |  |
		# t3|. |  |  |  |  |
		# t4|. |  |  |  |  |
		# every entry e is an array [liveliness,has_expressed_protein]
		# liveliness is string "1" or "0"
		# has_expressed_protein is integer 1 or 0
		# dict = { t1: {p1:[x11,y11],p2:[x12,y12]}, t2: {p1:[x21,y21] ... }}
		return dict

	@classmethod
	def __read(self,file):
		rows = []
		with open(file, 'r') as f:
			reader = csv.reader(f, dialect='excel', delimiter='\t')
			for row in reader:
				rows.append(row)
		return rows

	@classmethod
	def from_files(cls,file_clinic,file_expr):
		c_rows = cls.__read(file_clinic)
		e_rows = cls.__read(file_expr)
		return cls(cls.__create_dict(e_rows,c_rows))


	@classmethod
	def from_tables(cls,table_clinic,table_expr):
		return cls(cls.__create_dict(table_expr,table_clinic))

	def get_dictionary(self):
		return self.__dict

	def __get_instance_count(self,freq_set):
		expressed_and_alive = 0
		expressed_and_dead  = 0
		expressed = 0
		expressed_array = []
		unexpressed_and_alive = 0
		unexpressed_and_dead  = 0
		unexpressed = 0
		unexpressed_array = []
		alive = 0
		dead = 0
		
		# we search through the dictionary patient-wise first then protein-wise.
		# we check for each patient whether he/she has the freq_set:
		# if they do then we increment expressed otherwise increment unexpressed
		# we also maintain counts of expressed and alive/expressed and dead
		# same for unexpressed.
		for patient in self.__dict.keys():
			freq_set_contained = list(freq_set)
			patient_alive =  False
			for protein in self.__dict[patient].keys():
				if self.__dict[patient][protein][1] == 1 and not patient_alive:
					patient_alive = True

				if protein in freq_set and self.__dict[patient][protein][0] == "1":
					freq_set_contained[freq_set_contained.index(protein)] = True
				elif protein in freq_set and self.__dict[patient][protein][0] == "0":
					freq_set_contained[freq_set_contained.index(protein)] = False

			if(False not in freq_set_contained and patient_alive):
				expressed_and_alive+=1
				expressed+=1
				alive+=1
				expressed_array.append(patient)
			elif(False not in freq_set_contained and not patient_alive):
				expressed_and_dead+=1
				expressed+=1
				dead+=1
				expressed_array.append(patient)
			elif(False in freq_set_contained and patient_alive):
				unexpressed_and_alive+=1
				unexpressed+=1
				alive+=1
				unexpressed_array.append(patient)
			elif(False in freq_set_contained and not patient_alive):
				unexpressed_and_dead+=1
				unexpressed+=1
				dead+=1
				unexpressed_array.append(patient)

		return {"expressed and alive":expressed_and_alive, "expressed and dead":expressed_and_dead, "expressed":expressed, "alive":alive, 
		"unexpressed and alive":unexpressed_and_alive, "unexpressed and dead":unexpressed_and_dead, "unexpressed":unexpressed, "dead":dead,
		"expressed array":expressed_array, "unexpressed array":unexpressed_array}
	
	# the formula for two proportions z test can be found online...
	def __two_proportions_z_test(self,count,status):
		if(status == True):
			x_1 = float(count["expressed and alive"])
			x_2 = float(count["unexpressed and alive"])
			n_1 = float(count["expressed"])
			n_2 = float(count["unexpressed"])
		else:
			x_1 = float(count["expressed and dead"])
			x_2 = float(count["unexpressed and dead"])
			n_1 = float(count["expressed"])
			n_2 = float(count["unexpressed"])

		p_1 = x_1/n_1
		p_2 = x_2/n_2
		p   = (x_1+x_2)/(n_1+n_2)
		if(p!=1.0):
			z_score = (p_1-p_2)/(math.sqrt(p*(1.0-p)*(1/n_1+1/n_2)))
		else:
			z_score = "no difference between proportions!"
		return z_score

	def __KM_analysis(self,duration_table,expressed_array,unexpressed_array,freq_set):
		data = {}
		expressed_T = []
		expressed_C = []
		unexpressed_T = []
		unexpressed_C = []
		for idx,row in enumerate(duration_table):
			if(idx>0):
				if row[0] in unexpressed_array and row[1] !=  "NA" and row[2] !=  "NA":
					unexpressed_T.append(float(row[1]))
					unexpressed_C.append(int(row[2]))
				elif row[0] in expressed_array and row[1] != "NA" and row[2] !=  "NA":
					expressed_T.append(float(row[1]))
					expressed_C.append(int(row[2]))

		results = logrank_test(expressed_T, unexpressed_T, expressed_C, unexpressed_C, alpha=.95 )
		if(results.p_value < .0006):
			ax = plt.subplot(111)
			kmf = KaplanMeierFitter()
			kmf.fit(expressed_T, event_observed=expressed_C, label="Satisfying")
			kmf.plot(ax=ax, ci_force_lines=False)
			kmf.fit(unexpressed_T, event_observed=unexpressed_C, label="None-Satisfying")
			kmf.plot(ax=ax, ci_force_lines=False)
			plt.ylim(0,1)
			plt.title("Lifespans ("+str(freq_set)+")")
			plt.show()	
		return results.p_value

	# public method that wraps the methods above...
	def confirm_cgpb(self,freq_set,status,duration_table=None):
		count = self.__get_instance_count(freq_set)
		z_score = self.__two_proportions_z_test(count,status)
		if duration_table is not None:
			p_value = self.__KM_analysis(duration_table,count["expressed array"],count["unexpressed array"],freq_set)
			return {"z-score":z_score,"counts":count,"log-rank-test":p_value}
		else:
			return {"z-score":z_score,"counts":count,"log-rank-test":"NA"}


        # unit tests
	def test_two_proportions_z_test(self):
		status = True
		count = {'expressed and alive': 1, 'expressed and dead': 1, 'alive': 9, 'unexpressed': 12, 'dead': 5, 'unexpressed array': ['t8', 't9', 't6', 't4', 't5', 't2', 't1', 't14', 't10', 't11', 't12', 't13'], 'expressed array': ['t7', 't3'], 'unexpressed and alive': 8, 'expressed': 2, 'unexpressed and dead': 4}
		print(self.__two_proportions_z_test(count,status))

        def test_KM_analysis(self):
		duration_table = [['patient', 'time', 'status'], ['t1', '3.65', '0'], ['t2', '65.6', '0'], ['t3', '63.3', '0'], ['t4', '19.74', '1'], ['t5', '29.99', '0'], ['t6', '19.22', '0'], ['t7', '5.03', '1'], ['t8', '13.3', '0'], ['t9', '22.96', '0'], ['t10', '17.84', '1'],['t11', '24.32', '1'],['t12', '30.12', '1'],['t13', '45.42', '1'],['t14', '65.84', '1']]
		expressed_array = ['t8', 't9', 't6', 't4', 't5', 't2', 't1', 't14', 't10', 't11', 't12', 't13']
		unexpressed_array = ['t7', 't3']
		print(self.__KM_analysis(duration_table,expressed_array,unexpressed_array,['p1_h','p2_l']))

# run integration test and unit tests
def test_confirm_cgpb():
	finder = cgpb_finder.from_files('input_clinic.tsv','input_expr.tsv')
	print("Test - two proportions z test")
	finder.test_two_proportions_z_test()

	print("Test - KM Analysis")	
	finder.test_KM_analysis()

	print("Test - a) Integeration test using sample files")
	print(finder.confirm_cgpb(['p1_h','p2_l'],True))

	print("Test - b) test the dictionary created from sample files")
	print(finder.get_dictionary())

# run tests
print(test_confirm_cgpb())

