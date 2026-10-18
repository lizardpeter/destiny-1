
void FUN_007d3560(ulong param_1,ulong param_2)

{
  int iVar1;
  int iVar2;
  long lVar3;
  ulong uVar4;
  ulong uVar5;
  undefined4 uVar6;
  uint uVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  long lVar11;
  undefined8 uVar12;
  uint uVar13;
  long lVar14;
  ulong uVar15;
  ulong uVar16;
  ulong local_50;
  ulong local_48;
  uint local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar8 = (*DAT_0254ee98)(param_1,param_2,1,1);
  uVar13 = (int)(uint)param_2 >> 0xd;
  lVar9 = (ulong)((uVar13 >> 0x12 | 0x3ff) & uVar13) * 0x40;
  lVar10 = *DAT_01a238a0;
  lVar3 = *(long *)(lVar10 + 0x10 + lVar9);
  iVar1 = *(int *)(lVar10 + 0x34 + lVar9);
  uVar15 = (ulong)(((uint)param_2 & 0x1fff) * *(int *)(lVar10 + 0x30 + lVar9));
  uVar13 = (int)(uint)param_1 >> 0xd;
  uVar4 = *(ulong *)(lVar3 + 8 + uVar15);
  uVar6 = FUN_000de720(param_2 & 0xffffffff);
  uVar7 = FUN_000de660(param_2 & 0xffffffff);
  lVar10 = FUN_000de6f0(uVar6);
  lVar11 = FUN_000de6f0(uVar7);
  *(byte *)(lVar10 + 0x16) = *(byte *)(lVar10 + 0x16) | 1;
  lVar14 = (ulong)((uVar13 >> 0x12 | 0x3ff) & uVar13) * 0x40;
  *(byte *)(lVar11 + 0x16) = *(byte *)(lVar11 + 0x16) | 1;
  lVar10 = *DAT_01a238a0;
  uVar16 = (ulong)(((uint)param_1 & 0x1fff) * *(int *)(lVar10 + 0x30 + lVar14));
  lVar9 = *(long *)(lVar10 + 0x10 + lVar14);
  iVar2 = *(int *)(lVar10 + 0x34 + lVar14);
  uVar5 = *(ulong *)(lVar9 + 8 + uVar16);
  uVar12 = (*DAT_0254ee98)(param_1 & 0xffffffff,param_2 & 0xffffffff,2,1);
  lVar10 = FUN_000deb60(lVar11,uVar7 & 0xffff,uVar7 >> 0x10 & 0xff,local_40);
  *(byte *)(lVar10 + 0x16) = *(byte *)(lVar10 + 0x16) | 1;
  FUN_000de1d0(param_1 & 0xffffffff);
  local_48 = (ulong)uVar7;
  local_50 = (ulong)local_40[0];
  FUN_007da960(lVar3 + uVar15 + (lVar8 - ((long)iVar1 & uVar4)),
               (lVar9 + uVar16) - ((long)iVar2 & uVar5),uVar12,FUN_007d3720,&local_48,&local_50,0);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

