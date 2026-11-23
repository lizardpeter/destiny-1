
undefined1 FUN_002cf080(undefined8 *param_1,undefined8 param_2)

{
  uint uVar1;
  long lVar2;
  long lVar3;
  char cVar4;
  ulong uVar5;
  undefined8 uVar6;
  long lVar7;
  uint uVar8;
  
  lVar2 = param_1[1];
  if (lVar2 == 0) {
    lVar2 = param_1[2];
    if (lVar2 == 0) {
      return 0;
    }
    if (*(int *)(lVar2 + 0x88) == 0) {
      return 0;
    }
    if (*(int *)(lVar2 + 0x88) == -1) {
      return 0;
    }
    if (*(int *)(lVar2 + 0x90) == -1) {
      return 0;
    }
    uVar6 = FUN_00108a90();
    cVar4 = FUN_00001f70(uVar6);
    if (cVar4 != '\0') {
      FUN_00353510(param_1[2] + 0x88,*param_1,param_2);
    }
  }
  else {
    if (*(int *)(lVar2 + 0x88) == 0) {
      return 0;
    }
    if (*(int *)(lVar2 + 0x88) == -1) {
      return 0;
    }
    if (*(int *)(lVar2 + 0x90) == -1) {
      return 0;
    }
    cVar4 = FUN_001081b0();
    if (cVar4 == '\0') {
      return 0;
    }
    uVar1 = *(uint *)param_1[1];
    uVar8 = (int)uVar1 >> 0xd;
    lVar7 = (ulong)((uVar8 >> 0x12 | 0x3ff) & uVar8) * 0x40;
    lVar2 = *DAT_01a238a0;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar7);
    uVar5 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar7));
    cVar4 = FUN_00001f70(*(long *)((uint *)param_1[1] + 2) + 0x40 +
                         ((lVar3 + uVar5) -
                         ((long)*(int *)(lVar2 + 0x34 + lVar7) & *(ulong *)(lVar3 + 8 + uVar5))));
    if (cVar4 != '\0') {
      FUN_00352fa0(param_1[1] + 0x88,param_2);
    }
  }
  FUN_000f8210();
  return 1;
}

