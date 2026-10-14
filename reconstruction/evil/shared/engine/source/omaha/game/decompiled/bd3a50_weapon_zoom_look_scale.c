
void FUN_00bd3a50(undefined8 param_1,float *param_2,float *param_3)

{
  long lVar1;
  float fVar2;
  uint uVar3;
  int iVar4;
  ulong uVar5;
  long lVar6;
  long lVar7;
  
  *param_2 = 1.0;
  *param_3 = 1.0;
  uVar3 = FUN_00bd3820();
  uVar5 = (ulong)((uVar3 & 0x1fff) * DAT_02689800);
  uVar3 = *(uint *)(((uVar5 + DAT_026897f8) -
                    (*(ulong *)(DAT_026897f8 + 8 + uVar5) & (long)DAT_02689818)) + 0x68);
  if (uVar3 != 0xffffffff) {
    uVar5 = (ulong)((uVar3 & 0x1fff) * DAT_02689800);
    iVar4 = FUN_007397f0((DAT_026897f8 + uVar5) -
                         (*(ulong *)(DAT_026897f8 + 8 + uVar5) & (long)DAT_02689818));
    if (iVar4 != -1) {
      iVar4 = FUN_006ed9f0(iVar4);
      if (iVar4 != -1) {
        uVar3 = FUN_006fc510(iVar4);
        fVar2 = DAT_01699a3c;
        if (uVar3 != 0xffffffff) {
          lVar6 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
          lVar7 = *DAT_01a238a0;
          lVar1 = *(long *)(lVar7 + 0x10 + lVar6);
          uVar5 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar6));
          lVar7 = (lVar1 + uVar5) -
                  ((long)*(int *)(lVar7 + 0x34 + lVar6) & *(ulong *)(lVar1 + 8 + uVar5));
          *param_3 = DAT_01699a3c - *(float *)(lVar7 + 0x184);
          *param_2 = fVar2 - *(float *)(lVar7 + 0x1b4);
        }
      }
    }
  }
  return;
}

