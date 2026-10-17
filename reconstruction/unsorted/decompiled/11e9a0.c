
ulong FUN_0011e9a0(int param_1)

{
  short sVar1;
  long lVar2;
  long lVar3;
  char cVar4;
  ushort uVar5;
  ulong uVar6;
  long lVar7;
  ulong uVar8;
  uint local_68 [2];
  long local_60;
  long local_50;
  short local_48;
  int iStack_44;
  bool local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_50 = 0;
  uVar5 = FUN_00107550(0);
  local_50 = 0;
  if (uVar5 != 0) {
    local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar5 * DAT_01ad5010 + DAT_01ad5000);
  }
  local_40 = false;
  if (param_1 == -1) {
    uVar6 = 0xffffffff;
  }
  else {
    uVar5 = FUN_00107550(0);
    local_50 = 0;
    if (uVar5 != 0) {
      local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar5 * DAT_01ad5010 + DAT_01ad5000);
    }
    iStack_44 = 0xd;
    local_48 = 0;
    local_40 = 0 < *(short *)(local_50 + 0x2bd52);
    if (0 < *(short *)(local_50 + 0x2bd52)) {
      do {
        cVar4 = FUN_0100d0a0(&local_50,0,local_68);
        if (cVar4 != '\0') {
          uVar6 = (ulong)local_68[0];
          lVar7 = (ulong)(((uint)((int)local_68[0] >> 0xd) >> 0x12 | 0x3ff) &
                         (int)local_68[0] >> 0xd) * 0x40;
          lVar2 = *DAT_01a238a0;
          lVar3 = *(long *)(lVar2 + 0x10 + lVar7);
          uVar8 = (ulong)((local_68[0] & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar7));
          if (*(char *)(local_60 + 0x1ac +
                       ((lVar3 + uVar8) -
                       ((long)*(int *)(lVar2 + 0x34 + lVar7) & *(ulong *)(lVar3 + 8 + uVar8)))) ==
              param_1) goto LAB_0011eb26;
        }
        local_48 = local_48 + 1;
        if (local_48 < 0) {
          local_40 = false;
          break;
        }
        if (iStack_44 == -1) {
          sVar1 = *(short *)(local_50 + 0x510);
        }
        else {
          sVar1 = *(short *)(local_50 + 0x2bd1e + (long)iStack_44 * 4);
        }
        local_40 = local_48 < sVar1;
      } while (local_48 < sVar1);
    }
    uVar6 = 0xffffffff;
  }
LAB_0011eb26:
  if (*DAT_01a1f100 != local_38) {
    uVar6 = thunk_FUN_012aa7f6();
    return uVar6;
  }
  return uVar6;
}

