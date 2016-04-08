# FP-Growth Module

_by Eugene Kovalev_

## Introduction

The FP-Growth Module is a program written to peform frequent itemset mining using the Fp-Growth Algorithm. It is capable of a surprising amount of flexibility for discretization of data.

## Using the FP-Growth Module

The basic idea behind using the FP-Growth Module is that you give it a set of transactions, a discretization function, and a set of thresholds for which you want it to compute frequent itemsets.

### Simple Use Case

The simple use case, i.e. to find all frequent itemsets from a discretized set of data, is as follows:

```python
from fp_growth import fp_growth

T = [[1,1,0,1,1],
    [0,1,1,0,1],
    [1,1,0,1,1],
    [1,1,1,0,1],
    [1,1,1,1,1],
    [0,1,1,1,0]]
solutions = fp_growth(T,3)
```

Note that this is extremely simple. You get your data set, which has to be a list of transactions, and you simply call the `fp_growth()` function with the data set and a threshold of 3. Again, this is extremely simplistic and not necessarily the function you wanna use. I recommend reading further for those advanced functions.

### FrequentItemsetMiner Object - Basic Use-Case

You can use the FrequentItemsetMiner object for fim as well if your data set is already discrete, like so:

```python
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
```

If you do not pass in a discretization function, the FrequentItemsetMiner simply uses the given dataset for its calculations and treats it as discrete.

### Discretizing Data

The more advanced functions can be performed using the FrequentItemsetMiner object. One of the things that it can do is discretization.

Sometimes we have a set of floating point data instead of discrete data. In this case, a a discretization function is required for the FrequentItemsetMiner object to be able to get the number of frequent itemsets. You need to define this function. The only requirement is that the function take one parameter, a column of data, and return a list of columns of data based on the input column.

For example, let's say we have a very simple floating point data set that we wish to turn into 0s and 1s based on the average as the dividing line. We can write the following discretization function:

```python
def discretize_on_avg(column):
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
	return [high_column, low_column]
```

Now we can use that function (this one is actually implemented in fp_growth for your convenience) to initialize our FrequentItemsetMiner object:

```python
from fp_growth import FrequentItemsetMiner, discretize_on_avg

T = [...]
fim = FrequentItemsetMiner()
discretized_data = fim.initialize(T,discretize_on_avg)
```

The `initialize()` function on the FrequentItemsetMiner object returns the discretized version of T, which is the data that results from discretizing T with the given discretization function.

You do not have to receive the value returned from `initialize()` and can get the discretized data at any time after the initialization step by accessing the `discretized_transactions` value of your FrequentItemsetMiner instance, like so:

```python
from fp_growth import FrequentItemsetMiner, discretize_on_avg

T = [...]
fim = FrequentItemsetMiner()
fim.initialize(T,discretize_on_avg)
print(fim.discretized_transactions)
```

### Frequent Itemset Mining

But how do we use the FrequentItemsetMiner for efficient data mining? Well, that's quite easy. There are two main ways to actually run it for frequent-itemset mining: The first is with duplicate solutions, and the second is without. The reason for this distinction is that if you have many thresholds, some solutions (i.e. frequent itemsets) may appear multiple times for different thresholds. This may be annoying in some cases and useful in others. Therefore our implementation allows you to do both.

To get all the frequent itemsets for each threshold with duplicates and all, you can do the following:

```python
from fp_growth import FrequentItemsetMiner, discretize_on_avg

T = [...]
fim = FrequentItemsetMiner()
fim.initialize(T,discretize_on_avg)
solutions = fim.run([4,5,6])
print(solutions)
```

Here we can see that to run the frequent itemset mining calculation, we simply call the `run()` function and give it a set of thresholds to use. The output is a dictionary keyed by threshold where each entry is a list of tuples where each tuple represents a frequent itemset, like so:

```python
{4: [(), (19,), (14,), (12,), (16, 12), (12, 0), (9,), (16, 9), (6,), (11, 6), (5,), (11, 5), (3,), (11, 3), (0,), (16, 0), (16,), (11,)], 5: [(), (16,), (11,)], 6: [()]}
```

The numbers inside the tuples are the indices of the items that are part of the frequent itemset (the index of the column in the discretized dataset representing the item).

If we do not want duplicates, we can use the following approach:

```python
from fp_growth import FrequentItemsetMiner, discretize_on_avg

T = [...]
fim = FrequentItemsetMiner(duplicate_solutions=False)
fim.initialize(T,discretize_on_avg)
solutions = fim.run([4,5,6])
print(solutions)
```

Now that we have set `duplicate_solutions` set to `False` the output (in the same format as above) will only include frequent itemsets with the _maximum_ threshold that they meet, like so:

```python
{4: [(16, 0), (0,), (12, 0), (16, 9), (11, 5), (3,), (11, 3), (9,), (5,), (6,), (12,), (19,), (14,), (11, 6), (16, 12)], 5: [(16,), (), (11,)]}
```

Note that the frequent itemset `16` (containing only the item 16) should appear for thresholds 4 and 5 because if it appears at least 5 times then it appears 4 times as well. However, here, it only appears at the maximum associated threshold which happens to be 5.