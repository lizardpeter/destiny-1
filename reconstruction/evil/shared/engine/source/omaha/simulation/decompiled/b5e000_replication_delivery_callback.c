
void FUN_00b5e000(long param_1,int param_2,byte param_3,char param_4)

{
  byte *pbVar1;
  long *plVar2;
  long *plVar3;
  ushort *puVar4;
  int iVar5;
  uint uVar6;
  long *plVar7;
  undefined4 *puVar8;
  long lVar9;
  long lVar10;
  bool bVar11;
  byte bVar12;
  char cVar13;
  ushort uVar14;
  uint uVar15;
  ulong uVar16;
  long lVar17;
  bool bVar18;
  ushort uVar19;
  ulong uVar20;
  long *plVar21;
  undefined8 *puVar22;
  bool bVar23;
  long lVar24;
  undefined8 *puVar25;
  
  plVar7 = (long *)(param_1 + 0x20);
  do {
    plVar21 = plVar7;
    plVar7 = (long *)*plVar21;
    if (plVar7 == (long *)0x0) goto LAB_00b5e515;
  } while (*(int *)(plVar7 + 1) != param_2);
  do {
    iVar5 = *(int *)(plVar7 + 3);
    *(int *)(plVar7 + 3) = iVar5 + -1;
    lVar17 = (long)(iVar5 + -1) * 0x20;
    lVar9 = plVar7[2];
    uVar6 = *(uint *)(lVar9 + 0x10 + lVar17);
    if (uVar6 != 0xffffffff) {
      lVar10 = (&DAT_02883348)
               [(long)*(short *)(*(long *)(param_1 + 0x10) + 0xb4 + (ulong)(uVar6 & 0x3fff) * 6) *
                0x10];
      lVar24 = (long)*(int *)(param_1 + 0xc) * 0x40;
      bVar18 = false;
      puVar22 = *(undefined8 **)(lVar10 + 0x50 + lVar24);
      plVar3 = (long *)(lVar10 + 0x20 + lVar24);
      if (param_3 == 1) {
        bVar12 = 0;
        if (param_4 == '\0') {
          if ((*(byte *)(lVar9 + 0x14 + lVar17) & 4) == 0) {
            FUN_011c1510(plVar3,lVar10 + 0x30 + lVar24);
            uVar14 = *(ushort *)(lVar10 + 0x58 + lVar24);
            uVar19 = uVar14 | 0x40;
            if ((uVar14 & 0x100) == 0) {
              uVar19 = uVar14 & 0xffbf;
            }
            *(ushort *)(lVar10 + 0x58 + lVar24) = uVar19;
            if ((uVar19 & 0x400) == 0) {
              uVar19 = uVar19 & 0xfdff;
            }
            else {
              uVar19 = uVar19 | 0x200;
            }
            *(ushort *)(lVar10 + 0x58 + lVar24) = uVar19;
            bVar18 = false;
          }
          else {
            uVar15 = FUN_00b50b70(*(long *)(param_1 + 0x10),uVar6);
            if (uVar15 == uVar6) {
              pbVar1 = (byte *)(lVar10 + 0x58 + lVar24);
              *pbVar1 = *pbVar1 & 0x7f;
            }
            iVar5 = *(int *)(lVar10 + 0x28 + lVar24);
            if (((iVar5 << 0x12) >> 0x12 & 0xfffffffeU) == 0xfffffffe) {
              puVar8 = (undefined4 *)*plVar3;
              uVar16 = (ulong)(((iVar5 << 4) >> 0x12) + 0x1f >> 5);
              if ((uVar16 * 4 < 0x21) && (((ulong)puVar8 & 3) == 0)) {
                uVar16 = uVar16 & 0x3fffffffffffffff;
                if ((uVar16 != 0) && (*puVar8 = 0, uVar16 != 1)) {
                  uVar20 = 1;
                  do {
                    *(undefined4 *)(*plVar3 + uVar20 * 4) = 0;
                    uVar20 = uVar20 + 1;
                  } while (uVar16 != uVar20);
                }
              }
              else {
                thunk_FUN_012aa986(puVar8,0);
              }
            }
            else {
              *(int *)plVar3 = 0;
            }
            plVar2 = (long *)(lVar10 + 0x30 + lVar24);
            iVar5 = *(int *)(lVar10 + 0x38 + lVar24);
            if (((iVar5 << 0x12) >> 0x12 & 0xfffffffeU) == 0xfffffffe) {
              puVar8 = (undefined4 *)*plVar2;
              uVar16 = (ulong)(((iVar5 << 4) >> 0x12) + 0x1f >> 5);
              if ((uVar16 * 4 < 0x21) && (((ulong)puVar8 & 3) == 0)) {
                uVar16 = uVar16 & 0x3fffffffffffffff;
                if ((uVar16 != 0) && (*puVar8 = 0, uVar16 != 1)) {
                  uVar20 = 1;
                  do {
                    *(undefined4 *)(*plVar2 + uVar20 * 4) = 0;
                    uVar20 = uVar20 + 1;
                  } while (uVar16 != uVar20);
                }
              }
              else {
                thunk_FUN_012aa986(puVar8,0);
              }
            }
            else {
              *(undefined4 *)plVar2 = 0;
            }
            puVar4 = (ushort *)(lVar10 + 0x58 + lVar24);
            *puVar4 = *puVar4 & 0xf8bf;
            bVar18 = true;
          }
          bVar12 = *(byte *)(lVar9 + 0x14 + lVar17) >> 3 & 1;
        }
      }
      else {
        bVar12 = 0;
      }
      if (puVar22 != (undefined8 *)0x0) {
        puVar25 = (undefined8 *)(lVar10 + 0x50 + lVar24);
        puVar4 = (ushort *)(lVar10 + 0x58 + lVar24);
        bVar11 = false;
        bVar23 = bVar18;
        do {
          bVar11 = (bool)(puVar22 == (undefined8 *)(lVar9 + 8 + lVar17) | bVar11);
          if ((!bVar23 && (param_3 ^ 1) == 0) && (bVar23 = false, param_4 == '\0')) {
            bVar23 = bVar11;
          }
          if ((bVar23) || (!(bool)(bVar11 ^ 1))) {
            *puVar25 = *puVar22;
            FUN_002c7230(puVar22 + 2);
            *(undefined4 *)(puVar22 + 1) = 0xffffffff;
          }
          else if (!bVar11) {
            FUN_011c1430(plVar3,puVar22 + 2);
            uVar14 = *puVar4;
            if (((uVar14 & 0x40) == 0) && ((*(byte *)((long)puVar22 + 0xd) & 1) == 0)) {
              uVar14 = uVar14 & 0xffbf;
            }
            else {
              uVar14 = uVar14 | 0x40;
            }
            *puVar4 = uVar14;
            if (((uVar14 & 0x200) == 0) && ((*(byte *)((long)puVar22 + 0xd) & 4) == 0)) {
              uVar14 = uVar14 & 0xfdff;
            }
            else {
              uVar14 = uVar14 | 0x200;
            }
            *puVar4 = uVar14;
            puVar25 = puVar22;
          }
          puVar22 = (undefined8 *)*puVar25;
        } while (puVar22 != (undefined8 *)0x0);
      }
      if ((param_3 ^ 1) == 0 && param_4 == '\0') {
        puVar4 = (ushort *)(lVar10 + 0x58 + lVar24);
        uVar14 = *(ushort *)(lVar10 + 0x58 + lVar24);
        if ((uVar14 & 1) != 0) {
          *puVar4 = uVar14 & 0xfffe;
          *(int *)(param_1 + 0x28) = *(int *)(param_1 + 0x28) + -1;
          uVar14 = *puVar4;
        }
        if ((uVar14 & 2) != 0) {
          if (((*(int *)(lVar10 + 0x28 + lVar24) << 0x12) >> 0x12 & 0xfffffffeU) == 0xfffffffe) {
            cVar13 = FUN_002c7650(plVar3);
            if (cVar13 != '\0') {
              uVar14 = *puVar4;
LAB_00b5e429:
              *puVar4 = uVar14 & 0xfffd;
              *(int *)(param_1 + 0x2c) = *(int *)(param_1 + 0x2c) + -1;
            }
          }
          else if ((int)*plVar3 == 0) goto LAB_00b5e429;
        }
        if (bVar18) {
          FUN_002c7230(plVar3);
          plVar3[1] = 0;
          *plVar3 = 0;
          *(undefined4 *)(lVar10 + 0x28 + lVar24) = 0x4000;
          FUN_002c7230(lVar10 + 0x30 + lVar24);
          *(undefined8 *)(lVar10 + 0x38 + lVar24) = 0;
          *(undefined8 *)(lVar10 + 0x30 + lVar24) = 0;
          *(undefined4 *)(lVar10 + 0x38 + lVar24) = 0x4000;
          *puVar4 = 0;
          *(int *)(param_1 + 0x30) = *(int *)(param_1 + 0x30) + -1;
          FUN_00b5e530(param_1,uVar6,0);
        }
        if ((bVar12 != 0) && ((*puVar4 & 8) != 0)) {
          *puVar4 = *puVar4 & 0xfff7;
          *(int *)(param_1 + 0x34) = *(int *)(param_1 + 0x34) + -1;
          FUN_00b57860(*(undefined8 *)(param_1 + 0x10),uVar6,*(undefined4 *)(param_1 + 0xc));
        }
      }
    }
    if (*(int *)(plVar7 + 3) == 0) {
      plVar7[2] = *(undefined8 *)plVar7[2];
      *(undefined4 *)(plVar7 + 3) = 0x40;
      FUN_00aeaf90();
      if (plVar7[2] == 0) {
        *plVar21 = *plVar7;
        FUN_00aeaf90(plVar7);
LAB_00b5e515:
        FUN_00aeb030(*(undefined8 *)(param_1 + 0x10));
        return;
      }
    }
  } while( true );
}

