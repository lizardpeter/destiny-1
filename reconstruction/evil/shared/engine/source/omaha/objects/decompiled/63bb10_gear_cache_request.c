
ulong FUN_0063bb10(long param_1,undefined4 param_2,int param_3,undefined8 param_4,int param_5)

{
  long *plVar1;
  short *psVar2;
  undefined8 uVar3;
  long lVar4;
  bool bVar5;
  char cVar6;
  undefined4 uVar7;
  int iVar8;
  ulong uVar9;
  ulong uVar10;
  int iVar11;
  uint uVar12;
  uint uVar13;
  int iVar14;
  ulong uVar15;
  int local_80;
  int local_7c;
  int local_74;
  uint local_60 [2];
  long local_58;
  int local_50;
  uint uStack_4c;
  long *local_48;
  long *local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar3 = *(undefined8 *)(*(long *)(*(long *)(param_1 + 0x10) + 8) + 0x10);
  plVar1 = (long *)(param_1 + 0x10);
  uVar7 = FUN_0006f140(plVar1);
  FUN_0008f550(local_60,uVar3,uVar7);
  local_40 = *(long **)(param_1 + 0x10);
  local_48 = plVar1;
  if ((int)local_60[0] < local_50) {
    while( true ) {
      uVar10 = (ulong)((local_60[0] & 0xffff) * (int)local_40[2]);
      lVar4 = *local_40;
      cVar6 = FUN_0063b3c0(uVar10 + 8 + lVar4,param_4);
      if ((cVar6 != '\0') && (*(char *)(uVar10 + 0x10c + lVar4) == '\0')) break;
      uVar10 = (ulong)uStack_4c;
LAB_0063bbe0:
      do {
        uVar12 = local_60[0] + 1;
        if ((int)uVar12 < local_50) {
          uVar10 = uVar10 >> 1;
          uStack_4c = (uint)uVar10;
          if (uStack_4c == 0) {
            uVar12 = local_60[0] + 0x20;
            local_60[0] = uVar12 & 0xffffffe0;
            if (local_50 <= (int)local_60[0]) {
LAB_0063bc4e:
              uVar10 = 0;
              uVar12 = local_60[0];
              goto LAB_0063bc50;
            }
            uStack_4c = *(uint *)(local_58 + (long)((int)uVar12 >> 5) * 4);
            while (uVar10 = (ulong)uStack_4c, uVar12 = local_60[0], uStack_4c == 0) {
              local_60[0] = local_60[0] + 0x20;
              if (local_50 <= (int)local_60[0]) goto LAB_0063bc4e;
              uStack_4c = *(uint *)(local_58 + (long)((int)local_60[0] >> 5) * 4);
            }
          }
          local_60[0] = uVar12;
          uVar12 = local_60[0];
          if ((uVar10 & 1) == 0) goto LAB_0063bbe0;
        }
LAB_0063bc50:
        local_60[0] = uVar12;
        if (local_50 <= (int)local_60[0]) goto LAB_0063bd4d;
      } while ((*(uint *)(*(long *)(local_40[1] + 0x10) + (ulong)(local_60[0] >> 5 & 0x7ff) * 4) >>
                (local_60[0] & 0x1f) & 1) == 0);
    }
    uVar9 = (ulong)local_60[0];
    if (local_50 <= (int)local_60[0]) {
      uVar9 = 0xffff;
    }
    uVar15 = 0xffffffff;
    if ((short)uVar9 != -1) {
      uVar13 = *(uint *)(local_48[1] +
                        (ulong)*(uint *)((long)local_48 + 0x1c) +
                        (ulong)*(uint *)(local_48 + 4) * (uVar9 & 0xffff)) &
               *(uint *)((long)local_48 + 0x24);
      uVar12 = *(uint *)((long)local_48 + 0x34);
      if ((uVar12 & 0x40000000) == 0) {
        uVar15 = (ulong)((uVar13 & 0xff) << 0x17 | (uVar12 & 0x3ff) << 0xd | (uint)uVar9 & 0x1fff);
      }
      else {
        uVar15 = (ulong)((uVar13 & 7) << 0x1b | (uVar12 & 0x3fff) << 0xd | (uint)uVar9 & 0x1fff |
                        0x80000000);
      }
    }
    if (*(int *)(uVar10 + 0xd8 + lVar4) < param_3) {
      FUN_0063c7a0(uVar10 + 0xd4 + lVar4);
    }
    if (param_5 == 1) {
      psVar2 = (short *)(uVar10 + 0x12a + lVar4);
      *psVar2 = *psVar2 + 1;
    }
    else if (param_5 == 0) {
      psVar2 = (short *)(uVar10 + 0x128 + lVar4);
      *psVar2 = *psVar2 + 1;
    }
    if ((int)uVar15 != -1) goto LAB_0063be65;
  }
LAB_0063bd4d:
  FUN_00640c10(&local_80);
  if (*(int *)(param_1 + 0x90) == 1) {
    iVar14 = 0x62000;
    iVar11 = local_80;
LAB_0063bd82:
    iVar8 = FUN_00640bd0();
    bVar5 = false;
    if (-1 < iVar11) {
      bVar5 = iVar11 <= (int)((uint)*(ushort *)(*plVar1 + 0x1a) - (uint)*(ushort *)(*plVar1 + 0x18))
      ;
    }
  }
  else {
    if (*(int *)(param_1 + 0x90) == 2) {
      iVar14 = 0x28000;
      iVar11 = local_7c;
      goto LAB_0063bd82;
    }
    iVar8 = FUN_00640bd0();
    bVar5 = false;
    iVar14 = 0;
  }
  if (!bVar5 && (local_74 < 0 || iVar14 + iVar8 <= local_74)) {
    uVar12 = FUN_0006e750(plVar1);
    uVar15 = (ulong)uVar12;
    if (uVar12 != 0xffffffff) {
      uVar10 = (ulong)((uVar12 & 0x1fff) * *(int *)(param_1 + 0x20));
      lVar4 = *(long *)(param_1 + 0x18);
      FUN_00639c60(lVar4 + uVar10,param_2,param_3,param_4);
      *(undefined2 *)(lVar4 + 0x128 + uVar10) = 0;
      *(undefined2 *)(lVar4 + 0x12a + uVar10) = 0;
      *(undefined1 *)(param_1 + 1) = 1;
      if (param_5 == 0) {
        psVar2 = (short *)(lVar4 + 0x128 + uVar10);
        *psVar2 = *psVar2 + 1;
      }
      else if (param_5 == 1) {
        psVar2 = (short *)(lVar4 + 0x12a + uVar10);
        *psVar2 = *psVar2 + 1;
      }
      goto LAB_0063be65;
    }
  }
  uVar15 = 0xffffffff;
  if (*(int *)(param_1 + 0x90) - 1U < 2) {
    FUN_00640150();
  }
LAB_0063be65:
  if (*DAT_01a1f100 == local_38) {
    return uVar15;
  }
  uVar10 = thunk_FUN_012aa7f6();
  return uVar10;
}

