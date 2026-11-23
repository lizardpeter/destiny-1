
void FUN_007dec20(long param_1,uint param_2,ushort param_3,uint param_4,int param_5)

{
  undefined1 *puVar1;
  uint uVar2;
  int iVar3;
  uint *puVar4;
  long lVar5;
  long lVar6;
  uint uVar7;
  long lVar8;
  ulong uVar9;
  ulong uVar10;
  uint uVar11;
  int local_240;
  undefined1 local_238 [512];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((param_2 != 0xffffffff) &&
     (((uVar10 = (ulong)param_3, *(uint *)(param_1 + 0x1d78 + uVar10 * 4) != param_2 ||
       (*(uint *)(&DAT_00001df8 + uVar10 * 4 + param_1) != param_4)) &&
      (puVar4 = *(uint **)(param_1 + 0x1d60), puVar4 != (uint *)0x0)))) {
    uVar2 = puVar4[uVar10 + 1];
    lVar8 = (ulong)(((uint)((int)param_2 >> 0xd) >> 0x12 | 0x3ff) & (int)param_2 >> 0xd) * 0x40;
    lVar5 = *DAT_01a238a0;
    uVar9 = (ulong)((param_2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar8));
    if (uVar2 != 0) {
      lVar6 = *(long *)(lVar5 + 0x10 + lVar8);
      lVar8 = (lVar6 + uVar9) -
              ((long)*(int *)(lVar5 + 0x34 + lVar8) & *(ulong *)(lVar6 + 8 + uVar9));
      lVar5 = *(long *)(lVar8 + 0x28);
      iVar3 = *(int *)(lVar8 + 0x30);
      local_240 = iVar3;
      if ((param_4 != 0) && (local_240 = param_5, param_5 == 0)) {
        local_240 = iVar3 - param_4 / uVar2;
      }
      uVar7 = *puVar4;
      if (uVar7 != 0) {
        uVar11 = 0;
        do {
          uVar9 = (ulong)uVar11;
          if (*(byte *)((long)puVar4 + uVar9 * 8 + 0x19) == param_3) {
            puVar1 = local_238 + uVar9 * 0x10;
            FUN_00f7cf90(puVar1,(ulong)((byte)puVar4[uVar9 * 2 + 6] + param_4) + lVar5,
                         puVar4[uVar9 * 2 + 5],uVar2,local_240);
            FUN_00f7d010(puVar1,0x10);
            FUN_00f8b600(*(long *)(param_1 + 0x50) + 0xc0,2,uVar9,1,puVar1);
            uVar7 = *puVar4;
          }
          uVar11 = uVar11 + 1;
        } while (uVar11 < uVar7);
      }
      *(uint *)(param_1 + 0x1d78 + uVar10 * 4) = param_2;
      *(uint *)(&DAT_00001df8 + uVar10 * 4 + param_1) = param_4;
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

