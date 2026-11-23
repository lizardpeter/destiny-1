
void FUN_00409430(long param_1)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  long lVar4;
  long lVar5;
  ulong uVar6;
  ulong uVar7;
  long lVar8;
  
  uVar2 = FUN_00108cb0();
  lVar4 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
  lVar5 = *DAT_01a238a0;
  lVar8 = *(long *)(lVar5 + 0x10 + lVar4);
  iVar3 = *(int *)(lVar5 + 0x34 + lVar4);
  uVar6 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
  uVar7 = *(ulong *)(lVar8 + 8 + uVar6);
  *(undefined8 *)(param_1 + 0x210) = 0;
  *(undefined8 *)(param_1 + 0x208) = 0;
  *(uint *)(param_1 + 0x208) = uVar2;
  *(ulong *)(param_1 + 0x210) = (param_1 + 600 + ((long)iVar3 & uVar7)) - (lVar8 + uVar6);
  uVar2 = FUN_00108cb0(param_1);
  lVar5 = *DAT_01a238a0;
  lVar4 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
  lVar8 = *(long *)(lVar5 + 0x10 + lVar4);
  iVar3 = *(int *)(lVar5 + 0x34 + lVar4);
  uVar6 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
  uVar7 = *(ulong *)(lVar8 + 8 + uVar6);
  *(undefined8 *)(param_1 + 800) = 0;
  *(undefined8 *)(param_1 + 0x318) = 0;
  *(uint *)(param_1 + 0x318) = uVar2;
  *(ulong *)(param_1 + 800) = (param_1 + 0x288 + ((long)iVar3 & uVar7)) - (lVar8 + uVar6);
  cVar1 = FUN_001293b0(param_1);
  if (cVar1 != '\0') {
    iVar3 = FUN_00108470(param_1);
    if (iVar3 == 0) {
      uVar2 = FUN_00108cb0(param_1);
      lVar4 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
      lVar5 = *DAT_01a238a0;
      lVar8 = *(long *)(lVar5 + 0x10 + lVar4);
      iVar3 = *(int *)(lVar5 + 0x34 + lVar4);
      uVar6 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
      uVar7 = *(ulong *)(lVar8 + 8 + uVar6);
      *(undefined8 *)(param_1 + 0x200) = 0;
      *(undefined8 *)(param_1 + 0x1f8) = 0;
      *(uint *)(param_1 + 0x1f8) = uVar2;
      *(ulong *)(param_1 + 0x200) = (param_1 + 0x290 + ((long)iVar3 & uVar7)) - (lVar8 + uVar6);
      uVar2 = FUN_00108cb0(param_1);
      lVar5 = *DAT_01a238a0;
      lVar4 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
      lVar8 = *(long *)(lVar5 + 0x10 + lVar4);
      uVar7 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
      lVar5 = param_1 + 0x2a0 +
              ((long)*(int *)(lVar5 + 0x34 + lVar4) & *(ulong *)(lVar8 + 8 + uVar7));
      goto LAB_004096d7;
    }
  }
  uVar2 = FUN_00108cb0(param_1);
  lVar4 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
  lVar5 = *DAT_01a238a0;
  lVar8 = *(long *)(lVar5 + 0x10 + lVar4);
  iVar3 = *(int *)(lVar5 + 0x34 + lVar4);
  uVar6 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
  uVar7 = *(ulong *)(lVar8 + 8 + uVar6);
  *(undefined8 *)(param_1 + 0x200) = 0;
  *(undefined8 *)(param_1 + 0x1f8) = 0;
  *(uint *)(param_1 + 0x1f8) = uVar2;
  *(ulong *)(param_1 + 0x200) = (param_1 + 0x218 + ((long)iVar3 & uVar7)) - (lVar8 + uVar6);
  uVar2 = FUN_00108cb0(param_1);
  lVar5 = *DAT_01a238a0;
  lVar4 = (ulong)(((uint)((int)uVar2 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar2 >> 0xd) * 0x40;
  lVar8 = *(long *)(lVar5 + 0x10 + lVar4);
  uVar7 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar4));
  lVar5 = param_1 + 0x228 + ((long)*(int *)(lVar5 + 0x34 + lVar4) & *(ulong *)(lVar8 + 8 + uVar7));
LAB_004096d7:
  *(undefined8 *)(param_1 + 0x310) = 0;
  *(undefined8 *)(param_1 + 0x308) = 0;
  *(uint *)(param_1 + 0x308) = uVar2;
  *(ulong *)(param_1 + 0x310) = lVar5 - (lVar8 + uVar7);
  return;
}

