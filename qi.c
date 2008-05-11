#include <stdio.h>
#include <assert.h>

void print(long* array, int len, int lower, int upper)
{
	printf("len: %d, lower: %d, upper: %d\n", len, lower, upper);
	int i;
	for(i = lower; i < upper; i++)
	{
		printf("%d:%ld ", i, array[i]);
	}
	printf("\n");
}

int getIndexOf(long* array, int len, long timestamp)
{	
	printf("Looking for: %ld\n", timestamp);
	long first = array[0];
	if(first >= timestamp)
		return 0;
	
	long last = array[len - 1];
	if(last < timestamp)
		return len;

	int lower = 0;
	int upper = len;
	int range = upper - lower;
		
	while(range > 2)
	{
		print(array, len, lower, upper);

		int half = range / 2;
		int index = lower + half;
		long cur = array[index];
		if(timestamp > cur)
			lower = index;
		else if(timestamp < cur)
			upper = index + 1;
		else
			return index;
		range = upper - lower;
	}

	int i;
	for(i = lower; i < upper; i++)
	{
		long cur = array[i];
		if(cur >= timestamp)
		{
			printf("ret: %d\n", i);
			return i;
		}
	}
	
	printf("ret: %d\n", len);
	return len;
}

int main (int argc, const char * argv[]) 
{
	long array[] = 
	{
		100,    // 0
		140,    // 1
		2000,   // 2
		2001,   // 3
		2202,   // 4
		3000,   // 5
		4000,   // 6
		5510,   // 7
		5560,   // 8
		6787    // 9
	};
	
	int len = sizeof(array) / sizeof(long);
	assert(getIndexOf(array, len, 3003) == 6);
	assert(getIndexOf(array, len, 3000) == 5);
	assert(getIndexOf(array, len, 2999) == 5);
	assert(getIndexOf(array, len, 1) == 0);
	assert(getIndexOf(array, len, 9000) == 10);

	long array1[] =
	{
		100     // 0
	};
	int len1 = sizeof(array1) / sizeof(long);
	assert(getIndexOf(array1, len1, 1) == 0);
	assert(getIndexOf(array1, len1, 100) == 0);
	assert(getIndexOf(array1, len1, 200) == 1);
	
	long array2[] = 
	{
		100,    // 0
		140     // 1
	};
	int len2 = sizeof(array2) / sizeof(long);
	assert(getIndexOf(array2, len2, 1) == 0);
	assert(getIndexOf(array2, len2, 100) == 0);
	assert(getIndexOf(array2, len2, 120) == 1);
	assert(getIndexOf(array2, len2, 140) == 1);
	assert(getIndexOf(array2, len2, 150) == 2);
	
	long array3[] =
	{
		100,
		200,
		300
	};
	int len3 = sizeof(array3) / sizeof(long);
	assert(getIndexOf(array3, len3, 1) == 0);
	assert(getIndexOf(array3, len3, 100) == 0);
	assert(getIndexOf(array3, len3, 101) == 1);
	assert(getIndexOf(array3, len3, 200) == 1);
	assert(getIndexOf(array3, len3, 201) == 2);
	assert(getIndexOf(array3, len3, 300) == 2);
	assert(getIndexOf(array3, len3, 301) == 3);

	long array3x[] =
	{
		100,
		200,
		200
	};
	int len3x = sizeof(array3x) / sizeof(long);
	assert(getIndexOf(array3x, len3x, 1) == 0);
	assert(getIndexOf(array3x, len3x, 100) == 0);
	assert(getIndexOf(array3x, len3x, 101) == 1);
	assert(getIndexOf(array3x, len3x, 200) == 1);
	assert(getIndexOf(array3x, len3x, 201) == 3);
	
    return 0;
}
