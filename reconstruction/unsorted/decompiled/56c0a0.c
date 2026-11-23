
int FUN_0056c0a0(long param_1,char param_2,long *param_3)

{
  int iVar1;
  char *pcVar2;
  
  iVar1 = 0;
  if (*param_3 != 0) {
    for (pcVar2 = (char *)(param_1 + 0x89);
        (pcVar2[-0x29] != param_2 || (*(long *)(pcVar2 + -9) != *param_3)); pcVar2 = pcVar2 + 0x40)
    {
    }
    iVar1 = (int)*pcVar2;
  }
  return iVar1;
}

