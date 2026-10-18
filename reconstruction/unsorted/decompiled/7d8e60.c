
void FUN_007d8e60(long param_1,ulong param_2,int param_3,uint param_4,undefined8 param_5,
                 undefined8 *param_6)

{
  short sVar1;
  long lVar2;
  ulong uVar3;
  short *psVar4;
  uint uVar5;
  uint uVar6;
  long lVar7;
  long lVar8;
  ulong uVar9;
  uint *puVar10;
  undefined4 *puVar11;
  undefined4 uVar12;
  long lVar13;
  undefined4 *puVar14;
  undefined4 *puVar15;
  byte bVar16;
  long local_50;
  uint local_48;
  uint local_44;
  long local_38;
  
  bVar16 = 0;
  local_38 = *DAT_01a1f100;
  if (((char)param_3 == '\0') && ((param_4 & 0x1e01) == 1)) {
    puVar15 = (undefined4 *)0x0;
    if ((param_4 & 0x1e) == 0) goto LAB_007d90ea;
    puVar10 = (uint *)(param_1 + 0x98);
    uVar5 = param_4 & 0x1e;
    do {
      uVar6 = uVar5 >> 1;
      if (uVar5 >> 1 == 0) goto LAB_007d90ea;
      puVar10 = puVar10 + 1;
      uVar5 = uVar6;
    } while ((uVar6 & 1) == 0);
    uVar9 = (ulong)((*puVar10 & 0x1fff) * DAT_026df1e0);
    uVar5 = (int)*(uint *)(DAT_026df1d8 + uVar9) >> 0xd;
    uVar12 = 0;
    lVar2 = *DAT_01a238a0;
    lVar7 = (ulong)((uVar5 >> 0x12 | 0x3ff) & uVar5) * 0x40;
    lVar13 = *(long *)(lVar2 + 0x10 + lVar7);
    uVar3 = (ulong)((*(uint *)(DAT_026df1d8 + uVar9) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar7));
    lVar2 = (lVar13 + uVar3) -
            ((long)*(int *)(lVar2 + 0x34 + lVar7) & *(ulong *)(lVar13 + 8 + uVar3));
    psVar4 = (short *)(lVar2 + 0x36 + (param_2 & 0xffffffff) * 2);
  }
  else {
    uVar5 = param_4 & 0x1e0;
    puVar15 = (undefined4 *)0x0;
    if (uVar5 == 0) goto LAB_007d90ea;
    param_3 = param_3 - (uint)((param_4 & 0x1e01) == 1);
    if (param_3 < 0) goto LAB_007d90ea;
    lVar2 = 0;
    param_3 = param_3 - (uVar5 >> 5 & 1);
    if (-1 < param_3) {
      uVar5 = uVar5 >> 5;
      do {
        lVar2 = lVar2 + 1;
        uVar5 = (int)uVar5 >> 1;
        param_3 = param_3 - (uVar5 & 1);
      } while (-1 < param_3);
    }
    uVar9 = (ulong)((*(uint *)(param_1 + 0x9c + lVar2 * 4) & 0x1fff) * DAT_026df1e0);
    uVar5 = (int)*(uint *)(DAT_026df1d8 + uVar9) >> 0xd;
    uVar12 = 1;
    lVar2 = *DAT_01a238a0;
    lVar7 = (ulong)((uVar5 >> 0x12 | 0x3ff) & uVar5) * 0x40;
    lVar13 = *(long *)(lVar2 + 0x10 + lVar7);
    uVar3 = (ulong)((*(uint *)(DAT_026df1d8 + uVar9) & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar7));
    lVar2 = (lVar13 + uVar3) -
            ((long)*(int *)(lVar2 + 0x34 + lVar7) & *(ulong *)(lVar13 + 8 + uVar3));
    psVar4 = (short *)(lVar2 + 0x10 + (param_2 & 0xffffffff) * 2);
  }
  lVar13 = DAT_026df1d8 + uVar9;
  sVar1 = *psVar4;
  puVar15 = (undefined4 *)0x0;
  if ((long)sVar1 != -1) {
    FUN_00076040(&local_50,param_5,0x88,0xffff,0,0,0);
    puVar15 = (undefined4 *)0x0;
    if (((ulong)local_44 + 0x88 <= (ulong)local_48) &&
       (puVar14 = (undefined4 *)(local_50 + (ulong)local_44), puVar14 != (undefined4 *)0x0)) {
      *puVar14 = *(undefined4 *)(lVar13 + 8);
      puVar14[1] = uVar12;
      lVar7 = 0;
      if (*(long *)(lVar2 + 0x68) != 0) {
        lVar7 = *(long *)(lVar2 + 0x68) + lVar2 + 0x78;
      }
      puVar15 = (undefined4 *)(lVar7 + (long)sVar1 * 4);
      puVar11 = puVar14 + 2;
      for (lVar8 = 0x1b; lVar8 != 0; lVar8 = lVar8 + -1) {
        *puVar11 = *puVar15;
        puVar15 = puVar15 + (ulong)bVar16 * -2 + 1;
        puVar11 = puVar11 + (ulong)bVar16 * -2 + 1;
      }
      puVar14[0x1d] = *(undefined4 *)(lVar2 + 0x70);
      uVar3 = (ulong)((*(uint *)(lVar13 + 4) & 0x1fff) * DAT_02689800);
      lVar2 = (DAT_026897f8 + uVar3) - ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar3));
      FUN_00802e50(lVar2 + 0x1f8,lVar2,lVar2);
      FUN_0081f460(puVar14 + 0x1e,param_5,lVar2 + 0x1f8);
      puVar15 = puVar14;
    }
  }
LAB_007d90ea:
  *param_6 = puVar15;
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

