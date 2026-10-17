
void FUN_00752f10(long param_1,uint param_2)

{
  int *piVar1;
  undefined *puVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  int iVar6;
  uint uVar7;
  long lVar8;
  undefined8 uVar9;
  long lVar10;
  ulong uVar11;
  undefined4 local_140;
  undefined4 local_13c;
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar8 = (long)(int)param_2;
  uVar7 = *(uint *)(param_1 + lVar8 * 0xc);
  piVar1 = (int *)(param_1 + lVar8 * 0xc);
  if (uVar7 < 6) {
    if ((0x36U >> (uVar7 & 0x1f) & 1) != 0) goto LAB_007530b1;
    if (uVar7 == 3) {
      uVar9 = FUN_00346d20();
      thunk_FUN_00348a40(uVar9,*(undefined4 *)(param_1 + 4 + lVar8 * 0xc));
      FUN_007530f0(param_1,param_2);
      if (*piVar1 == 4) goto LAB_007530b1;
    }
  }
  puVar2 = (&PTR_DAT_01944c30)[param_2];
  iVar6 = FUN_000cdb80(puVar2);
  if (iVar6 == -1) {
    *piVar1 = 5;
  }
  else {
    uVar9 = FUN_00346d20();
    FUN_010156f0(local_138,s__global_resource_load_of___s__0164a02f + 1,puVar2);
    uVar7 = FUN_00349c50(uVar9,7,2,0,local_138);
    *(uint *)(param_1 + 4 + lVar8 * 0xc) = uVar7;
    if (uVar7 == 0xffffffff) {
      *piVar1 = 4;
    }
    else {
      lVar10 = (ulong)(((uint)((int)uVar7 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar7 >> 0xd) * 0x40;
      lVar3 = *DAT_01a238a0;
      lVar4 = *(long *)(lVar3 + 0x10 + lVar10);
      iVar6 = *(int *)(lVar3 + 0x34 + lVar10);
      uVar11 = (ulong)((uVar7 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar10));
      uVar5 = *(ulong *)(lVar4 + 8 + uVar11);
      local_13c = FUN_000cdb80(puVar2);
      *(undefined4 *)(param_1 + 8 + lVar8 * 0xc) = local_13c;
      local_140 = 2;
      FUN_003469a0((lVar4 + uVar11) - ((long)iVar6 & uVar5),&local_140);
      FUN_0034a1d0(uVar9,*(undefined4 *)(param_1 + 4 + lVar8 * 0xc));
      *piVar1 = 1;
      *(int *)(param_1 + 0x60) = *(int *)(param_1 + 0x60) + 1;
    }
  }
LAB_007530b1:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

