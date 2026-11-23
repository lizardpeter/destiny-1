
long FUN_0023cb40(uint param_1)

{
  uint *puVar1;
  int iVar2;
  undefined8 *puVar3;
  long lVar4;
  long lVar5;
  uint uVar6;
  undefined8 uVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  uint uVar11;
  ulong *puVar12;
  ulong uVar13;
  long lVar14;
  undefined4 uStack_18c;
  undefined4 uStack_184;
  undefined1 local_180 [192];
  long local_c0;
  
  lVar5 = DAT_02648518;
  local_c0 = *DAT_01a1f100;
  uVar13 = (ulong)((param_1 & 0x1fff) * DAT_02648520);
  puVar1 = (uint *)(uVar13 + 0x80 + DAT_02648518);
  lVar8 = uVar13 + 0x20 + DAT_02648518;
  uVar11 = *(uint *)(uVar13 + 0x80 + DAT_02648518);
  do {
    uVar6 = uVar11;
    LOCK();
    uVar11 = *puVar1;
    if (uVar6 == uVar11) {
      *puVar1 = uVar6 | 0x80000000;
      uVar11 = uVar6;
    }
    UNLOCK();
  } while (uVar11 != uVar6);
  uVar11 = uVar6 >> 5 & 3;
  lVar10 = *(long *)(uVar13 + 0x88 + lVar5);
  *(long *)(uVar13 + 0x88 + lVar5) = lVar10 + 1;
  lVar9 = ((ulong)((uVar6 >> 1 & 3) + (uVar11 - (uVar6 >> 3 & 3))) % (ulong)uVar11) * 0x20;
  *(long *)(lVar8 + lVar9) = lVar10;
  puVar3 = *(undefined8 **)(lVar8 + 0x10 + lVar9);
  iVar2 = *(int *)(lVar8 + 0x18 + lVar9);
  if (iVar2 < 1) {
    puVar12 = (ulong *)(uVar13 + 0x90 + lVar5);
  }
  else {
    puVar12 = (ulong *)(uVar13 + 0x90 + lVar5);
    lVar10 = 0;
    lVar14 = 1;
    do {
      lVar4 = *(long *)(lVar5 + 0x18 + uVar13);
      FUN_000f8fe0(local_180,DAT_026485b0,(long *)(lVar8 + lVar9),7,
                   *(undefined8 *)(lVar4 + -8 + lVar14 * 8),7,CONCAT44(uStack_18c,param_1),
                   CONCAT44(uStack_184,9),DAT_025d11c0,DAT_025d11c8);
      uVar7 = FUN_000fb3e0(*(undefined4 *)(lVar4 + lVar14 * 8),local_180,DAT_025d12b1 | DAT_025d12ad
                          );
      puVar3[lVar10] = uVar7;
      if ((int)lVar10 == 0) {
        if ((*puVar12 & 0xffff00000000) != 0xffff00000000) {
          FUN_000fb6e0(*puVar3);
        }
      }
      else {
        FUN_000fb670(uVar7,puVar3[lVar10 + -1]);
      }
      lVar14 = lVar14 + 2;
      lVar10 = lVar10 + 1;
    } while (iVar2 != (int)lVar10);
    lVar10 = *(long *)(lVar8 + lVar9);
  }
  *puVar12 = puVar3[iVar2 + -1];
  *(undefined4 *)(lVar8 + 8 + lVar9) = 0;
  if (*DAT_01a1f100 != local_c0) {
    lVar8 = thunk_FUN_012aa7f6();
    return lVar8;
  }
  return lVar10;
}

