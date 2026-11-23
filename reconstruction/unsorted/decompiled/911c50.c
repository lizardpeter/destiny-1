
void FUN_00911c50(uint param_1,uint param_2,undefined1 param_3,char param_4)

{
  byte *pbVar1;
  uint *puVar2;
  long lVar3;
  char cVar4;
  uint uVar5;
  undefined4 uVar6;
  int iVar7;
  ulong uVar8;
  long lVar9;
  long lVar10;
  ulong uVar11;
  ulong uVar12;
  long lVar13;
  long lVar14;
  long lVar15;
  uint uVar16;
  float fVar17;
  long local_a8;
  long local_a0;
  long local_90;
  undefined4 local_88;
  undefined1 local_80;
  undefined1 local_78 [16];
  uint local_68;
  uint local_60;
  long local_58;
  undefined4 local_50;
  long local_48;
  long local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar15 = ((ulong)param_1 & 0xffff) * 0x2af0;
  lVar3 = *(long *)(DAT_0273ea80 + 8);
  uVar5 = *(uint *)(lVar3 + 0x644 + lVar15);
  if (uVar5 != param_2) {
    puVar2 = (uint *)(lVar3 + 0x644 + lVar15);
    lVar9 = (ulong)((*(uint *)(lVar3 + 4 + lVar15) & 0x1fff) * DAT_02689590) + DAT_02689588;
    if (param_4 == '\0') {
      FUN_0052c540(param_1);
      uVar5 = *puVar2;
    }
    lVar10 = DAT_026897f8;
    if (uVar5 != 0xffffffff) {
      uVar8 = (ulong)((uVar5 & 0x1fff) * DAT_02689800);
      uVar11 = (ulong)DAT_02689818;
      uVar12 = (ulong)((*(uint *)(((uVar8 + DAT_026897f8) -
                                  (*(ulong *)(DAT_026897f8 + 8 + uVar8) & uVar11)) + 0x68) & 0x1fff)
                      * DAT_02689800);
      uVar8 = *(ulong *)(DAT_026897f8 + 8 + uVar12);
      uVar5 = FUN_006ed8f0();
      lVar13 = DAT_02692228;
      uVar16 = (uVar5 & 0x1fff) * DAT_02692230;
      if (*(char *)(DAT_0273ea90 + 0xa8) != '\0') {
        local_40 = *(long *)(DAT_0273ea90 + 0xa9);
        if (*(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar15) == local_40) {
          uVar6 = FUN_00923150(*puVar2);
          FUN_006e9a50(uVar6,uVar5);
          iVar7 = FUN_00071f60(lVar3 + 0x688 + lVar15);
          if ((iVar7 != -1) && (*(int *)(lVar3 + 0x690 + lVar15) != -1)) {
            FUN_00649d40(param_1);
          }
        }
      }
      lVar10 = (lVar10 + uVar12) - (uVar11 & uVar8);
      FUN_00923280(param_1,0xffffffff,param_3);
      *(undefined4 *)(lVar10 + 0x9d8) = 0xffffffff;
      *(uint *)(lVar10 + 0x9dc) = param_1;
      FUN_00bd5ca0(*puVar2,0);
      uVar6 = FUN_006ed8f0(*puVar2);
      FUN_00511710(uVar6);
      pbVar1 = (byte *)((ulong)uVar16 + 6 + lVar13);
      *pbVar1 = *pbVar1 & 0xfb;
      FUN_00301dc0(lVar9,0xffffffff);
      *puVar2 = 0xffffffff;
    }
    *(undefined8 *)(lVar3 + 0x654 + lVar15) = 0;
    if (param_2 != 0xffffffff) {
      uVar8 = (ulong)((param_2 & 0x1fff) * DAT_02689800);
      lVar13 = (uVar8 + DAT_026897f8) - (*(ulong *)(DAT_026897f8 + 8 + uVar8) & (long)DAT_02689818);
      uVar8 = (ulong)((*(uint *)(lVar13 + 0x68) & 0x1fff) * DAT_02689800);
      lVar14 = (DAT_026897f8 + uVar8) - ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar8));
      uVar5 = FUN_006ed8f0(param_2);
      lVar10 = DAT_02692228;
      uVar16 = DAT_02692230 * (uVar5 & 0x1fff);
      *(uint *)(lVar14 + 0x9d8) = param_1;
      *(undefined4 *)(lVar14 + 0x9dc) = 0xffffffff;
      FUN_00bd5ca0(param_2,1);
      *puVar2 = param_2;
      FUN_00301dc0(lVar9,uVar5);
      FUN_00923280(param_1,param_2,param_3);
      uVar8 = (ulong)((*(uint *)(lVar13 + 0x68) & 0x1fff) * DAT_02689800);
      FUN_0073ba20((DAT_026897f8 + uVar8) -
                   ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar8)));
      FUN_00bd5ca0(param_2,1);
      *puVar2 = param_2;
      FUN_0052c730(param_1,param_2);
      FUN_00301dc0(lVar9,uVar5);
      pbVar1 = (byte *)((ulong)uVar16 + 6 + lVar10);
      *pbVar1 = *pbVar1 | 4;
      FUN_00511600(uVar5);
      *(undefined8 *)(lVar3 + 0x64c + lVar15) = 0xffffffffffffffff;
      fVar17 = (float)FUN_00591b80();
      FUN_009187e0(fVar17 + fVar17,0,param_1);
      FUN_0073d8f0(param_1);
      if (*(char *)(DAT_0273ea90 + 0xa8) != '\0') {
        local_48 = *(long *)(DAT_0273ea90 + 0xa9);
        if (*(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar15) == local_48) {
          FUN_0011a0d0(*(long *)(DAT_0273ea80 + 8) + 0x80 + lVar15,uVar5);
          uVar6 = FUN_00923150(*puVar2);
          FUN_006e98c0(uVar6,uVar5);
          FUN_00648f50(param_1);
          iVar7 = FUN_00071f60(lVar3 + 0x688 + lVar15);
          if ((iVar7 != -1) && (*(int *)(lVar3 + 0x690 + lVar15) != -1)) {
            uVar6 = FUN_006ed8f0(param_2);
            FUN_00649c10(param_1,uVar6);
          }
        }
      }
      uVar8 = (ulong)((uVar5 & 0x1fff) * DAT_02692230);
      cVar4 = FUN_003381f0(DAT_02692228 + uVar8,*(undefined4 *)PTR_DAT_019b3ee8,
                           *(undefined4 *)(DAT_02692228 + 0x54 + uVar8),local_78);
      if (cVar4 != '\0') {
        local_80 = 0;
        lVar3 = *DAT_01a238a0;
        lVar9 = (ulong)(((uint)((int)local_68 >> 0xd) >> 0x12 | 0x3ff) & (int)local_68 >> 0xd) *
                0x40;
        lVar15 = *(long *)(lVar3 + 0x10 + lVar9);
        uVar8 = (ulong)((local_68 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar9));
        local_a8 = (lVar15 + uVar8) -
                   ((long)*(int *)(lVar3 + 0x34 + lVar9) & *(ulong *)(lVar15 + 8 + uVar8));
        lVar9 = (ulong)(((uint)((int)local_60 >> 0xd) >> 0x12 | 0x3ff) & (int)local_60 >> 0xd) *
                0x40;
        lVar15 = *(long *)(lVar3 + 0x10 + lVar9);
        uVar8 = (ulong)((local_60 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar9));
        local_a0 = ((lVar15 + uVar8) -
                   ((long)*(int *)(lVar3 + 0x34 + lVar9) & *(ulong *)(lVar15 + 8 + uVar8))) +
                   local_58;
        local_88 = local_50;
        local_90 = local_58;
        FUN_00353610(&local_a8);
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

