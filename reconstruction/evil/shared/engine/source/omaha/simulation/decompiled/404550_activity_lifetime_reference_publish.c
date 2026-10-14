
void FUN_00404550(long param_1,uint *param_2)

{
  int iVar1;
  long lVar2;
  long lVar3;
  ulong uVar4;
  uint uVar5;
  long lVar6;
  ulong uVar7;
  
  uVar5 = FUN_00108cb0();
  lVar2 = *DAT_01a238a0;
  lVar6 = (ulong)(((uint)((int)uVar5 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar5 >> 0xd) * 0x40;
  uVar7 = (ulong)((uVar5 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar6));
  lVar3 = *(long *)(lVar2 + 0x10 + lVar6);
  iVar1 = *(int *)(lVar2 + 0x34 + lVar6);
  uVar4 = *(ulong *)(lVar3 + 8 + uVar7);
  param_2[4] = *(uint *)PTR_DAT_019b2b20;
  param_2[2] = 0;
  param_2[3] = 0;
  param_2[0] = 0;
  param_2[1] = 0;
  *param_2 = uVar5;
  *(ulong *)(param_2 + 2) = (param_1 + 0x1ad + ((long)iVar1 & uVar4)) - (lVar3 + uVar7);
  return;
}

