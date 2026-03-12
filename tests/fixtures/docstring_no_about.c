/*
 * ft_strlen
 *
 * # Example
 *
 * ```c
 * int main(void)
 * {
 * 	int	len;
 *
 * 	len = ft_strlen("abc");
 * 	return (len);
 * }
 * ```
 *
 * @param[str]: input string.
 */
int ft_strlen(char *str)
{
	int	len;

	len = 0;
	while (str[len])
		len++;
	return (len);
}
