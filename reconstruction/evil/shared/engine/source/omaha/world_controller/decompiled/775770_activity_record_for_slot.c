
char * FUN_00775770(int param_1)

{
  char *pcVar1;
  char *pcVar2;
  long lVar3;
  
  if (DAT_026ca4e0 != (char *)0x0) {
    pcVar1 = (char *)0x0;
    if (*DAT_026ca4e0 != '\0') {
      pcVar1 = DAT_026ca4e0;
    }
    if ((pcVar1 != (char *)0x0) && (param_1 != -1)) {
      lVar3 = (long)param_1 * 0x131c8;
      if (*(uint *)(pcVar1 + (long)*(int *)(pcVar1 + lVar3 + 8) * 0x98e0 + 0x8c58 + lVar3) < 0xb) {
        pcVar2 = (char *)0x0;
        if ((0x7f0U >> (*(uint *)(pcVar1 + (long)*(int *)(pcVar1 + lVar3 + 8) * 0x98e0 + 0x8c58 +
                                           lVar3) & 0x1f) & 1) != 0) {
          pcVar2 = pcVar1 + (long)*(int *)(pcVar1 + lVar3 + 8) * 0x98e0 + 0x6b38 + lVar3;
        }
        return pcVar2;
      }
    }
  }
  return (char *)0x0;
}

