
void FUN_001e3d40(long param_1)

{
  long lVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  int *piVar7;
  uint *puVar8;
  long lVar9;
  long lVar10;
  int iVar11;
  long lVar12;
  int iVar13;
  ulong uVar14;
  ulong uVar15;
  int iVar16;
  uint uVar17;
  int iVar18;
  uint uVar19;
  uint local_248;
  undefined1 local_240 [264];
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar6 = FUN_000b89f0();
  local_248 = 0;
  piVar7 = (int *)FUN_000ba9f0(uVar6,0,0,0xd2f8);
  *piVar7 = 0;
  thunk_FUN_012aa986(piVar7 + 0x2ee2,0,3000);
  thunk_FUN_012aa986(piVar7 + 0x31d0,0xff,3000);
  iVar4 = FUN_002b0770();
  iVar4 = iVar4 + -1;
LAB_001e3de0:
  do {
    do {
      if (iVar4 == -1) {
        if (local_248 != 0) {
          iVar4 = FUN_000b9a00(local_248);
          if (iVar4 == -1) {
            iVar4 = FUN_000b9430(0,local_248,2);
          }
          FUN_000b8000(iVar4,0);
          lVar10 = FUN_000b7d80(iVar4);
          FUN_000b7c60(iVar4,local_248,800);
          iVar4 = *(int *)(param_1 + 8);
          if (iVar4 != -1) {
            do {
              *(int *)(param_1 + 8) = iVar4 + -1;
              lVar9 = FUN_002b0510();
              lVar1 = lVar9 + 1;
              uVar6 = thunk_FUN_012aa816(lVar1);
              iVar4 = FUN_000bc8f0(lVar1,uVar6);
              uVar19 = (uint)(iVar4 * 0xceb) % 0x5dc;
              uVar15 = (ulong)uVar19;
              iVar5 = (int)*(short *)((long)piVar7 + uVar15 * 2 + 0xbb88);
              if (0 < iVar5) {
                iVar18 = 0;
                do {
                  iVar11 = (int)uVar15;
                  lVar12 = (long)iVar11;
                  if ((int)*(short *)((long)piVar7 + lVar12 * 2 + 0xc740) == uVar19) {
                    if (((piVar7[lVar12 * 8 + 6] == iVar4) && (piVar7[lVar12 * 8 + 7] == 0)) &&
                       (piVar7[lVar12 * 8 + 8] == 0)) {
                      if ((iVar11 != -1) && (*(long *)(piVar7 + lVar12 * 8 + 2) == 0)) {
                        *(long *)(piVar7 + lVar12 * 8 + 2) = lVar9;
                        FUN_00087ad0(local_240);
                        FUN_00087e90(local_240);
                        FUN_00087b10(local_240,s__packages_0161bcef + 1);
                        FUN_00088400(local_240,lVar1);
                        FUN_000886e0(local_240,local_138,0x100);
                        FUN_000bd570(*(undefined8 *)(lVar10 + 8),local_138,
                                     *(undefined4 *)(lVar9 + 0x104));
                      }
                      break;
                    }
                    if (iVar5 < 2) break;
                    iVar5 = iVar5 + -1;
                  }
                  iVar18 = iVar18 + 1;
                  uVar15 = (ulong)(uint)((iVar11 + 1) % 0x5dc);
                } while (iVar18 < 0x5dc);
              }
              iVar4 = *(int *)(param_1 + 8);
            } while (iVar4 != -1);
          }
        }
        uVar6 = FUN_000b89f0();
        FUN_000aedc0(uVar6,piVar7);
        if (*DAT_01a1f100 != local_38) {
          thunk_FUN_012aa7f6();
          return;
        }
        return;
      }
      iVar5 = iVar4 + -1;
      puVar8 = (uint *)FUN_002b08c0(iVar4);
      uVar19 = *puVar8;
      iVar4 = iVar5;
    } while ((uVar19 & 0xf0000000) != 0xd0000000);
    uVar6 = thunk_FUN_012aa816(puVar8 + 1);
    iVar5 = FUN_000bc8f0(puVar8 + 1,uVar6);
    if (local_248 == 0 || local_248 == uVar19) {
      local_248 = uVar19;
    }
    uVar19 = (uint)(iVar5 * 0xceb) % 0x5dc;
    uVar15 = (ulong)uVar19;
    sVar2 = *(short *)((long)piVar7 + uVar15 * 2 + 0xbb88);
    iVar18 = (int)sVar2;
    if (0 < sVar2) {
      iVar16 = 0;
      uVar14 = uVar15;
      iVar11 = iVar18;
      do {
        iVar13 = (int)uVar14;
        lVar10 = (long)iVar13;
        if ((int)*(short *)((long)piVar7 + lVar10 * 2 + 0xc740) == uVar19) {
          if (((piVar7[lVar10 * 8 + 6] == iVar5) && (piVar7[lVar10 * 8 + 7] == 0)) &&
             (piVar7[lVar10 * 8 + 8] == 0)) {
            if (iVar13 != -1) goto LAB_001e3de0;
            break;
          }
          if (iVar11 < 2) break;
          iVar11 = iVar11 + -1;
        }
        iVar16 = iVar16 + 1;
        uVar14 = (ulong)(uint)((iVar13 + 1) % 0x5dc);
      } while (iVar16 < 0x5dc);
    }
    iVar11 = *piVar7;
    lVar10 = -1;
    if (iVar11 < 0x5dc) {
      uVar14 = uVar15;
      if (0 < sVar2) {
        do {
          iVar16 = (int)uVar14;
          uVar14 = (ulong)(iVar16 + 1);
          iVar18 = iVar18 - (uint)((int)*(short *)((long)piVar7 +
                                                  (long)(iVar16 % 0x5dc) * 2 + 0xc740) == uVar19);
        } while (0 < iVar18);
      }
      iVar18 = (int)uVar14 % 0x5dc;
      do {
        sVar3 = *(short *)((long)piVar7 + (long)iVar18 * 2 + 0xc740);
        uVar17 = (int)uVar14 + (uint)(sVar3 != -1);
        uVar14 = (ulong)uVar17;
        iVar18 = (int)uVar17 % 0x5dc;
      } while (sVar3 != -1);
      lVar10 = (long)iVar18;
      if (iVar18 != -1) {
        piVar7[lVar10 * 8 + 6] = iVar5;
        piVar7[lVar10 * 8 + 7] = 0;
        piVar7[lVar10 * 8 + 8] = 0;
        *(short *)((long)piVar7 + lVar10 * 2 + 0xc740) = (short)uVar19;
        *(short *)((long)piVar7 + uVar15 * 2 + 0xbb88) = sVar2 + 1;
        iVar11 = *piVar7;
      }
      *piVar7 = iVar11 + 1;
    }
    *(uint **)(piVar7 + lVar10 * 8 + 4) = puVar8;
    (piVar7 + lVar10 * 8 + 2)[0] = 0;
    (piVar7 + lVar10 * 8 + 2)[1] = 0;
  } while( true );
}

