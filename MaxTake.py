#Find the maximum sum that can be achieved in a list of values, if no consecutive values can be used.
def findMaxReturn(values):
	#If the array is empty, return 0, as there's nothing else to add in this path
	if(len(values)==0):
		return 0
	#If there are only one or two options left, return the greater value.
	if(len(values)<=2):
		return max(values)
	#Choose either the first or second option, and then run the function recursively on the
	#available remainder of the street
	opt1 = values[0] + findMaxReturn(values[2:])
	opt2 = values[1] + findMaxReturn(values[3:])
	return max(opt1, opt2)
	
	
print findMaxReturn([1, 2, 3, 4, 5])
print findMaxReturn([9, 2, 3, 7, 12, 6, 15, 8])
print findMaxReturn([20, 50, 10, 5, 1])
print findMaxReturn([20, 50, 10, 5, 1, 10])
print findMaxReturn([20, 2, 3, 20, 8, 13, 20, 4, 15, 20])