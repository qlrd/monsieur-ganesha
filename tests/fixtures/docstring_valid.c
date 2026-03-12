/*
 * ft_str_is_lowercase
 *
 * # About
 *
 * Returns 1 if the string only contains lowercase letters.
 *
 * # Example
 *
 * ```c
 * int	main(void)
 * {
 * 	int	ok;
 *
 * 	ok = ft_str_is_lowercase("abc");
 * 	return (ok);
 * }
 * ```
 *
 * @param[str]: input string to validate.
 */
int	ft_str_is_lowercase(char *str)
{
	while (*str)
	{
		if (*str < 'a' || *str > 'z')
			return (0);
		str++;
	}
	return (1);
}
