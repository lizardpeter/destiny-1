
void FUN_0010f870(int *param_1)

{
  int iVar1;
  int iVar2;
  char cVar3;
  ushort uVar4;
  ulong uVar5;
  int *piVar6;
  short sVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  int iVar11;
  uint local_68 [2];
  long local_60;
  long local_50;
  short local_48;
  int iStack_44;
  bool local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_50 = 0;
  uVar4 = FUN_00107550(0);
  lVar9 = 0;
  local_50 = 0;
  if (uVar4 != 0) {
    local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar4 * DAT_01ad5010 + DAT_01ad5000);
  }
  local_40 = false;
  uVar4 = FUN_00107550(0);
  if (uVar4 != 0) {
    lVar9 = *(long *)(&DAT_01ad5030 + (ulong)uVar4 * DAT_01ad5010 + DAT_01ad5000);
  }
  iStack_44 = 0x12;
  local_48 = 0;
  local_40 = 0 < *(short *)(lVar9 + 0x2bd66);
  local_50 = lVar9;
  if (0 < *(short *)(lVar9 + 0x2bd66)) {
    do {
      cVar3 = FUN_0100d0a0(&local_50,0,local_68);
      if (cVar3 != '\0') {
        lVar8 = (ulong)(((uint)((int)local_68[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_68[0] >> 0xd)
                * 0x40;
        lVar9 = *DAT_01a238a0;
        lVar10 = *(long *)(lVar9 + 0x10 + lVar8);
        uVar5 = (ulong)((local_68[0] & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar8));
        piVar6 = (int *)FUN_0012a400(((lVar10 + uVar5) -
                                     ((long)*(int *)(lVar9 + 0x34 + lVar8) &
                                     *(ulong *)(lVar10 + 8 + uVar5))) + local_60);
        lVar9 = 0;
        iVar11 = *piVar6;
        if (0 < iVar11) {
          do {
            iVar1 = piVar6[lVar9 + 1];
            iVar2 = *param_1;
            lVar10 = 0;
            do {
              if (iVar2 <= (int)lVar10) {
                if (iVar2 == 0x20) goto LAB_0010f9ec;
                *param_1 = iVar2 + 1;
                param_1[(long)iVar2 + 1] = iVar1;
                iVar11 = *piVar6;
                break;
              }
              lVar8 = lVar10 + 1;
              lVar10 = lVar10 + 1;
            } while (param_1[lVar8] != iVar1);
            lVar9 = lVar9 + 1;
          } while ((int)lVar9 < iVar11);
        }
LAB_0010f9ec:
        iVar11 = piVar6[0x21];
        lVar9 = 0;
        if (0 < iVar11) {
          do {
            iVar1 = piVar6[lVar9 + 0x22];
            iVar2 = param_1[0x21];
            lVar10 = 0;
            do {
              if (iVar2 <= (int)lVar10) {
                if (iVar2 == 0x20) goto LAB_0010fa60;
                param_1[0x21] = iVar2 + 1;
                param_1[(long)iVar2 + 0x22] = iVar1;
                iVar11 = piVar6[0x21];
                break;
              }
              lVar8 = lVar10 + 0x22;
              lVar10 = lVar10 + 1;
            } while (param_1[lVar8] != iVar1);
            lVar9 = lVar9 + 1;
          } while ((int)lVar9 < iVar11);
        }
      }
LAB_0010fa60:
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
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

