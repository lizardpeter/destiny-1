
void FUN_002c7fa0(uint param_1,undefined8 param_2,int param_3,undefined8 param_4,undefined8 param_5,
                 int param_6)

{
  long lVar1;
  long *plVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  ulong uVar6;
  undefined8 local_40;
  int local_38;
  int local_34;
  undefined8 local_30;
  undefined8 local_28;
  long local_20;
  
  plVar2 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_34 = param_3 + 1;
  lVar5 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
  lVar4 = 0;
  lVar1 = *DAT_01a238a0;
  lVar3 = *(long *)(lVar1 + 0x10 + lVar5);
  uVar6 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar5));
  lVar3 = (lVar3 + uVar6) - ((long)*(int *)(lVar1 + 0x34 + lVar5) & *(ulong *)(lVar3 + 8 + uVar6));
  lVar1 = *(long *)(lVar3 + 0x48);
  if (lVar1 != 0) {
    lVar4 = lVar3 + 0x48 + lVar1;
  }
  local_40 = param_2;
  local_38 = param_3;
  local_30 = param_4;
  local_28 = param_5;
  if (param_6 == 1) {
    FUN_0101c220();
  }
  else {
    FUN_0101c940(lVar4,&local_40);
  }
  if (*plVar2 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

