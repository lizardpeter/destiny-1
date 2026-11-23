
ulong FUN_00b5c530(long param_1,uint param_2,uint param_3,undefined8 param_4,int param_5,
                  long param_6)

{
  undefined1 *puVar1;
  long lVar2;
  ushort uVar3;
  uint uVar4;
  long lVar5;
  long lVar6;
  float fVar7;
  bool bVar8;
  char cVar9;
  uint uVar10;
  ulong uVar11;
  ushort uVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  long lVar16;
  int iVar17;
  uint uVar18;
  long lVar19;
  float fVar20;
  uint local_44;
  undefined1 local_3d;
  undefined4 local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  *(undefined8 *)(param_1 + 0x18) = param_4;
  local_44 = 0;
  if ((*(char *)(param_1 + 9) != '\0') && (*(char *)(param_1 + 10) != '\0')) {
    bVar8 = false;
    lVar5 = *(long *)(param_1 + 0x10);
    iVar17 = 0;
    lVar16 = 0;
    iVar15 = -1;
    do {
      uVar14 = *(uint *)(lVar5 + 0x12cc0 + lVar16 * 4);
      uVar18 = 1;
      if (uVar14 != 0) {
        uVar18 = 1;
        while (!bVar8) {
          if (uVar18 == 0) {
            uVar18 = 0;
            break;
          }
          if ((uVar18 & uVar14) != 0) {
            bVar8 = true;
          }
          uVar18 = uVar18 * 2;
          iVar15 = iVar15 + 1;
        }
      }
      if (bVar8) break;
      iVar17 = iVar17 + 1;
      lVar16 = lVar16 + 1;
      iVar13 = (int)lVar16 * 0x20;
      uVar18 = 1;
      iVar15 = iVar13 + -1;
    } while (iVar13 < 0x401);
    uVar14 = (param_3 & 3) << 0x1b | (param_2 & 3) << 0x1d;
    local_44 = 0;
    do {
      if ((0x3ff < iVar15) || (param_5 <= (int)local_44)) break;
      lVar16 = (long)(short)iVar15 * 0x80;
      puVar1 = &DAT_028832d8 + lVar16;
      cVar9 = FUN_00b5b650(puVar1,*(undefined4 *)(param_1 + 0xc));
      if (cVar9 != '\0') {
        lVar6 = (&DAT_02883348)
                [(long)*(short *)(*(long *)(param_1 + 0x10) + 0xb4 +
                                 ((ulong)(uint)(&DAT_028832e0)[(long)(short)iVar15 * 0x20] & 0x3fff)
                                 * 6) * 0x10];
        lVar19 = (long)*(int *)(param_1 + 0xc) * 0x40;
        lVar2 = lVar6 + 0x20 + lVar19;
        local_3c = 0;
        local_3d = 0;
        cVar9 = FUN_00b5c2a0(param_1,puVar1,lVar2,&local_3d,&local_3c);
        uVar3 = *(ushort *)(lVar6 + 0x58 + lVar19);
        uVar12 = uVar3 & 0xff7f;
        if (cVar9 != '\0') {
          uVar12 = uVar3 | 0x80;
        }
        *(ushort *)(lVar6 + 0x58 + lVar19) = uVar12;
        *(undefined4 *)(lVar6 + 0x48 + lVar19) = local_3c;
        if (((uVar12 & 0x80) != 0) && ((*(byte *)((long)&DAT_02883328 + lVar16 + 1) & 2) == 0)) {
          fVar20 = (float)FUN_00bc6040(puVar1,lVar2,local_3d,0);
          if (fVar20 < 0.0) {
            fVar20 = 0.0;
          }
          fVar7 = fVar20 * DAT_0168c094;
          lVar16 = (long)(int)local_44;
          uVar4 = *(uint *)(param_6 + lVar16 * 4);
          *(uint *)(param_6 + lVar16 * 4) = uVar4 & 0x87ffffff | uVar14;
          uVar10 = ((uint)(long)fVar7 & 0x3ff) << 0xf;
          if (0.0 <= fVar20 + DAT_0168c098) {
            uVar10 = 0x1ff8000;
          }
          *(uint *)(param_6 + lVar16 * 4) =
               (&DAT_028832e0)[(long)(short)iVar15 * 0x20] & 0x3fff | uVar4 & 0x80000000 | uVar14 |
               uVar10;
          FUN_00b9b720(5,puVar1);
          local_44 = local_44 + 1;
        }
      }
      lVar16 = (long)iVar17;
      bVar8 = false;
      do {
        uVar4 = *(uint *)(lVar5 + 0x12cc0 + lVar16 * 4);
        if (uVar4 != 0) {
          while (!bVar8) {
            if (uVar18 == 0) {
              uVar18 = 0;
              break;
            }
            if ((uVar18 & uVar4) != 0) {
              bVar8 = true;
            }
            uVar18 = uVar18 * 2;
            iVar15 = iVar15 + 1;
          }
        }
        if (bVar8) break;
        lVar16 = lVar16 + 1;
        iVar17 = iVar17 + 1;
        uVar18 = 1;
        iVar15 = iVar17 * 0x20 + -1;
      } while (iVar17 * 0x20 < 0x401);
    } while( true );
  }
  *(undefined8 *)(param_1 + 0x38) = 0;
  *(undefined4 *)(param_1 + 0x40) = 0;
  if (*DAT_01a1f100 != local_38) {
    uVar11 = thunk_FUN_012aa7f6();
    return uVar11;
  }
  return (ulong)local_44;
}

