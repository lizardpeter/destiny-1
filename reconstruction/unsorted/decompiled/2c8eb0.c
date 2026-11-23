
/* WARNING: Removing unreachable block (ram,0x002c901b) */
/* WARNING: Removing unreachable block (ram,0x002c9031) */
/* WARNING: Removing unreachable block (ram,0x002c9040) */

void FUN_002c8eb0(uint param_1,undefined8 param_2,undefined8 param_3,int param_4)

{
  long lVar1;
  ulong uVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  ulong uVar6;
  int iVar7;
  undefined4 **local_548;
  undefined4 local_540;
  undefined4 local_53c;
  undefined8 local_538;
  undefined8 local_530;
  undefined4 *local_528;
  uint local_520;
  undefined4 local_51c;
  undefined4 local_518;
  undefined4 local_514;
  undefined4 auStack_510 [310];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar1 = (ulong)(((uint)((int)param_1 >> 0xd) >> 0x12 | 0x3ff) & (int)param_1 >> 0xd) * 0x40;
  lVar5 = *DAT_01a238a0;
  local_528 = &local_51c;
  lVar3 = *(long *)(lVar5 + 0x10 + lVar1);
  uVar2 = (ulong)(*(int *)(lVar5 + 0x30 + lVar1) * (param_1 & 0x1fff));
  lVar5 = (lVar3 + uVar2) - ((long)*(int *)(lVar5 + 0x34 + lVar1) & *(ulong *)(lVar3 + 8 + uVar2));
  iVar7 = *(int *)(lVar5 + 0x5c + *(long *)(lVar5 + 0x48)) + 1;
  local_520 = iVar7 * 0x4000 | 0xf0003ffe;
  uVar2 = (ulong)((iVar7 * 0x40000 >> 0x12) + 0x1f >> 5);
  if (uVar2 * 4 < 0x21) {
    uVar6 = uVar2 & 0x3fffffffffffffff;
    if ((((uVar6 != 0) && (local_51c = 0, uVar6 != 1)) && (local_518 = 0, uVar6 != 2)) &&
       (local_514 = 0, uVar6 != 3)) {
      for (lVar5 = 0; auStack_510[lVar5] = 0, (uVar2 & 0x3fffffffffffffff) - 4 != lVar5;
          lVar5 = lVar5 + 1) {
      }
    }
  }
  else {
    thunk_FUN_012aa986(local_528,0);
  }
  FUN_002c7690(&local_528);
  local_540 = 0;
  local_53c = 1;
  local_548 = &local_528;
  lVar4 = 0;
  lVar5 = *DAT_01a238a0;
  uVar2 = (ulong)((param_1 & 0x1fff) * *(int *)(lVar5 + lVar1 + 0x30));
  lVar3 = *(long *)(lVar5 + lVar1 + 0x10);
  lVar3 = (lVar3 + uVar2) - ((long)*(int *)(lVar5 + lVar1 + 0x34) & *(ulong *)(lVar3 + 8 + uVar2));
  lVar5 = *(long *)(lVar3 + 0x48);
  if (lVar5 != 0) {
    lVar4 = lVar3 + 0x48 + lVar5;
  }
  local_538 = param_2;
  local_530 = param_3;
  if (param_4 == 1) {
    FUN_0101c220();
  }
  else {
    FUN_0101c940(lVar4,&local_548);
  }
  FUN_002c7230(&local_528);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

