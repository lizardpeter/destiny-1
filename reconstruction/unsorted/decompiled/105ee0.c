
void FUN_00105ee0(int param_1)

{
  long lVar1;
  char cVar2;
  ushort uVar3;
  ulong uVar4;
  short sVar5;
  long lVar6;
  long lVar7;
  uint local_68 [2];
  long local_60;
  long local_50;
  short local_48;
  int iStack_44;
  bool local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_50 = 0;
  uVar3 = FUN_00107550(0);
  lVar6 = 0;
  local_50 = 0;
  if (uVar3 != 0) {
    local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar3 * DAT_01ad5010 + DAT_01ad5000);
  }
  local_40 = false;
  uVar3 = FUN_00107550(0);
  if (uVar3 != 0) {
    lVar6 = *(long *)(&DAT_01ad5030 + (ulong)uVar3 * DAT_01ad5010 + DAT_01ad5000);
  }
  iStack_44 = 1;
  local_48 = 0;
  local_40 = 0 < *(short *)(lVar6 + 0x2bd22);
  local_50 = lVar6;
  if (0 < *(short *)(lVar6 + 0x2bd22)) {
    do {
      cVar2 = FUN_0100d0a0(&local_50,0,local_68);
      if (cVar2 != '\0') {
        lVar7 = (ulong)(((uint)((int)local_68[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_68[0] >> 0xd)
                * 0x40;
        lVar6 = *DAT_01a238a0;
        lVar1 = *(long *)(lVar6 + 0x10 + lVar7);
        uVar4 = (ulong)((local_68[0] & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar7));
        lVar6 = (lVar1 + uVar4) -
                ((long)*(int *)(lVar6 + 0x34 + lVar7) & *(ulong *)(lVar1 + 8 + uVar4));
        if (*(int *)(local_60 + 0x274 + lVar6) == param_1) {
          *(undefined4 *)(lVar6 + 0x274 + local_60) = 0xffffffff;
        }
      }
      local_48 = local_48 + 1;
      if (local_48 < 0) {
        local_40 = false;
        break;
      }
      if (iStack_44 == -1) {
        sVar5 = *(short *)(local_50 + 0x510);
      }
      else {
        sVar5 = *(short *)(local_50 + 0x2bd1e + (long)iStack_44 * 4);
      }
      local_40 = local_48 < sVar5;
    } while (local_48 < sVar5);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

