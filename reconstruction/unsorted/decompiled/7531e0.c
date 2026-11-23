
void FUN_007531e0(long param_1,uint param_2)

{
  int *piVar1;
  undefined *puVar2;
  long lVar3;
  long lVar4;
  int iVar5;
  uint uVar6;
  long lVar7;
  undefined8 uVar8;
  ulong uVar9;
  long lVar10;
  undefined4 local_140;
  undefined4 local_13c;
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar7 = (long)(int)param_2;
  iVar5 = *(int *)(param_1 + lVar7 * 0xc);
  if ((2 < iVar5 - 3U) && (iVar5 != 0)) {
    piVar1 = (int *)(param_1 + lVar7 * 0xc);
    if (iVar5 == 1) {
      uVar8 = FUN_00346d20();
      thunk_FUN_00348a40(uVar8,*(undefined4 *)(param_1 + 4 + lVar7 * 0xc));
      FUN_007530f0(param_1,param_2);
      if (*piVar1 == 4) goto LAB_00753383;
    }
    puVar2 = (&PTR_DAT_01944c30)[param_2];
    iVar5 = FUN_000cdb80(puVar2);
    if (iVar5 == -1) {
      *piVar1 = 5;
    }
    else {
      uVar8 = FUN_00346d20();
      if (param_2 == 7) {
        FUN_00542810();
      }
      else if (param_2 == 6) {
        thunk_FUN_00546940();
      }
      FUN_010156f0(local_138,s_global_resource_unload_of___s__0164a04d,puVar2);
      uVar6 = FUN_00349c50(uVar8,7,2,0,local_138);
      *(uint *)(param_1 + 4 + lVar7 * 0xc) = uVar6;
      if (uVar6 == 0xffffffff) {
        *piVar1 = 4;
      }
      else {
        lVar10 = (ulong)(((uint)((int)uVar6 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar6 >> 0xd) * 0x40;
        lVar3 = *DAT_01a238a0;
        lVar4 = *(long *)(lVar3 + 0x10 + lVar10);
        uVar9 = (ulong)((uVar6 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar10));
        local_140 = 2;
        local_13c = *(undefined4 *)(param_1 + 8 + lVar7 * 0xc);
        FUN_00346a50((lVar4 + uVar9) -
                     ((long)*(int *)(lVar3 + 0x34 + lVar10) & *(ulong *)(lVar4 + 8 + uVar9)),
                     &local_140);
        FUN_0034a1d0(uVar8,*(undefined4 *)(param_1 + 4 + lVar7 * 0xc));
        *piVar1 = 3;
        *(int *)(param_1 + 0x60) = *(int *)(param_1 + 0x60) + 1;
      }
    }
  }
LAB_00753383:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

