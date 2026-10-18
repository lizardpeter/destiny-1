
undefined8 FUN_00109dc0(int param_1,undefined4 *param_2)

{
  uint uVar1;
  long lVar2;
  char cVar3;
  ushort uVar4;
  int iVar5;
  undefined8 uVar6;
  ulong uVar7;
  short sVar8;
  long lVar9;
  uint uVar10;
  long lVar11;
  long lVar12;
  undefined1 local_69;
  uint local_68 [2];
  long local_60;
  long local_50;
  short local_48;
  int iStack_44;
  bool local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_69 = 0;
  if (param_1 != -1) {
    cVar3 = FUN_002d8470(param_1);
    if (cVar3 != '\0') {
      uVar6 = FUN_002d7300(param_1,param_2);
      if (*DAT_01a1f100 == local_38) {
        return uVar6;
      }
      goto LAB_0010a003;
    }
    local_50 = 0;
    uVar4 = FUN_00107550(0);
    lVar11 = 0;
    local_50 = 0;
    if (uVar4 != 0) {
      local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar4 * DAT_01ad5010 + DAT_01ad5000);
    }
    local_40 = false;
    uVar4 = FUN_00107550(0);
    if (uVar4 != 0) {
      lVar11 = *(long *)(&DAT_01ad5030 + (ulong)uVar4 * DAT_01ad5010 + DAT_01ad5000);
    }
    iStack_44 = 4;
    local_48 = 0;
    local_40 = 0 < *(short *)(lVar11 + 0x2bd2e);
    local_50 = lVar11;
    if (0 < *(short *)(lVar11 + 0x2bd2e)) {
      do {
        cVar3 = FUN_0100d0a0(&local_50,0,local_68);
        lVar11 = local_60;
        if (cVar3 != '\0') {
          lVar9 = (ulong)(((uint)((int)local_68[0] >> 0xd) >> 0x12 | 0x3ff) &
                         (int)local_68[0] >> 0xd) * 0x40;
          lVar12 = *DAT_01a238a0;
          lVar2 = *(long *)(lVar12 + 0x10 + lVar9);
          uVar7 = (ulong)((local_68[0] & 0x1fff) * *(int *)(lVar12 + 0x30 + lVar9));
          lVar12 = (lVar2 + uVar7) -
                   ((long)*(int *)(lVar12 + 0x34 + lVar9) & *(ulong *)(lVar2 + 8 + uVar7));
          iVar5 = FUN_00123bf0(lVar12 + local_60);
          if (iVar5 == param_1) {
            uVar1 = *(uint *)(lVar12 + lVar11);
            uVar10 = (int)uVar1 >> 0xd;
            lVar2 = *DAT_01a238a0;
            local_69 = 1;
            lVar11 = *(long *)(lVar12 + 8 + lVar11);
            lVar9 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
            lVar12 = *(long *)(lVar2 + 0x10 + lVar9);
            uVar7 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar9));
            lVar12 = (lVar12 + uVar7) -
                     ((long)*(int *)(lVar2 + 0x34 + lVar9) & *(ulong *)(lVar12 + 8 + uVar7));
            *param_2 = *(undefined4 *)(lVar11 + 0x40 + lVar12);
            param_2[1] = *(undefined4 *)(lVar11 + 0x44 + lVar12);
            break;
          }
        }
        local_48 = local_48 + 1;
        if (local_48 < 0) {
          local_40 = false;
          break;
        }
        if (iStack_44 == -1) {
          sVar8 = *(short *)(local_50 + 0x510);
        }
        else {
          sVar8 = *(short *)(local_50 + 0x2bd1e + (long)iStack_44 * 4);
        }
        local_40 = local_48 < sVar8;
      } while (local_48 < sVar8);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_69);
  }
LAB_0010a003:
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

