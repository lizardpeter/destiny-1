
code * FUN_004e3d50(int *param_1)

{
  int iVar1;
  long lVar2;
  long lVar3;
  long lVar4;
  uint uVar5;
  code *pcVar6;
  ulong uVar7;
  code *pcVar8;
  long lVar9;
  int iVar10;
  long local_70;
  long local_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined4 local_50;
  undefined1 local_48;
  int local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar1 = *(int *)(thunk_FUN_007eb6f0 + DAT_026afef0);
  iVar10 = -1;
  pcVar6 = FUN_00001320;
  do {
    lVar4 = DAT_026afef0;
    iVar10 = iVar10 + 1;
    pcVar8 = (code *)0x0;
    if (iVar1 <= iVar10) goto LAB_004e3e87;
    pcVar8 = pcVar6 + 0x38;
    local_48 = 0;
    uVar5 = (int)*(uint *)(pcVar6 + DAT_026afef0 + 0x50) >> 0xd;
    lVar2 = *DAT_01a238a0;
    lVar9 = (ulong)((uVar5 >> 0x12 | 0x3ff) & uVar5) * 0x40;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar9);
    uVar7 = (ulong)((*(uint *)(pcVar6 + DAT_026afef0 + 0x50) & 0x1fff) *
                   *(int *)(lVar2 + 0x30 + lVar9));
    local_70 = (lVar3 + uVar7) -
               ((long)*(int *)(lVar2 + 0x34 + lVar9) & *(ulong *)(lVar3 + 8 + uVar7));
    uVar5 = (int)*(uint *)(pcVar6 + DAT_026afef0 + 0x58) >> 0xd;
    lVar9 = (ulong)((uVar5 >> 0x12 | 0x3ff) & uVar5) * 0x40;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar9);
    uVar7 = (ulong)((*(uint *)(pcVar6 + DAT_026afef0 + 0x58) & 0x1fff) *
                   *(int *)(lVar2 + 0x30 + lVar9));
    local_68 = ((lVar3 + uVar7) -
               ((long)*(int *)(lVar2 + 0x34 + lVar9) & *(ulong *)(lVar3 + 8 + uVar7))) +
               *(long *)(pcVar6 + DAT_026afef0 + 0x60);
    local_50 = *(undefined4 *)(pcVar6 + DAT_026afef0 + 0x68);
    local_60 = *(undefined8 *)(pcVar6 + DAT_026afef0 + 0x58);
    local_58 = *(undefined8 *)(pcVar6 + DAT_026afef0 + 0x60);
    FUN_00354400(local_40,&local_70);
    pcVar6 = pcVar8;
  } while (*param_1 != local_40[0]);
  pcVar8 = pcVar8 + lVar4;
LAB_004e3e87:
  if (*DAT_01a1f100 == local_38) {
    return pcVar8;
  }
  pcVar6 = (code *)thunk_FUN_012aa7f6();
  return pcVar6;
}

