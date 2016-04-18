# fim_cancer
A data mining project focused on discovering complex protein expression correlations using Frequent Itemset Mining on data from cancer patients.

<h1>Controller</h2>
<p>The overarching controller is responsible for data reading, preprocessing, and feeding our subroutines. This means we need to take the raw data files as presented by TCPA or cBioportal and scrub them so that they can fed into our modules. The pipeline is as follows, we parse out the proteins, patients, and transactions data from the reduced expressions data (we remove irrelevant columns). From here we run fim on the transactions and map the result from indices to names. Fim will give us our discretized transactions that then needs to be formatted into a table structure. We also need to produce a table from our clinical data. Once we have our in-memory tables we simply run the confirmer of our finder in a loop over all the solutions (frequent item sets). As we discover z-scores we can do the ranking of the sets in place or after we are done looping.  We can output our result either permanent storage or house them in memory.
</p>

```python
c=controller('examples/data/TCGA-THCA-L3-S54_reduced.csv','examples/data/thca_tcga_clinical_data.tsv',[4,5,6])
print(c.ranks) 
```
