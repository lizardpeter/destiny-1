
undefined8 FUN_00109bf0(int param_1)

{
  long lVar1;
  char cVar2;
  ushort uVar3;
  int iVar4;
  undefined8 uVar5;
  ulong uVar6;
  short sVar7;
  long lVar8;
  long lVar9;
  uint local_68 [2];
  long local_60;
  long local_50;
  short local_48;
  int iStack_44;
  bool local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_1 != -1) {
    cVar2 = FUN_002d8470(param_1);
    if (cVar2 != '\0') {
      uVar5 = FUN_002d7250(param_1);
      goto LAB_00109d81;
    }
    local_50 = 0;
    uVar3 = FUN_00107550(0);
    lVar9 = 0;
    local_50 = 0;
    if (uVar3 != 0) {
      local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar3 * DAT_01ad5010 + DAT_01ad5000);
    }
    local_40 = false;
    uVar3 = FUN_00107550(0);
    if (uVar3 != 0) {
      lVar9 = *(long *)(&DAT_01ad5030 + (ulong)uVar3 * DAT_01ad5010 + DAT_01ad5000);
    }
    iStack_44 = 4;
    local_48 = 0;
    local_40 = 0 < *(short *)(lVar9 + 0x2bd2e);
    local_50 = lVar9;
    if (0 < *(short *)(lVar9 + 0x2bd2e)) {
      do {
        cVar2 = FUN_0100d0a0(&local_50,0,local_68);
        if (cVar2 != '\0') {
          lVar8 = (ulong)(((uint)((int)local_68[0] >> 0xd) >> 0x12 | 0x3ff) &
                         (int)local_68[0] >> 0xd) * 0x40;
          lVar9 = *DAT_01a238a0;
          lVar1 = *(long *)(lVar9 + 0x10 + lVar8);
          uVar6 = (ulong)((local_68[0] & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar8));
          iVar4 = FUN_00123bf0(((lVar1 + uVar6) -
                               ((long)*(int *)(lVar9 + 0x34 + lVar8) & *(ulong *)(lVar1 + 8 + uVar6)
                               )) + local_60);
          uVar5 = 1;
          if (iVar4 == param_1) goto LAB_00109d81;
        }
        local_48 = local_48 + 1;
        if (local_48 < 0) {
          local_40 = false;
          break;
        }
        if (iStack_44 == -1) {
          sVar7 = *(short *)(local_50 + 0x510);
        }
        else {
          sVar7 = *(short *)(local_50 + 0x2bd1e + (long)iStack_44 * 4);
        }
        local_40 = local_48 < sVar7;
      } while (local_48 < sVar7);
    }
  }
  uVar5 = 0;
LAB_00109d81:
  if (*DAT_01a1f100 != local_38) {
    uVar5 = thunk_FUN_012aa7f6();
    return uVar5;
  }
  return uVar5;
}

