
void FUN_007ace30(long param_1)

{
  long lVar1;
  char cVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  char *pcVar6;
  undefined8 uVar7;
  
  iVar3 = FUN_00788e30();
  if (iVar3 != 0x13) {
    return;
  }
  uVar4 = FUN_00765ee0();
  cVar2 = FUN_007581e0(uVar4);
  if (cVar2 != '\0') {
    lVar1 = *(long *)(param_1 + 0x38);
    if (lVar1 == -1) {
      return;
    }
    lVar5 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar5 = FUN_000694d0();
    }
    if (lVar5 - lVar1 < 0x1389) {
      return;
    }
  }
  pcVar6 = (char *)FUN_00574ef0();
  if ((*pcVar6 == '\x01') && (cVar2 = FUN_00545230(*(undefined2 *)(pcVar6 + 2)), cVar2 == '\0')) {
    iVar3 = *(int *)(param_1 + 0x30);
    uVar7 = 0x13;
  }
  else {
    iVar3 = *(int *)(param_1 + 0x30);
    uVar4 = 0x21;
    if ((iVar3 - 5U < 2) || (uVar7 = 0x22, iVar3 == 0x119)) goto LAB_007aced0;
  }
  uVar4 = uVar7;
  if (iVar3 == 4) {
    return;
  }
LAB_007aced0:
  FUN_00788e10(uVar4);
  return;
}

