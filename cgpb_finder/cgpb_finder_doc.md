<h1>cGPBFinder</h1>
<h2>Introduction</h2>
<p>The cGPBfinder, one of our main subroutines is responsible for searching and counting up the number of instances of a particular item set. The finder is a simple linear search through our data. It can be run multiple times for different itemset instances. </p> 
<h2>Parsing the search space</h2>

<p>dict = { t1: {p1:[x11,y11],p2:[x12,y12]}, t2: {p1:[x21,y21] ... }}</p>

<p>The search space is composed from the reduced clinical and discretized expression data. The procedure for initializing the space is as follows: We take the expression data as is and read it into our dictionary, marking for each entry e whether or not the transaction expresses this protein or not. Nextly we read through the clinical data and mark in the dictionary whether or not the transaction (patient) is alive or dead. We remove transactions that either aren’t present in the clinical data or have a value that is something other than “Alive” or “Deceased”. This assures that our search space has good data.</p>

<p>Once the space is established it’s a matter of doing a linear search through it to ascertain the counts on each of the possible situations: Expressed, Unexpressed, Expressed/Alive, Expressed/Dead, Unexpressed/Alive, and finally Unexpressed/Dead. There maybe some level in redundancy in counting both Alive and Dead cases but we lose nothing performance wise by keeping an incremental count of both. We do our search patient-wise, for each patient marking off whether or not they express the proteins within the frequent item set. If a protein(s) from the frequent item set is missing then this patient isn’t expressing this set otherwise they are. We also note whether or not they are alive we only need to check one of the entries e in the transaction to confirm this.</p>

<h2>Significance Testing</h2>
<p>Once the counting is done we apply the two-proportions-z test on the following proportions: (Expressed & Alive)/Expressed and (Unexpressed & Alive)/Unexpressed. The test will return to us a z-score which indicates how different these two proportions are from one another.
Based on the z-score associated with each set we can establish a ranking of the ones that either least or most significant. 

<h2>Using it</h2>
<p>To use the cGPBFinder for an individual set we run the code as followed:</p>

```python
from cgpb_finder import cgpb_finder
finder = cGBPFinder('input_clinic.tsv','input_expr.tsv')
finder.confirmcGPB(['p1','p2'])
```
