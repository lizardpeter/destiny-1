
void FUN_002c8340(uint param_1,undefined8 param_2,int param_3,undefined8 param_4,undefined8 param_5,
                 undefined8 param_6,int param_7)

{
  long lVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  undefined8 local_38;
  undefined8 local_30;
  undefined8 local_28;
  int local_20;
  int local_1c;
  undefined8 local_18;
  long local_10;
  
  local_10 = *DAT_01a1f100;
  lVar4 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
  lVar3 = 0;
  local_1c = param_3 + 1;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar4);
  uVar5 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar4));
  lVar2 = (lVar2 + uVar5) - ((long)*(int *)(lVar1 + 0x34 + lVar4) & *(ulong *)(lVar2 + 8 + uVar5));
  lVar1 = *(long *)(lVar2 + 0x48);
  if (lVar1 != 0) {
    lVar3 = lVar2 + 0x48 + lVar1;
  }
  local_38 = param_2;
  local_30 = param_4;
  local_28 = param_5;
  local_20 = param_3;
  local_18 = param_6;
  if (param_7 == 1) {
    FUN_0101eb30();
  }
  else {
    FUN_0101f1d0(lVar3,&local_38);
  }
  if (*DAT_01a1f100 == local_10) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

