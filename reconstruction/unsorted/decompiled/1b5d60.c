
void FUN_001b5d60(uint param_1,uint param_2)

{
  byte *pbVar1;
  ushort *puVar2;
  long lVar3;
  long lVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  long lVar9;
  uint *puVar10;
  long lVar11;
  long lVar12;
  ulong uVar13;
  ulong uVar14;
  short sVar15;
  uint uVar16;
  uint *puVar17;
  undefined4 local_50;
  undefined4 local_4c;
  undefined1 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_2 != 0xffffffff) {
    lVar9 = (ulong)(((uint)((int)param_2 >> 0xd) >> 0x12 | 0x3ff) & (int)param_2 >> 0xd) * 0x40;
    lVar3 = *DAT_01a238a0;
    lVar11 = *(long *)(lVar3 + 0x10 + lVar9);
    uVar13 = (ulong)((param_2 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar9));
    puVar17 = (uint *)((lVar11 + uVar13) -
                      ((long)*(int *)(lVar3 + 0x34 + lVar9) & *(ulong *)(lVar11 + 8 + uVar13)));
    uVar5 = puVar17[1];
    lVar3 = *(long *)(&DAT_01907950 + (long)(char)uVar5 * 8);
    if ((puVar17[5] & 2) == 0) {
      sVar15 = (short)puVar17[6];
    }
    else {
      puVar10 = (uint *)FUN_003055a0();
      sVar15 = *(short *)((long)puVar17 + 0x16);
      uVar7 = puVar17[6];
      uVar16 = *puVar10 * 0x19660d + 0x3c6ef35f;
      *puVar10 = uVar16;
      sVar15 = (short)((uVar16 >> 0x10) * ((int)sVar15 - (int)(short)uVar7) >> 0x10) + (short)uVar7;
    }
    local_4c = *(undefined4 *)
                (FUN_00002410 + DAT_025d79a8 + (ulong)(DAT_025d79b0 * (param_1 & 0x1fff)));
    local_50 = 0xffffffff;
    local_48 = 0;
    local_40 = 0;
    do {
      lVar11 = FUN_001b2050(&local_50);
      if (lVar11 == 0) {
        uVar7 = FUN_0006e750(&DAT_025d90d0);
        lVar11 = DAT_025d79a8;
        if (uVar7 != 0xffffffff) {
          lVar12 = (ulong)(((uint)((int)uVar7 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar7 >> 0xd) * 0x40;
          uVar14 = (ulong)((param_1 & 0x1fff) * DAT_025d79b0);
          lVar9 = *DAT_01a238a0;
          lVar4 = *(long *)(lVar9 + 0x10 + lVar12);
          uVar13 = (ulong)((uVar7 & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar12));
          puVar10 = (uint *)((lVar4 + uVar13) -
                            ((long)*(int *)(lVar9 + 0x34 + lVar12) & *(ulong *)(lVar4 + 8 + uVar13))
                            );
          puVar10[4] = 0xffffffff;
          puVar10[5] = 0xffffffff;
          puVar10[2] = 0xffffffff;
          puVar10[3] = 0xffffffff;
          puVar10[0] = 0xffffffff;
          puVar10[1] = 0xffffffff;
          *puVar10 = param_1;
          puVar10[1] = param_2;
          puVar10[2] = *(uint *)(FUN_00002410 + lVar11 + uVar14);
          *(uint *)(FUN_00002410 + lVar11 + uVar14) = uVar7;
          puVar10[3] = *puVar17;
          *puVar17 = uVar7;
          uVar16 = thunk_FUN_005916f0();
          uVar8 = 0xffffffff;
          puVar10[4] = uVar16;
          if (sVar15 != -1) {
            iVar6 = thunk_FUN_005916f0();
            uVar8 = iVar6 + sVar15;
          }
          puVar10[5] = uVar8;
          *(byte *)(puVar10 + 6) = (byte)puVar10[6] | 1;
          if ((byte)puVar17[1] == 0xe) {
            pbVar1 = (byte *)(lVar11 + 0x22f1 + uVar14);
            *pbVar1 = *pbVar1 | 0x40;
            *(uint *)(lVar11 + 0x22f4 + uVar14) = param_1;
          }
          else {
            puVar2 = (ushort *)(lVar11 + 0x22f0 + uVar14);
            *puVar2 = *puVar2 | (ushort)(1 << ((byte)puVar17[1] & 0x1f));
          }
          if (((long)(char)uVar5 - 10U < 4) && (*(code **)(lVar3 + 8) != (code *)0x0)) {
            (**(code **)(lVar3 + 8))(uVar7);
          }
        }
        goto LAB_001b5feb;
      }
    } while (*(uint *)(lVar11 + 4) != param_2);
    iVar6 = -1;
    if (sVar15 != -1) {
      iVar6 = thunk_FUN_005916f0();
      iVar6 = iVar6 + sVar15;
    }
    *(int *)(lVar11 + 0x14) = iVar6;
    *(byte *)(lVar11 + 0x18) = *(byte *)(lVar11 + 0x18) | 1;
  }
LAB_001b5feb:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

