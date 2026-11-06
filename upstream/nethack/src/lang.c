/* NetHack-es: language detection for i18n */
#include "hack.h"
#if defined(WIN32)
#include <windows.h> /* GetModuleFileNameA, MAX_PATH */
#endif

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
#if defined(WIN32)
        /* En Windows, la traduccion se distribuye junto al ejecutable.
         * HACKDIR (\\nethack) no apunta a la carpeta instalada.
         */
        char mo_path[MAX_PATH + 64];
        DWORD len = GetModuleFileNameA(NULL, mo_path, MAX_PATH);
        if (len > 0 && len < MAX_PATH) {
            char *file = strrchr(mo_path, '\\');
            if (!file)
                file = strrchr(mo_path, '/');
            if (file) {
                *(file + 1) = '\0';
                Strcat(mo_path, "locale\\");
                Strcat(mo_path, current_lang);
                Strcat(mo_path, "\\LC_MESSAGES\\nethack.mo");
                nh_load_mo(mo_path);
            }
        }
#else
        char mo_path[BUFSZ];
        Strcpy(mo_path, HACKDIR "/locale/");
        Strcat(mo_path, current_lang);
        Strcat(mo_path, "/LC_MESSAGES/nethack.mo");
        nh_load_mo(mo_path);
#endif
    }
}
