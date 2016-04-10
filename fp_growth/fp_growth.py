def cmp_to_key(mycmp):
    class key(object):
        def __init__(self, a, *args): self.a = a
        def __lt__(self, b): return mycmp(self.a, b.a) < 0
        def __gt__(self, b): return mycmp(self.a, b.a) > 0
        def __eq__(self, b): return mycmp(self.a, b.a) == 0
        def __le__(self, b): return mycmp(self.a, b.a) <= 0
        def __ge__(self, b): return mycmp(self.a, b.a) >= 0
        def __ne__(self, b): return mycmp(self.a, b.a) != 0
    return key

def node_repr(node, tabs):
		s = ('\t' * tabs) + str(node)
		for c in node.children:
			if c: s += '\n' + node_repr(c, tabs + 1)
		return s

def compare_item(x,y):
	if x[1] != y[1]:
		return x[1] - y[1]
	else:
		return y[0] - x[0]

class FPNode(object):
	def __init__(self, item):
		self.item = item
		self.conditional_support = 0
		self.conditional_node = None
		
		self.tree = None
		self.support = 0
		self.header = None
		self.num_items = 0
		self.children = [None] * self.num_items
		self.child_indices = []
		self.parent = None

	def load(self, tree):
		self.tree = tree
		self.support = 0
		if self.item is not None:
			self.header = self.tree.headers[self.item]
			self.incrementSupport()
			self.header.add_node(self)
		else:
			self.header = None
		self.num_items = self.tree.num_items
		self.children = [None] * self.num_items
		self.child_indices = []
		self.parent = None
		return self

	def load_conditional(self, node, tree):
		self.tree = tree
		self.support = node.conditional_support
		if self.item is not None:
			self.header = self.tree.headers[self.item]
			self.header.add_node(self)
			self.header.support += self.support
			self.header.frequency_idx = node.header.frequency_idx
		else:
			self.header = None
		self.num_items = self.tree.num_items
		self.children = [None] * self.num_items
		self.child_indices = []
		self.parent = None
		return self

	def incrementSupport(self):
		self.support += 1
		self.header.support += 1

	def bottom_up_conditional_support(self, item, conditional_support):
		if self.header:
			if self.item != item:
				self.conditional_support += conditional_support
				self.header.conditional_support += conditional_support
				self.parent.bottom_up_conditional_support(item, conditional_support)
			else:
				self.parent.bottom_up_conditional_support(item, self.support)

	def add_child(self, item):
		if self.children[item]:
			self.children[item].incrementSupport()
		else:
			self.children[item] = FPNode(item).load(self.tree) 
			self.child_indices.append(item)
			self.children[item].parent = self
		return self.children[item]

	def add_child_node(self, node):
		self.children[node.item] = node
		self.child_indices.append(node.item)
		node.parent = self

	def __repr__(self):
		return "{0}({1},{2}):{3}".format(self.item, self.support, self.conditional_support, self.child_indices)


class FPHeader(object):

	def __init__(self, item, tree):
		self.item = item
		self.tree = tree
		self.support = 0
		self.conditional_support = 0
		self.nodes = []
		self.num_items = self.tree.num_items
	
	def add_node(self, node):
		self.nodes.append(node)
	
	def __repr__(self):
		return "{0}({1},{2}) N:{3}".format(self.item, self.support, 
			                                    self.conditional_support, 
			                                    self.nodes)


def clone_tree(src_node, dst_tree):
	cloned_node = FPNode(src_node.item).load_conditional(src_node, dst_tree)
	for c in src_node.child_indices:
		child = src_node.children[c]
		if child.header.conditional_support >= dst_tree.threshold:
			cloned_node.add_child_node(clone_tree(child, dst_tree))
	return cloned_node


class FPTree(object):
	def __init__(self, threshold):
		self.threshold = threshold
		self.header_indices = []

	def load_transactions(self, transactions):
		self.num_items = len(transactions[0])
		self.headers = [FPHeader(i, self) for i in range(self.num_items)]
		for header in self.headers:
			self.header_indices.append(header.item)
		self.frequency = [(i,0) for i in range(self.num_items)]
		self.root = FPNode(None).load(self)
		for t in transactions:
			for i in range(len(t)):
				self.frequency[i] = (i, self.frequency[i][1] + t[i])
		self.frequency.sort(key=cmp_to_key(compare_item), reverse=True)
		self.frequency = [self.frequency[fi] for fi in range(len(self.frequency)) if self.frequency[fi][1] >= self.threshold]
		for t in transactions:
			current_node = self.root
			for fi in range(len(self.frequency)):
				i,f = self.frequency[fi]
				if t[i] and f >= self.threshold:
					current_node = current_node.add_child(i)
					current_node.header.frequency_idx = fi
		return self
	
	def load_conditional(self, tree):
		self.num_items = tree.num_items
		self.headers = [FPHeader(i, self) for i in range(self.num_items)]
		self.root = clone_tree(tree.root, self)
		self.frequency = tree.frequency
		for item in range(self.num_items):
			header = self.headers[item]
			if not header.nodes:
				self.headers[item] = None
			else:
				self.header_indices.append(header.item)
		self.frequency = [(header.item, header.support) for header in self.headers if header]
		self.frequency.sort(key=cmp_to_key(compare_item), reverse=True)
		for fi in range(len(self.frequency)):
			i,f = self.frequency[fi]
			self.headers[i].frequency_idx = fi
		return self
	
	def reset_conditional_supports(self, current_node):
		current_node.conditional_support = 0
		if current_node.header:
			current_node.header.conditional_support = 0
		for c in current_node.child_indices:
			child = current_node.children[c]
			if child.conditional_support > 0:
				self.reset_conditional_supports(child)
	
	def project(self, item):
		header = self.headers[item]
		for node in header.nodes:
			node.bottom_up_conditional_support(item, 0)
		result = FPTree(self.threshold).load_conditional(self)
		self.reset_conditional_supports(self.root)
		return result

	def __repr__(self):
		s = "FP-TREE:\n\tFREQUENCIES: {0}\n\tHEADERS: {1}\n".format(self.frequency, self.header_indices)
		for header in self.headers:
			s += "\t\t{0}\n".format(header)
		s += "\tNODES:\n" + node_repr(self.root,2)
		return s

class FPSearchState(object):
	def __init__(self, tree, projected_item, projected_items):
		self.tree = tree
		self.projected_tree = None
		self.projected_item = projected_item
		self.projected_items = list(projected_items) + [self.projected_item]
	def process(self, solutions):
		solutions.append(list(self.projected_items))
		self.projected_tree = self.tree.project(self.projected_item)

class FPSearchStack(object):
	def __init__(self, initial_tree=None):
		self.array = []
		if initial_tree:
			# self.push(initial_tree, initial_item, [])
			for i,f in initial_tree.frequency:
				self.push(initial_tree, i, [])
	def push(self, tree, projected_item, projected_items):
		self.array.append(FPSearchState(tree, projected_item, projected_items))
	def peek(self):
		return self.array[-1]
	def empty(self):
		return not self.array
	def pop(self):
		ss = self.array.pop()
		if not ss.projected_tree:
			print("WARNING: Popping a non-processed search state off of the stack.")
		tree = ss.projected_tree if ss.projected_tree else ss.tree
		for i,f in tree.frequency:
			self.push(tree, i, ss.projected_items)
		return ss

def fp_growth(transactions, threshold):
	solutions = [[]]
	initial_tree = FPTree(threshold).load_transactions(transactions)
	stack = FPSearchStack(initial_tree)
	while not stack.empty():
		state = stack.peek()
		state.process(solutions)
		stack.pop()
	return solutions

class NameMismatchError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class FrequentItemsetMiner(object):
	def __init__(self, duplicate_solutions=True):
		self.discretization_function = None
		self.transactions = None
		self.discretized_transactions = None
		self.duplicate_solutions = duplicate_solutions
		self.thresholds = None
		self.names = None
		self.discretized_names = None

	def initialize(self, transactions, names=None, discretization_function=None):
		if names and len(transactions[0]) != len(names):
			raise NameMismatchError('The number of columns does not match the set of names provided!')
		self.names = names
		discretized_columns = []
		self.discretized_names = []
		self.discretized_transactions = []
		self.transactions = transactions
		self.discretization_function = discretization_function
		if self.discretization_function:
			for c in range(len(transactions[0])):
				column = [row[c] for row in transactions]
				name = None if not names else names[c]
				if name:
					C, N = self.discretization_function(column,name)
					self.discretized_names.extend(N)
				else:
					C = self.discretization_function(column)
				discretized_columns.extend(C)
			for r in range(len(discretized_columns[0])):
				discretized_transaction = [dc[r] for dc in discretized_columns]
				self.discretized_transactions.append(discretized_transaction)
		else:
			self.discretized_transactions = self.transactions
			self.discretized_names = self.names
		if names is not None:
			return self.discretized_transactions, self.discretized_names
		else:
			return self.discretized_transactions
	
	def run(self, thresholds):
		solutions = {}
		if self.duplicate_solutions:
			for threshold in thresholds:
				solutions[threshold] = fp_growth(self.discretized_transactions, threshold)
			for threshold in solutions:
				S = solutions[threshold]
				for i in range(len(S)):
					S[i] = ts = tuple(sorted(S[i], reverse=True))
		else:
			solutions_to_thresholds = {}
			solutions = {}
			for threshold in thresholds:
				S = fp_growth(self.discretized_transactions, threshold)
				for s in S:
					ts = tuple(sorted(s, reverse=True))
					if ts in solutions_to_thresholds:
						solutions_to_thresholds[ts] = max(solutions_to_thresholds[ts], threshold)
					else:
						solutions_to_thresholds[ts] = threshold
			for solution in solutions_to_thresholds:
				threshold = solutions_to_thresholds[solution]
				if threshold not in solutions:
					solutions[threshold] = []
				solutions[threshold].append(solution)
		if self.discretized_names:
			named_solutions = {}
			for threshold in solutions:
				named_solutions[threshold] = []
				for itemset in solutions[threshold]:
					s = tuple([self.discretized_names[item] for item in itemset])
					named_solutions[threshold].append(s)
			solutions = named_solutions
		return solutions

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

def test_tree_building():
	T = [[1,1,0,1,1],[0,1,1,0,1],[1,1,0,1,1],[1,1,1,0,1],[1,1,1,1,1],[0,1,1,1,0]]
	fpt = FPTree(3).load_transactions(T)
	print(fpt)

def test_projection():
	T = [[1,1,0,1,1],[0,1,1,0,1],[1,1,0,1,1],[1,1,1,0,1],[1,1,1,1,1],[0,1,1,1,0]]
	fpt = FPTree(3).load_transactions(T)
	print("PROJECT: 3")
	print(fpt.project(3))
	print("PROJECT: 2")
	print(fpt.project(2))
	print("PROJECT: 0")
	print(fpt.project(0))
	print("PROJECT: 4")
	print(fpt.project(4))
	print("PROJECT: 1")
	print(fpt.project(1))
	print(fpt)

def test_fp_growth():
	T = [[1,1,0,1,1],
	    [0,1,1,0,1],
	    [1,1,0,1,1],
	    [1,1,1,0,1],
	    [1,1,1,1,1],
	    [0,1,1,1,0]]
	solutions = fp_growth(T,3)
	alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	for s in solutions:
		print([alphabet[i] for i in s])
	print("SOLUTIONS: {0}".format(len(solutions)))

def test_discretization():
	T = [[0.0749417049434653, 0.47955356469803334, 0.3003988003726794, 0.43098345314354636, 0.6214806456348348, 0.23950080880342106, 0.19368804850236376, 0.3099796805878434, 0.3372493874497201, 0.9638462398347232],
		[0.7041122457976033, 0.18374838591247133, 0.4321317486192555, 0.679356838110222, 0.2892176951157458, 0.3954409838738262, 0.9809593890458055, 0.6506815438103337, 0.9457975825867121, 0.09815536072771014],
		[0.9737472315421025, 0.7004632055256557, 0.7556385565428755, 0.22886499720331654, 0.4332049099410554, 0.8772439106456966, 0.8963844709187757, 0.6180246674366953, 0.8578656711255255, 0.30779868374984365],
		[0.050289925908512334, 0.5424980114115222, 0.8307928045014382, 0.6735869327039641, 0.5887357499768487, 0.19323753261032395, 0.4507479080892529, 0.004924981715803356, 0.027606789663687903, 0.024606253039842207],
		[0.834222994909624, 0.9419631024781285, 0.6499191080001684, 0.4287399883329528, 0.9643981803865654, 0.9006420891536407, 0.6808111670711892, 0.0874135568317912, 0.8140352351417328, 0.0699549310534322],
		[0.12476789340926919, 0.5969183016501332, 0.06042387645642078, 0.7180925227765411, 0.44410467786968777, 0.26541743459645484, 0.24403295721739093, 0.07228615874344724, 0.810960766284046, 0.5529050776232424],
		[0.7472370029484009, 0.8613403855167118, 0.4762109730740388, 0.7704518640065161, 0.16221403205506535, 0.22429338351371442, 0.9530617890253003, 0.3575790300741385, 0.8802749530675757, 0.6333662233864481]]
	fim = FrequentItemsetMiner()
	discretized_data = fim.initialize(T,discretization_function=discretize_on_avg)
	for r in discretized_data:
		print(r)

def test_discretization_with_names():
	N = ['Protein_1','Protein_2','Protein_3','Protein_4','Protein_5','Protein_6','Protein_7','Protein_8','Protein_9','Protein_10']
	T = [[0.0749417049434653, 0.47955356469803334, 0.3003988003726794, 0.43098345314354636, 0.6214806456348348, 0.23950080880342106, 0.19368804850236376, 0.3099796805878434, 0.3372493874497201, 0.9638462398347232],
		[0.7041122457976033, 0.18374838591247133, 0.4321317486192555, 0.679356838110222, 0.2892176951157458, 0.3954409838738262, 0.9809593890458055, 0.6506815438103337, 0.9457975825867121, 0.09815536072771014],
		[0.9737472315421025, 0.7004632055256557, 0.7556385565428755, 0.22886499720331654, 0.4332049099410554, 0.8772439106456966, 0.8963844709187757, 0.6180246674366953, 0.8578656711255255, 0.30779868374984365],
		[0.050289925908512334, 0.5424980114115222, 0.8307928045014382, 0.6735869327039641, 0.5887357499768487, 0.19323753261032395, 0.4507479080892529, 0.004924981715803356, 0.027606789663687903, 0.024606253039842207],
		[0.834222994909624, 0.9419631024781285, 0.6499191080001684, 0.4287399883329528, 0.9643981803865654, 0.9006420891536407, 0.6808111670711892, 0.0874135568317912, 0.8140352351417328, 0.0699549310534322],
		[0.12476789340926919, 0.5969183016501332, 0.06042387645642078, 0.7180925227765411, 0.44410467786968777, 0.26541743459645484, 0.24403295721739093, 0.07228615874344724, 0.810960766284046, 0.5529050776232424],
		[0.7472370029484009, 0.8613403855167118, 0.4762109730740388, 0.7704518640065161, 0.16221403205506535, 0.22429338351371442, 0.9530617890253003, 0.3575790300741385, 0.8802749530675757, 0.6333662233864481]]
	fim = FrequentItemsetMiner()
	discretized_data, discretized_names = fim.initialize(T,names = N, discretization_function=discretize_on_avg)
	print(discretized_names)
	for r in discretized_data:
		print(r)

def test_basic_fim():
	T = [[1,1,0,1,1],
	    [0,1,1,0,1],
	    [1,1,0,1,1],
	    [1,1,1,0,1],
	    [1,1,1,1,1],
	    [0,1,1,1,0]]
	fim = FrequentItemsetMiner()
	fim.initialize(T)
	solutions = fim.run([2,3,4])
	print(solutions)

def test_fim_with_duplicates():
	T = [[0.0749417049434653, 0.47955356469803334, 0.3003988003726794, 0.43098345314354636, 0.6214806456348348, 0.23950080880342106, 0.19368804850236376, 0.3099796805878434, 0.3372493874497201, 0.9638462398347232],
		[0.7041122457976033, 0.18374838591247133, 0.4321317486192555, 0.679356838110222, 0.2892176951157458, 0.3954409838738262, 0.9809593890458055, 0.6506815438103337, 0.9457975825867121, 0.09815536072771014],
		[0.9737472315421025, 0.7004632055256557, 0.7556385565428755, 0.22886499720331654, 0.4332049099410554, 0.8772439106456966, 0.8963844709187757, 0.6180246674366953, 0.8578656711255255, 0.30779868374984365],
		[0.050289925908512334, 0.5424980114115222, 0.8307928045014382, 0.6735869327039641, 0.5887357499768487, 0.19323753261032395, 0.4507479080892529, 0.004924981715803356, 0.027606789663687903, 0.024606253039842207],
		[0.834222994909624, 0.9419631024781285, 0.6499191080001684, 0.4287399883329528, 0.9643981803865654, 0.9006420891536407, 0.6808111670711892, 0.0874135568317912, 0.8140352351417328, 0.0699549310534322],
		[0.12476789340926919, 0.5969183016501332, 0.06042387645642078, 0.7180925227765411, 0.44410467786968777, 0.26541743459645484, 0.24403295721739093, 0.07228615874344724, 0.810960766284046, 0.5529050776232424],
		[0.7472370029484009, 0.8613403855167118, 0.4762109730740388, 0.7704518640065161, 0.16221403205506535, 0.22429338351371442, 0.9530617890253003, 0.3575790300741385, 0.8802749530675757, 0.6333662233864481]]
	fim = FrequentItemsetMiner()
	fim.initialize(T,discretization_function=discretize_on_avg)
	solutions = fim.run([4,5,6])
	print(solutions)

def test_fim_without_duplicates():
	T = [[0.0749417049434653, 0.47955356469803334, 0.3003988003726794, 0.43098345314354636, 0.6214806456348348, 0.23950080880342106, 0.19368804850236376, 0.3099796805878434, 0.3372493874497201, 0.9638462398347232],
		[0.7041122457976033, 0.18374838591247133, 0.4321317486192555, 0.679356838110222, 0.2892176951157458, 0.3954409838738262, 0.9809593890458055, 0.6506815438103337, 0.9457975825867121, 0.09815536072771014],
		[0.9737472315421025, 0.7004632055256557, 0.7556385565428755, 0.22886499720331654, 0.4332049099410554, 0.8772439106456966, 0.8963844709187757, 0.6180246674366953, 0.8578656711255255, 0.30779868374984365],
		[0.050289925908512334, 0.5424980114115222, 0.8307928045014382, 0.6735869327039641, 0.5887357499768487, 0.19323753261032395, 0.4507479080892529, 0.004924981715803356, 0.027606789663687903, 0.024606253039842207],
		[0.834222994909624, 0.9419631024781285, 0.6499191080001684, 0.4287399883329528, 0.9643981803865654, 0.9006420891536407, 0.6808111670711892, 0.0874135568317912, 0.8140352351417328, 0.0699549310534322],
		[0.12476789340926919, 0.5969183016501332, 0.06042387645642078, 0.7180925227765411, 0.44410467786968777, 0.26541743459645484, 0.24403295721739093, 0.07228615874344724, 0.810960766284046, 0.5529050776232424],
		[0.7472370029484009, 0.8613403855167118, 0.4762109730740388, 0.7704518640065161, 0.16221403205506535, 0.22429338351371442, 0.9530617890253003, 0.3575790300741385, 0.8802749530675757, 0.6333662233864481]]
	fim = FrequentItemsetMiner(duplicate_solutions=False)
	fim.initialize(T,discretization_function=discretize_on_avg)
	solutions = fim.run([4,5,6])
	print(solutions)

def test_fim_with_duplicates_and_names():
	N = ['Protein_1','Protein_2','Protein_3','Protein_4','Protein_5','Protein_6','Protein_7','Protein_8','Protein_9','Protein_10']
	T = [[0.0749417049434653, 0.47955356469803334, 0.3003988003726794, 0.43098345314354636, 0.6214806456348348, 0.23950080880342106, 0.19368804850236376, 0.3099796805878434, 0.3372493874497201, 0.9638462398347232],
		[0.7041122457976033, 0.18374838591247133, 0.4321317486192555, 0.679356838110222, 0.2892176951157458, 0.3954409838738262, 0.9809593890458055, 0.6506815438103337, 0.9457975825867121, 0.09815536072771014],
		[0.9737472315421025, 0.7004632055256557, 0.7556385565428755, 0.22886499720331654, 0.4332049099410554, 0.8772439106456966, 0.8963844709187757, 0.6180246674366953, 0.8578656711255255, 0.30779868374984365],
		[0.050289925908512334, 0.5424980114115222, 0.8307928045014382, 0.6735869327039641, 0.5887357499768487, 0.19323753261032395, 0.4507479080892529, 0.004924981715803356, 0.027606789663687903, 0.024606253039842207],
		[0.834222994909624, 0.9419631024781285, 0.6499191080001684, 0.4287399883329528, 0.9643981803865654, 0.9006420891536407, 0.6808111670711892, 0.0874135568317912, 0.8140352351417328, 0.0699549310534322],
		[0.12476789340926919, 0.5969183016501332, 0.06042387645642078, 0.7180925227765411, 0.44410467786968777, 0.26541743459645484, 0.24403295721739093, 0.07228615874344724, 0.810960766284046, 0.5529050776232424],
		[0.7472370029484009, 0.8613403855167118, 0.4762109730740388, 0.7704518640065161, 0.16221403205506535, 0.22429338351371442, 0.9530617890253003, 0.3575790300741385, 0.8802749530675757, 0.6333662233864481]]
	fim = FrequentItemsetMiner()
	fim.initialize(T, names=N, discretization_function=discretize_on_avg)
	solutions = fim.run([4,5,6])
	print(solutions)

def test_fim_without_duplicates_and_names():
	N = ['Protein_1','Protein_2','Protein_3','Protein_4','Protein_5','Protein_6','Protein_7','Protein_8','Protein_9','Protein_10']
	T = [[0.0749417049434653, 0.47955356469803334, 0.3003988003726794, 0.43098345314354636, 0.6214806456348348, 0.23950080880342106, 0.19368804850236376, 0.3099796805878434, 0.3372493874497201, 0.9638462398347232],
		[0.7041122457976033, 0.18374838591247133, 0.4321317486192555, 0.679356838110222, 0.2892176951157458, 0.3954409838738262, 0.9809593890458055, 0.6506815438103337, 0.9457975825867121, 0.09815536072771014],
		[0.9737472315421025, 0.7004632055256557, 0.7556385565428755, 0.22886499720331654, 0.4332049099410554, 0.8772439106456966, 0.8963844709187757, 0.6180246674366953, 0.8578656711255255, 0.30779868374984365],
		[0.050289925908512334, 0.5424980114115222, 0.8307928045014382, 0.6735869327039641, 0.5887357499768487, 0.19323753261032395, 0.4507479080892529, 0.004924981715803356, 0.027606789663687903, 0.024606253039842207],
		[0.834222994909624, 0.9419631024781285, 0.6499191080001684, 0.4287399883329528, 0.9643981803865654, 0.9006420891536407, 0.6808111670711892, 0.0874135568317912, 0.8140352351417328, 0.0699549310534322],
		[0.12476789340926919, 0.5969183016501332, 0.06042387645642078, 0.7180925227765411, 0.44410467786968777, 0.26541743459645484, 0.24403295721739093, 0.07228615874344724, 0.810960766284046, 0.5529050776232424],
		[0.7472370029484009, 0.8613403855167118, 0.4762109730740388, 0.7704518640065161, 0.16221403205506535, 0.22429338351371442, 0.9530617890253003, 0.3575790300741385, 0.8802749530675757, 0.6333662233864481]]
	fim = FrequentItemsetMiner(duplicate_solutions=False)
	fim.initialize(T, names=N, discretization_function=discretize_on_avg)
	solutions = fim.run([4,5,6])
	print(solutions)

if __name__ == "__main__":
	test_tree_building()
	test_projection()
	test_fp_growth()
	test_discretization()
	test_discretization_with_names()
	print("WITH DUPLICATES:")
	test_fim_with_duplicates()
	print("WITHOUT DUPLICATES:")
	test_fim_without_duplicates()
	print("BASIC")
	test_basic_fim()
	print("WITH NAMES")
	test_fim_with_duplicates_and_names()
	test_fim_without_duplicates_and_names()