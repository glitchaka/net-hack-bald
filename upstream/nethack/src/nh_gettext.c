/* NetHack-es: lightweight .mo file loader for i18n */
#include "config.h"
#include "tradstdc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned char *mo_data = NULL;
static int mo_loaded = 0;
static long mo_size = 0;

/* .mo file magic numbers */
#define MO_MAGIC_LE 0x950412de
#define MO_MAGIC_BE 0xde120495

/* Load the .mo file from the given path */
void nh_load_mo(const char *path)
{
    FILE *f;

    /* Free previous translation data if reloading */
    if (mo_data) {
        free(mo_data);
        mo_data = NULL;
        mo_loaded = 0;
    }

    f = fopen(path, "rb");
    if (!f) return;

    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    rewind(f);

    if (size < 20) { /* .mo files have at least a 20-byte header */
        fclose(f);
        return;
    }

    mo_data = (unsigned char *)malloc(size);
    if (!mo_data) { fclose(f); return; }

    if (fread(mo_data, 1, size, f) != (size_t)size) {
        free(mo_data);
        mo_data = NULL;
        fclose(f);
        return;
    }
    fclose(f);

    /* Verify magic */
    {
        unsigned int magic_check;
        memcpy(&magic_check, mo_data, 4);
        if (magic_check != MO_MAGIC_LE && magic_check != MO_MAGIC_BE) {
            free(mo_data);
            mo_data = NULL;
            return;
        }
    }

    mo_loaded = 1;
    mo_size = size;
}

/* nh_gettext: lookup a string in the loaded .mo file */
const char *nh_gettext(const char *msgid)
{
    if (!mo_loaded || !mo_data || !msgid || !*msgid)
        return msgid;

    /* Parse .mo header */
    unsigned int magic_check, version, count;
    unsigned int orig_offset, trans_offset;
    int little_endian;

    memcpy(&magic_check, mo_data, 4);
    little_endian = (magic_check == MO_MAGIC_LE);

#define GET_U32(ptr) (little_endian ? \
    (unsigned int)((ptr)[0] | ((ptr)[1]<<8) | ((ptr)[2]<<16) | ((ptr)[3]<<24)) : \
    (unsigned int)((ptr)[3] | ((ptr)[2]<<8) | ((ptr)[1]<<16) | ((ptr)[0]<<24)))

    version = GET_U32(mo_data + 4);
    if (version != 0) return msgid;

    count = GET_U32(mo_data + 8);
    orig_offset = GET_U32(mo_data + 12);
    trans_offset = GET_U32(mo_data + 16);

    /* Sanity checks to prevent out-of-bounds access */
    if ((unsigned long)orig_offset >= (unsigned long)mo_size
        || (unsigned long)trans_offset >= (unsigned long)mo_size)
        return msgid;
    if (count > 1000000)
        return msgid;

    /* Binary search through the sorted original strings */
    int lo = 0, hi = count - 1;
    while (lo <= hi) {
        int mid = (lo + hi) / 2;
        unsigned long entry_off = (unsigned long)orig_offset + (unsigned long)mid * 8;
        if (entry_off + 8 > (unsigned long)mo_size)
            return msgid;
        unsigned int str_offset = GET_U32(mo_data + entry_off + 4);
        unsigned int str_len = GET_U32(mo_data + entry_off);

        if ((unsigned long)str_offset >= (unsigned long)mo_size)
            return msgid;

        const char *str = (const char *)(mo_data + str_offset);
        int cmp = strcmp(msgid, str);

        if (cmp == 0) {
            /* Found! Return translation */
            unsigned long tentry = (unsigned long)trans_offset + (unsigned long)mid * 8;
            if (tentry + 8 > (unsigned long)mo_size)
                return msgid;
            unsigned int t_offset = GET_U32(mo_data + tentry + 4);
            unsigned int t_len = GET_U32(mo_data + tentry);
            if ((unsigned long)t_offset + (unsigned long)t_len > (unsigned long)mo_size)
                return msgid;
            (void)t_len;
            return (const char *)(mo_data + t_offset);
        } else if (cmp < 0) {
            hi = mid - 1;
        } else {
            lo = mid + 1;
        }
    }

    return msgid; /* Not found */
}
