
void FUN_003469a0(long param_1,int *param_2)

{
  long lVar1;
  int iVar2;
  long lVar3;
  short sVar4;
  int *piVar5;
  long lVar6;
  
  lVar3 = DAT_02693bf8;
  if (*param_2 == 2) {
    lVar6 = param_1 + 0x10;
  }
  else {
    lVar6 = param_1 + 0x20;
  }
  iVar2 = param_2[1];
  lVar1 = DAT_02693bf8 + 0xc050;
  sVar4 = FUN_00077100(lVar1,1,lVar6);
  if ((sVar4 == -1) ||
     (piVar5 = (int *)((ulong)*(ushort *)(lVar6 + 2) * *(long *)(lVar3 + 0xc060) +
                      lVar1 + *(long *)(lVar3 + 0xc050)), piVar5 == (int *)0x0)) {
    if (*(char *)(param_1 + 6) == '\x02') {
      *(int *)(lVar3 + 8) = *(int *)(lVar3 + 8) + -1;
    }
    else {
      *(int *)(lVar3 + 4) = *(int *)(lVar3 + 4) + -1;
    }
    *(undefined1 *)(param_1 + 7) = 3;
    *(undefined1 *)(param_1 + 9) = 1;
  }
  else {
    *piVar5 = iVar2;
  }
  return;
}

