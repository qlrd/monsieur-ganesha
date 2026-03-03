#include <stdio.h>
#include <stdlib.h>

int	main(void)
{
	char	*buf;

	buf = malloc(42);
	printf("Hello, World!\n");
	free(buf);
	return (0);
}
