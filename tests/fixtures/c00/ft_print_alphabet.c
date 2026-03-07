#include <stdlib.h>
#include <unistd.h>

void	ft_print_alphabet(void)
{
	char	*buf;
	int		i;

	buf = malloc(27);
	i = 0;
	while (i < 26)
	{
		buf[i] = 'a' + i;
		i++;
	}
	buf[26] = '\0';
	write(1, buf, 26);
	free(buf);
}
