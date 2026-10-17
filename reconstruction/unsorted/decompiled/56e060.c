
void FUN_0056e060(undefined8 param_1,char *param_2)

{
  char *pcVar1;
  
  if (DAT_026bacc0 != 0) {
    for (pcVar1 = (char *)(DAT_026bacc0 + 0x8b);
        (pcVar1[-0x2b] != *param_2 || (*(long *)(pcVar1 + -0xb) != *(long *)(param_2 + 8)));
        pcVar1 = pcVar1 + 0x40) {
    }
    *pcVar1 = param_2[1];
  }
  return;
}

