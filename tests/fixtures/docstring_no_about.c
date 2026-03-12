/*
 * ft_strlen
 *
 * # Example
 *
 * ```c
 * intmain(void)
 * {
 * intlen;
 *
 * len = ft_strlen("abc");
 * return (len);
 * }
 * ```
 *
 * @param[str]: input string.
 */
intft_strlen(char *str)
{
intlen;

len = 0;
while (str[len])
len++;
return (len);
}
