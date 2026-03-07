#include <stdio.h>

void	ft_print_numbers(void)
{
	char	c;

	c = '0';
	while (c <= '9')
	{
		printf("%c", c);
		c++;
	}
}
