
/* File generated by gen_cfile.py. Should not be modified. */

#ifndef EXAMPLE_OBJDICT_H
#define EXAMPLE_OBJDICT_H

#include "data.h"

/* Prototypes of function provided by object dictionnary */
UNS32 Linux_slave_valueRangeTest (UNS8 typeValue, void * value);
const indextable * Linux_slave_scanIndexOD (UNS16 wIndex, UNS32 * errorCode, ODCallback_t **callbacks);

/* Master node data struct */
extern CO_Data Linux_slave_Data;
extern UNS8 Time_seconds;		/* Mapped at index 0x2000, subindex 0x01 */
extern UNS8 Time_minutes;		/* Mapped at index 0x2000, subindex 0x02 */
extern UNS8 Time_hours;		/* Mapped at index 0x2000, subindex 0x03 */
extern UNS8 Time_days;		/* Mapped at index 0x2000, subindex 0x04 */
extern UNS32 canopenErrNB;		/* Mapped at index 0x2001, subindex 0x00*/
extern UNS32 canopenErrVal;		/* Mapped at index 0x2002, subindex 0x00*/
extern INTEGER8 strTest[10];		/* Mapped at index 0x2003, subindex 0x00*/

#endif // EXAMPLE_OBJDICT_H
