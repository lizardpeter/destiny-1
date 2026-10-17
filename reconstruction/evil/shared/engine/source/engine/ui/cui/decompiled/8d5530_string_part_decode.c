
void FUN_008d5530(long param_1,short *param_2,long param_3)

{
  short *psVar1;
  byte bVar2;
  long lVar3;
  ushort uVar4;
  byte *pbVar5;
  long lVar6;
  ushort uVar7;
  byte *pbVar8;
  bool bVar9;
  
  pbVar5 = (byte *)0x0;
  if (*(long *)(param_1 + 8) != 0) {
    pbVar5 = (byte *)(*(long *)(param_1 + 8) + param_1 + 8);
  }
  if ((*(byte *)(param_1 + 0x1b) & 4) == 0) {
    if (((ulong)*(ushort *)(param_1 + 0x14) != 0) && (param_3 != 1)) {
      lVar6 = (ulong)*(ushort *)(param_1 + 0x14) * 2;
      lVar3 = param_3 * 2 + -4;
      do {
        lVar6 = lVar6 + -2;
        *param_2 = *(short *)(param_1 + 0x18) + *(short *)pbVar5;
        param_2 = param_2 + 1;
        if (lVar6 == 0) break;
        pbVar5 = pbVar5 + 2;
        bVar9 = lVar3 != 0;
        lVar3 = lVar3 + -2;
      } while (bVar9);
    }
  }
  else if (((ulong)*(ushort *)(param_1 + 0x14) != 0) && (param_3 != 1)) {
    psVar1 = param_2 + param_3 + -1;
    pbVar8 = pbVar5 + *(ushort *)(param_1 + 0x14);
    do {
      bVar2 = *pbVar5;
      uVar7 = (ushort)bVar2;
      lVar6 = 1;
      if ((bVar2 & 0x80) != 0) {
        uVar7 = (ushort)bVar2;
        if ((bVar2 & 0xe0) == 0xc0) {
          uVar7 = bVar2 & 0x1f;
          lVar6 = 2;
        }
        else if ((uVar7 & 0xf0) == 0xe0) {
          uVar7 = bVar2 & 0xf;
          lVar6 = 3;
        }
        else {
          uVar4 = uVar7 & 0xf8;
          uVar7 = uVar7 & 7;
          if (uVar4 != 0xf0) {
            uVar7 = 0;
          }
          lVar6 = 4;
          if (uVar4 != 0xf0) {
            lVar6 = (ulong)(uVar4 == 0xf0) << 2;
            goto LAB_008d5620;
          }
        }
        lVar3 = 1;
        do {
          uVar7 = uVar7 << 6 | pbVar5[lVar3] & 0x3f;
          lVar3 = lVar3 + 1;
        } while ((int)lVar3 < (int)lVar6);
      }
LAB_008d5620:
      *param_2 = uVar7 + *(short *)(param_1 + 0x18);
      pbVar5 = pbVar5 + lVar6;
      param_2 = param_2 + 1;
    } while ((pbVar5 != pbVar8) && (param_2 != psVar1));
  }
  *param_2 = 0;
  return;
}

