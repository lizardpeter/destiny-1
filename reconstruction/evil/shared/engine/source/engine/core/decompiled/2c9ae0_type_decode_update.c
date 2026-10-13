
bool FUN_002c9ae0(undefined8 param_1,undefined8 param_2,int *param_3,uint param_4,undefined4 param_5
                 )

{
  int iVar1;
  int iVar2;
  long lVar3;
  char cVar4;
  undefined1 uVar5;
  int iVar6;
  long lVar7;
  ulong uVar8;
  long lVar9;
  ulong uVar10;
  undefined4 *local_148;
  uint local_140;
  undefined4 local_13c;
  undefined4 local_138;
  undefined4 local_134;
  undefined4 auStack_130 [62];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar7 = (ulong)(((uint)((int)param_4 >> 0xd) >> 0x12 | 0x3ff) & (int)param_4 >> 0xd) * 0x40;
  lVar9 = *DAT_01a238a0;
  local_148 = &local_13c;
  lVar3 = *(long *)(lVar9 + 0x10 + lVar7);
  uVar8 = (ulong)(*(int *)(lVar9 + 0x30 + lVar7) * (param_4 & 0x1fff));
  lVar9 = (lVar3 + uVar8) - ((long)*(int *)(lVar9 + 0x34 + lVar7) & *(ulong *)(lVar3 + 8 + uVar8));
  iVar1 = *param_3;
  iVar2 = *(int *)(lVar9 + 0x54 + *(long *)(lVar9 + 0x48));
  iVar6 = *(int *)(lVar9 + 0x5c + *(long *)(lVar9 + 0x48)) + 1;
  local_140 = iVar6 * 0x4000 | 0xf0003ffe;
  uVar8 = (ulong)((iVar6 * 0x40000 >> 0x12) + 0x1f >> 5);
  if (uVar8 * 4 < 0x21) {
    uVar10 = uVar8 & 0x3fffffffffffffff;
    if ((((uVar10 != 0) && (local_13c = 0, uVar10 != 1)) && (local_138 = 0, uVar10 != 2)) &&
       (local_134 = 0, uVar10 != 3)) {
      for (lVar9 = 0; auStack_130[lVar9] = 0, (uVar8 & 0x3fffffffffffffff) - 4 != lVar9;
          lVar9 = lVar9 + 1) {
      }
    }
  }
  else {
    thunk_FUN_012aa986(local_148,0);
  }
  cVar4 = FUN_00073430(param_1);
  if (cVar4 != '\0') {
    FUN_002c8340(param_4,param_1,0,param_2,param_2,&local_148,param_5);
  }
  FUN_002c7230(&local_148);
  if (iVar2 <= iVar1) {
    lVar9 = *DAT_01a238a0;
    uVar8 = (ulong)((param_4 & 0x1fff) * *(int *)(lVar9 + lVar7 + 0x30));
    lVar3 = *(long *)(lVar9 + lVar7 + 0x10);
    lVar9 = (lVar3 + uVar8) - ((long)*(int *)(lVar9 + lVar7 + 0x34) & *(ulong *)(lVar3 + 8 + uVar8))
    ;
    *param_3 = *(int *)(lVar9 + 0x54 + *(long *)(lVar9 + 0x48));
  }
  if (*DAT_01a1f100 == local_38) {
    return iVar2 <= iVar1;
  }
  uVar5 = thunk_FUN_012aa7f6();
  return (bool)uVar5;
}

