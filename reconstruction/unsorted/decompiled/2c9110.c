
void FUN_002c9110(uint param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,int param_5)

{
  long *plVar1;
  long lVar2;
  ulong uVar3;
  long lVar4;
  long lVar5;
  int iVar6;
  long lVar7;
  ulong uVar8;
  undefined8 local_550;
  undefined8 local_548;
  undefined8 local_540;
  undefined4 local_538;
  undefined4 local_534;
  undefined4 **local_530;
  undefined4 *local_528;
  uint local_520;
  undefined4 local_51c;
  undefined4 local_518;
  undefined4 local_514;
  undefined4 auStack_510 [310];
  long local_38;
  
  plVar1 = DAT_01a238a0;
  local_38 = *DAT_01a1f100;
  lVar2 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
  lVar7 = *DAT_01a238a0;
  local_528 = &local_51c;
  lVar4 = *(long *)(lVar7 + 0x10 + lVar2);
  uVar3 = (ulong)(*(int *)(lVar7 + 0x30 + lVar2) * (param_1 & 0x1fff));
  lVar7 = (lVar4 + uVar3) - ((long)*(int *)(lVar7 + 0x34 + lVar2) & *(ulong *)(lVar4 + 8 + uVar3));
  iVar6 = *(int *)(lVar7 + 0x5c + *(long *)(lVar7 + 0x48)) + 1;
  local_520 = iVar6 * 0x4000 | 0xf0003ffe;
  uVar3 = (ulong)((iVar6 * 0x40000 >> 0x12) + 0x1f >> 5);
  if (uVar3 * 4 < 0x21) {
    uVar8 = uVar3 & 0x3fffffffffffffff;
    if ((((uVar8 != 0) && (local_51c = 0, uVar8 != 1)) && (local_518 = 0, uVar8 != 2)) &&
       (local_514 = 0, uVar8 != 3)) {
      for (lVar7 = 0; auStack_510[lVar7] = 0, (uVar3 & 0x3fffffffffffffff) - 4 != lVar7;
          lVar7 = lVar7 + 1) {
      }
    }
  }
  else {
    thunk_FUN_012aa986(local_528,0);
  }
  local_530 = &local_528;
  local_538 = 0;
  local_534 = 1;
  lVar5 = 0;
  lVar7 = *plVar1;
  uVar3 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar7 + lVar2 + 0x30));
  lVar4 = *(long *)(lVar7 + lVar2 + 0x10);
  lVar4 = (lVar4 + uVar3) - ((long)*(int *)(lVar7 + lVar2 + 0x34) & *(ulong *)(lVar4 + 8 + uVar3));
  lVar7 = *(long *)(lVar4 + 0x48);
  if (lVar7 != 0) {
    lVar5 = lVar4 + 0x48 + lVar7;
  }
  local_550 = param_2;
  local_548 = param_3;
  local_540 = param_4;
  if (param_5 == 1) {
    FUN_0101eb30();
  }
  else {
    FUN_0101f1d0(lVar5,&local_550);
  }
  FUN_002c7230(&local_528);
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

