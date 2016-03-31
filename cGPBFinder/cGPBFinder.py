import csv
import numpy as np

class cGBPFinder():
	__dict = {}
	def __read(self,file):
                rows = []
		with open(file, 'r') as f:
                        reader = csv.reader(f, dialect='excel', delimiter='\t')
                        for row in reader:
                                rows.append(row)
                return rows

	def __init__(self,file_clinic,file_expr):
		# read transcation data into dictionary
		rows = self.__read(file_expr)
		self.__dict = { row[0]:{rows[0][i]:[row[i],0] for i in range(1,len(rows[0]))} for row in rows[1:] }

		# read clinical data and mark the liveliness...
		rows = self.__read(file_clinic)
		for row in rows[1:]:
			patient = row[0]
			alive = row[1]
			if patient in self.__dict and alive == "LIVING":
				for protein in self.__dict[patient].keys():
					self.__dict[patient][protein][1] = 1

	def getDictionary(self):
		return self.__dict

	def confirmcGPB(self,freq_set):
		expressed_and_alive = 0
		expressed_and_dead  = 0
		unexpressed_and_alive = 0
		unexpressed_and_dead  = 0
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
			elif(False not in freq_set_contained and not patient_alive):
				expressed_and_dead+=1
			elif(False in freq_set_contained and patient_alive):
				unexpressed_and_alive+=1
			elif(False in freq_set_contained and not patient_alive):
				unexpressed_and_dead+=1

		return {"expressed and alive:":expressed_and_alive, "expressed and dead:":expressed_and_dead, 
		"unexpressed and alive:":unexpressed_and_alive, "unexpressed and dead:":unexpressed_and_dead}

	
	def sigMeasure():
		print("TO-DO")

finder = cGBPFinder('input_clinic.tsv','input_expr.tsv')
print(finder.getDictionary())
print(finder.confirmcGPB(['p1','p2']))
