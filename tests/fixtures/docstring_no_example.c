/*
 * ft_is_alpha
 *
 * # About
 *
 * Returns 1 when the character is alphabetic.
 *
 * @param[c]: character to test.
 */
intft_is_alpha(char c)
{
return ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'));
}
