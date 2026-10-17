
void FUN_0056d2f0(long param_1,char param_2,int param_3,int *param_4)

{
  char *pcVar1;
  short sVar2;
  short sVar3;
  short sVar4;
  short sVar5;
  short sVar6;
  short sVar7;
  int iVar8;
  long lVar9;
  undefined *puVar10;
  short sVar11;
  short sVar12;
  long lVar13;
  undefined8 uVar14;
  long lVar15;
  short sVar16;
  ushort uVar17;
  uint uVar18;
  undefined8 *puVar19;
  short sVar20;
  short sVar21;
  short sVar22;
  short sVar23;
  long lVar24;
  ulong uVar25;
  long lVar26;
  bool bVar27;
  long local_38;
  
  puVar10 = PTR_DAT_019e4bf0;
  if (0 < param_3) {
    lVar13 = (long)param_2;
    sVar16 = 0;
    sVar22 = 0;
    sVar23 = 0;
    sVar20 = 0;
    sVar21 = 0;
    sVar12 = 0;
    do {
      iVar8 = *param_4;
      *param_4 = iVar8 + 1;
      lVar9 = *(long *)(puVar10 + 8);
      uVar14 = FUN_000e8680(lVar9,0,0xffffffff);
      lVar24 = (long)iVar8 * 0x40;
      pcVar1 = (char *)(param_1 + 0x60 + lVar24);
      thunk_FUN_012aa986(pcVar1,0,uVar14);
      uVar17 = *(ushort *)(lVar9 + 0x1c) & 0x78;
      bVar27 = uVar17 != 0;
      if (uVar17 == 0) {
        uVar18 = *(uint *)(lVar9 + 0x20);
        if ((*(ushort *)(lVar9 + 0x1c) & 0x40) != 0) {
          lVar15 = FUN_000e8a90(lVar9,pcVar1);
          if (lVar15 == 0) {
            uVar18 = uVar18 | 0x5488bf;
          }
          else {
            uVar18 = *(uint *)(lVar15 + 0x20) & 0x5488bf | uVar18;
          }
        }
        bVar27 = (uVar18 & 0xc08070) != 0;
      }
      if (bVar27) {
        FUN_000e6730(lVar9,pcVar1,0,0xffffffff,0);
      }
      *pcVar1 = param_2;
      sVar2 = *(short *)(param_1 + lVar13 * 0xc);
      *(short *)(param_1 + 0x62 + lVar24) = sVar12;
      *(short *)(param_1 + 100 + lVar24) = sVar2;
      sVar3 = *(short *)(param_1 + 2 + lVar13 * 0xc);
      local_38 = 0;
      *(short *)(param_1 + 0x66 + lVar24) = sVar16;
      *(short *)(param_1 + 0x68 + lVar24) = sVar3;
      sVar4 = *(short *)(param_1 + 4 + lVar13 * 0xc);
      *(short *)(param_1 + 0x6a + lVar24) = sVar22;
      *(short *)(param_1 + 0x6c + lVar24) = sVar4;
      sVar5 = *(short *)(param_1 + 6 + lVar13 * 0xc);
      *(short *)(param_1 + 0x6e + lVar24) = sVar23;
      *(short *)(param_1 + 0x70 + lVar24) = sVar5;
      sVar6 = *(short *)(param_1 + 8 + lVar13 * 0xc);
      *(short *)(param_1 + 0x72 + lVar24) = sVar20;
      *(short *)(param_1 + 0x74 + lVar24) = sVar6;
      sVar7 = *(short *)(param_1 + 10 + lVar13 * 0xc);
      *(short *)(param_1 + 0x76 + lVar24) = sVar21;
      *(short *)(param_1 + 0x78 + lVar24) = sVar7;
      sVar11 = sVar2;
      while( true ) {
        lVar9 = param_1 + lVar24;
        if (0 < sVar11) {
          lVar15 = (long)*pcVar1 * 0x60 + param_1;
          lVar26 = (long)*(int *)(local_38 * 0x10 + 0x4fd98 + lVar15);
          uVar25 = (ulong)*(uint *)(local_38 * 0x10 + 0x4fd90 + lVar15);
          lVar15 = 0;
          if (uVar25 != 0xffffffff) {
            lVar15 = uVar25 + param_1 + 0x40a0;
          }
          uVar25 = (ulong)*(short *)(lVar9 + 0x62 + local_38 * 4);
          puVar19 = (undefined8 *)(uVar25 * lVar26 + lVar15);
          do {
            thunk_FUN_012aa986(puVar19,0,lVar26);
            *puVar19 = 0;
            puVar19 = (undefined8 *)((long)puVar19 + lVar26);
            uVar18 = (int)uVar25 + 1;
            uVar25 = (ulong)uVar18;
          } while ((int)uVar18 <
                   (int)*(short *)(lVar9 + 100 + local_38 * 4) +
                   (int)*(short *)(lVar9 + 0x62 + local_38 * 4));
        }
        local_38 = local_38 + 1;
        if ((int)local_38 == 6) break;
        sVar11 = *(short *)(lVar9 + 100 + local_38 * 4);
      }
      *(undefined8 *)(param_1 + 0x80 + lVar24) = 0;
      *(undefined1 *)(param_1 + 0x88 + lVar24) = 0;
      *(undefined1 *)(param_1 + 0x89 + lVar24) = 0;
      *(undefined4 *)(param_1 + 0x9c + lVar24) = 0xffffffff;
      FUN_00543ee0(param_1 + 0x8c + lVar24);
      FUN_00543ee0(param_1 + 0x94 + lVar24);
      sVar22 = sVar4 + sVar22;
      sVar23 = sVar5 + sVar23;
      sVar20 = sVar6 + sVar20;
      sVar21 = sVar7 + sVar21;
      sVar12 = sVar2 + sVar12;
      sVar16 = sVar3 + sVar16;
      param_3 = param_3 + -1;
    } while (0 < param_3);
  }
  return;
}

