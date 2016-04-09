import csv
import math

class cgpb_finder():
	__dict = {}

	def __init__(self,dict):
		self.__dict = dict

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
		# read transcation data into dictionary
		rows = cls.__read(file_expr)
		dict = { row[0]:{rows[0][i]:[row[i],0] for i in range(1,len(rows[0]))} for row in rows[1:] }

		# read clinical data and mark the liveliness...
		rows = cls.__read(file_clinic)
		print(rows)
		for row in rows[1:]:
			patient = row[0]
			alive = row[1]
			if patient in dict and alive == "LIVING":
				for protein in dict[patient].keys():
					dict[patient][protein][1] = 1
		return cls(dict)


	@classmethod
	def from_tables(cls,table_clinic,table_expr):
		rows = table_expr
		dict = { row[0]:{rows[0][i]:[row[i],0] for i in range(1,len(rows[0]))} for row in rows[1:] }
		
		rows = table_clinic
		for row in rows[1:]:
			patient = row[0]
			alive = row[1]
			if patient in dict and alive == "LIVING":
				for protein in dict[patient].keys():
					dict[patient][protein][1] = 1
		return cls(dict)

	def get_dictionary(self):
		return self.__dict

	def __get_instance_count(self,freq_set):
		expressed_and_alive = 0
		expressed_and_dead  = 0
		expressed = 0
		unexpressed_and_alive = 0
		unexpressed_and_dead  = 0
		unexpressed = 0
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
			elif(False not in freq_set_contained and not patient_alive):
				expressed_and_dead+=1
				expressed+=1
			elif(False in freq_set_contained and patient_alive):
				unexpressed_and_alive+=1
				unexpressed+=1
			elif(False in freq_set_contained and not patient_alive):
				unexpressed_and_dead+=1
				unexpressed+=1

		return {"expressed and alive":expressed_and_alive, "expressed and dead":expressed_and_dead, "expressed":expressed, 
		"unexpressed and alive":unexpressed_and_alive, "unexpressed and dead":unexpressed_and_dead, "unexpressed":unexpressed}

	
	def __two_proportions_z_test(self,count):
		p_1 = float(count["expressed and alive"])/float(count["expressed"])
		p_2 = float(count["unexpressed and alive"])/float(count["unexpressed"])
		p   = (float(count["expressed and alive"])+float(count["unexpressed and alive"])) \
			/(float(count["expressed"])+float(count["unexpressed"]))
		z_score = ((p_1-p_2)-0.0)/(math.sqrt(p*(1.0-p)*(1/float(count["expressed"])+1/float(count["unexpressed"]))))
		return z_score

	def confirm_cgpb(self,freq_set):
		count = self.__get_instance_count(freq_set)
		z_score = self.__two_proportions_z_test(count)
		if(-1.96 <= z_score <= 1.96):
			return {"z-score":z_score,"statistically different?": True}
		else:
			return {"z-score":z_score,"statistically different?": False}
		
class cgpb_finder_test():
	# integeration test
	# use the test data for which we know the result...
	def test_confirm_cgpb():
		finder = cgpb_finder.from_files('input_clinic.tsv','input_expr.tsv')
		assert(finder.confirm_cgpb(['p1','p2'])== {"z-score":1.138550085106622, "statistically different?": True})
	
	# unit tests
	def test_two_proportions_z_test(self,count):
		print("-")

	def test_get_instance_count(self,freq_set):
		print("-")

	def test_constructor_from_file(file_clinic,file_expr):
		print("-")

	def test_constructor_from_table(table_clinic,table_expr):
		print("-")

#finder = cgpb_finder.from_files('input_clinic.tsv','input_expr.tsv')
#assert(finder.confirm_cgpb(['p1','p2'])== {"z-score":1.138550085106622, "statistically different?": True})
