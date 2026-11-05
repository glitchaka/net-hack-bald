/* NetHack-es: language detection for i18n */
#include "hack.h"

static char current_lang[8] = "en"; /* default: English */

/* init_lang: detect language from LANG environment variable */
void init_lang(void)
{
    const char *env = nh_getenv("LANG");
    if (env && strlen(env) >= 2 && isalpha((int)env[0])
        && isalpha((int)env[1])) {
        current_lang[0] = tolower((int)env[0]);
        current_lang[1] = tolower((int)env[1]);
        current_lang[2] = '\0';
        /* Validate: only "es" and "en" for now */
        if (strcmp(current_lang, "es") != 0
            && strcmp(current_lang, "en") != 0)
            strcpy(current_lang, "en");
    } else {
        strcpy(current_lang, "en");
    }
}

/* get_lang: return the two-letter language code */
const char *get_lang(void)
{
    return current_lang;
}

/* set_lang: change language at runtime (from nethackrc OPTIONS=language:xx)
 * Falls back to "en" if the code is not supported.
 */
void set_lang(const char *code)
{
    if (!code || strlen(code) < 2) {
        strcpy(current_lang, "en");
        return;
    }
    current_lang[0] = tolower((int)code[0]);
    current_lang[1] = tolower((int)code[1]);
    current_lang[2] = '\0';
    if (strcmp(current_lang, "es") != 0
        && strcmp(current_lang, "en") != 0)
        strcpy(current_lang, "en");
    if (strcmp(current_lang, "en") != 0) {
        /* Reload the .mo file for the new language */
        char mo_path[BUFSZ];
        Strcpy(mo_path, HACKDIR "/locale/");
        Strcat(mo_path, current_lang);
        Strcat(mo_path, "/LC_MESSAGES/nethack.mo");
        nh_load_mo(mo_path);
    }
}
