
void FUN_007d9270(long param_1,uint param_2,undefined4 *param_3,long param_4)

{
  long lVar1;
  undefined8 uVar2;
  char cVar3;
  long lVar4;
  undefined4 *puVar5;
  long lVar6;
  ulong uVar7;
  
  lVar6 = 0;
  if (param_2 != 0xffffffff) {
    lVar4 = (ulong)(((uint)((int)param_2 >> 0xd) >> 0x12 | 0x3ff) & (int)param_2 >> 0xd) * 0x40;
    lVar6 = *DAT_01a238a0;
    lVar1 = *(long *)(lVar6 + 0x10 + lVar4);
    uVar7 = (ulong)((param_2 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar4));
    lVar6 = (lVar1 + uVar7) - ((long)*(int *)(lVar6 + 0x34 + lVar4) & *(ulong *)(lVar1 + 8 + uVar7))
    ;
  }
  puVar5 = (undefined4 *)FUN_0082b940(param_1,0x2d,4);
  *puVar5 = *param_3;
  uVar2 = *(undefined8 *)(param_3 + 0x1e);
  *(undefined8 *)(&DAT_000013e0 + param_1) = *(undefined8 *)(param_3 + 0x20);
  *(undefined8 *)(&DAT_000013d8 + param_1) = uVar2;
  FUN_0082b830(param_1,lVar6,param_4,1);
  FUN_0082ba20(param_1,0x2d,4);
  *(undefined4 *)(&DAT_000013d8 + param_1) = 0;
  *(undefined8 *)(&DAT_000013e0 + param_1) = 0;
  *(undefined4 *)(*(long *)(param_1 + 0x1010) + 0x70) = *(undefined4 *)(param_4 + 4);
  lVar6 = FUN_0082cb90(0);
  if (lVar6 != 0) {
    cVar3 = FUN_00820480(param_1,lVar6,param_4,*(undefined8 *)(param_1 + 0x15c0));
    if (cVar3 != '\0') {
      *(byte *)(param_1 + 0x15ac) = *(byte *)(param_1 + 0x15ac) | 1;
    }
  }
  return;
}

