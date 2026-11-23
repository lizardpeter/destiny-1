
ulong FUN_0100cb80(long *param_1,undefined8 *param_2)

{
  undefined8 *puVar1;
  int iVar2;
  int iVar3;
  long lVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  bool bVar7;
  int *in_RAX;
  ulong uVar8;
  short sVar9;
  int iVar10;
  int iVar11;
  long lVar12;
  int iVar13;
  int in_R11D;
  short sVar14;
  int unaff_R12D;
  
  iVar2 = *(int *)((long)param_1 + 0xc);
  lVar12 = (long)iVar2;
  iVar13 = iVar2;
  if (lVar12 == -1) {
    lVar4 = *param_1;
    iVar13 = -1;
    if (0 < *(int *)(lVar4 + 8)) {
      iVar10 = (int)(short)param_1[1];
      in_RAX = (int *)(lVar4 + 0x10);
      bVar7 = false;
      iVar11 = 0;
      do {
        sVar14 = (short)unaff_R12D;
        if (bVar7) break;
        iVar3 = *in_RAX;
        if ((iVar3 <= iVar10) && (iVar10 < in_RAX[-1] + iVar3)) {
          unaff_R12D = iVar10 - iVar3;
          bVar7 = true;
          in_R11D = iVar11;
        }
        sVar14 = (short)unaff_R12D;
        in_RAX = in_RAX + 5;
        iVar11 = iVar11 + 1;
      } while (iVar11 < *(int *)(lVar4 + 8));
      if (bVar7) {
        in_RAX = (int *)((long)((int)sVar14 + *(int *)(lVar4 + 0x10 + (long)in_R11D * 0x14)) * 0x38)
        ;
        iVar13 = *(int *)(lVar4 + 0x518 + (long)in_RAX);
      }
    }
  }
  uVar8 = (ulong)in_RAX & 0xffffffffffffff00;
  if ((((1 < iVar13 - 0x29U) && (iVar13 != 0x2d)) && (iVar13 != 0x2c)) &&
     ((iVar13 != 0x39 && (iVar13 != 0x3a)))) {
    lVar4 = *param_1;
    sVar14 = (short)param_1[1];
    sVar9 = sVar14;
    if ((iVar2 != -1) && (sVar9 = -1, sVar14 < *(short *)(lVar4 + 0x2bd1e + lVar12 * 4))) {
      sVar9 = *(short *)(lVar4 + 0x2a51c +
                        ((long)*(short *)(lVar4 + 0x2bd1c + lVar12 * 4) + (long)sVar14) * 2);
    }
    param_2[1] = 0;
    *param_2 = 0;
    *(undefined4 *)param_2 = 0xffffffff;
    *(undefined4 *)(param_2 + 2) = 0xffffffff;
    if ((sVar9 != -1) && (*(int *)(lVar4 + 0x520 + (long)sVar9 * 0x38) != -1)) {
      puVar1 = (undefined8 *)(lVar4 + 0x520 + (long)sVar9 * 0x38);
      *(undefined4 *)(param_2 + 2) = *(undefined4 *)(puVar1 + 2);
      uVar5 = *puVar1;
      uVar6 = puVar1[1];
      param_2[1] = uVar6;
      *param_2 = uVar5;
      uVar8 = CONCAT71((int7)((ulong)uVar6 >> 8),1);
    }
  }
  return uVar8;
}

