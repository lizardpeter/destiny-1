
undefined8 FUN_007d2e80(undefined4 param_1,uint param_2,undefined8 param_3)

{
  long lVar1;
  long lVar2;
  undefined8 uVar3;
  long lVar4;
  ulong uVar5;
  
  uVar3 = 0;
  switch(param_1) {
  case 1:
  case 2:
  case 3:
    uVar3 = FUN_007d4d40(param_2,param_3);
    return uVar3;
  case 4:
    uVar3 = FUN_007d4c30(param_2,param_3);
    return uVar3;
  case 6:
    uVar3 = FUN_007d4cb0(param_2,param_3);
    return uVar3;
  case 7:
    uVar3 = FUN_007d4da0(param_2,param_3);
    return uVar3;
  case 8:
    uVar3 = FUN_007d4b90(param_2,param_3);
    return uVar3;
  case 9:
    uVar3 = FUN_007d48c0(param_2,param_3);
    return uVar3;
  case 10:
    uVar3 = FUN_007d4ab0(param_2,param_3);
    return uVar3;
  case 0xb:
    uVar3 = FUN_007d4970(param_2,param_3);
    return uVar3;
  case 0xc:
    uVar3 = FUN_007d49f0(param_2,param_3);
    return uVar3;
  case 0xd:
    uVar3 = FUN_007d49f0(param_2,param_3);
    return uVar3;
  case 0xe:
    uVar3 = FUN_007d4970(param_2,param_3);
    return uVar3;
  case 0x10:
    uVar3 = FUN_00001f70(param_2,param_3);
    return uVar3;
  case 0x12:
    lVar4 = (ulong)(((uint)((int)param_2 >> 0xd) >> 0x12 | 0x3ff) & (int)param_2 >> 0xd) * 0x40;
    lVar1 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar1 + 0x10 + lVar4);
    uVar5 = (ulong)((param_2 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar4));
    FUN_00073d50((lVar2 + uVar5) -
                 ((long)*(int *)(lVar1 + 0x34 + lVar4) & *(ulong *)(lVar2 + 8 + uVar5)),param_3);
    uVar3 = 1;
  }
  return uVar3;
}

