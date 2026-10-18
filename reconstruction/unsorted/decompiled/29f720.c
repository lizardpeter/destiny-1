
void FUN_0029f720(void)

{
  undefined8 uVar1;
  int *piVar2;
  char cVar3;
  ushort uVar4;
  undefined4 uVar5;
  long lVar6;
  short sVar7;
  ulong uVar8;
  int iVar9;
  ulong uVar10;
  uint uVar11;
  long lVar12;
  undefined1 local_a8 [24];
  undefined1 local_90 [24];
  uint local_78 [2];
  long local_70;
  int local_68;
  uint uStack_64;
  undefined8 *local_60;
  long *local_58;
  long local_50;
  short local_48;
  uint uStack_44;
  bool local_40;
  long local_38;
  
  piVar2 = DAT_02655630;
  local_38 = *DAT_01a1f100;
  local_50 = 0;
  uVar4 = FUN_00107550(0);
  local_50 = 0;
  if (uVar4 != 0) {
    local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar4 * DAT_01ad5010 + DAT_01ad5000);
  }
  local_40 = false;
  FUN_00105a50();
  uVar1 = *(undefined8 *)(DAT_026556d0[1] + 0x10);
  uVar5 = FUN_0006f140(&DAT_026556d0);
  FUN_0008f550(local_78,uVar1,uVar5);
  local_60 = &DAT_026556d0;
  local_58 = DAT_026556d0;
  uVar8 = CONCAT44(uStack_64,local_68);
  if (local_68 <= (int)local_78[0]) {
LAB_0029f8af:
    iVar9 = 0;
    lVar12 = 1;
    do {
      uVar11 = (uint)lVar12;
      if (((uint)piVar2[(long)((int)uVar11 >> 5) + 1] >> (uVar11 & 0x1f) & 1) != 0) {
        uVar4 = FUN_00107550(0);
        local_50 = 0;
        if (uVar4 != 0) {
          local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar4 * DAT_01ad5010 + DAT_01ad5000);
        }
        local_48 = 0;
        sVar7 = *(short *)(local_50 + 0x2bd1e + lVar12 * 4);
        local_40 = 0 < sVar7;
        uStack_44 = uVar11;
        if (0 < sVar7) {
          do {
            iVar9 = iVar9 + 1;
            if (iVar9 % 3 == *piVar2) {
              if (uVar11 == 0x3a ||
                  (uVar11 == 0x39 || (uVar11 == 0x2c || (uVar11 - 0x29 < 2 || uVar11 == 0x2d)))) {
                lVar6 = FUN_0100cef0();
                if (lVar6 != 0) {
                  FUN_00108a90(lVar6);
                  cVar3 = FUN_00001f70();
joined_r0x0029fa8f:
                  if (cVar3 != '\0') {
                    FUN_00352e30();
                  }
                  FUN_000f8210();
                }
              }
              else {
                cVar3 = FUN_0100d0a0(&local_50,0,local_90);
                if (cVar3 != '\0') {
                  cVar3 = FUN_00001f70();
                  goto joined_r0x0029fa8f;
                }
              }
            }
            local_48 = local_48 + 1;
            if (local_48 < 0) {
              local_40 = false;
              break;
            }
            if (uStack_44 == 0xffffffff) {
              sVar7 = *(short *)(local_50 + 0x510);
            }
            else {
              sVar7 = *(short *)(local_50 + 0x2bd1e + (long)(int)uStack_44 * 4);
            }
            local_40 = local_48 < sVar7;
          } while (local_48 < sVar7);
        }
      }
      lVar12 = lVar12 + 1;
    } while ((int)lVar12 != 0x40);
    lVar12 = 1;
    do {
      uVar11 = (uint)lVar12;
      if (((uint)piVar2[(long)((int)uVar11 >> 5) + 3] >> (uVar11 & 0x1f) & 1) != 0) {
        uVar4 = FUN_00107550(0);
        local_50 = 0;
        if (uVar4 != 0) {
          local_50 = *(long *)(&DAT_01ad5030 + (ulong)uVar4 * DAT_01ad5010 + DAT_01ad5000);
        }
        local_48 = 0;
        sVar7 = *(short *)(local_50 + 0x2bd1e + lVar12 * 4);
        local_40 = 0 < sVar7;
        uStack_44 = uVar11;
        if (0 < sVar7) {
          if ((((uVar11 - 0x29 < 2) || (uVar11 == 0x2d)) || (uVar11 == 0x2c)) ||
             ((uVar11 == 0x39 || (uVar11 == 0x3a)))) {
            do {
              iVar9 = iVar9 + 1;
              if ((iVar9 % 3 == *piVar2) && (lVar6 = FUN_0100cef0(), lVar6 != 0)) {
                FUN_00108a90(lVar6);
                cVar3 = FUN_00001f70();
                if (cVar3 != '\0') {
                  FUN_00352e30();
                }
                FUN_000f8210();
              }
              local_48 = local_48 + 1;
              if (local_48 < 0) {
                local_40 = false;
                break;
              }
              if (uStack_44 == 0xffffffff) {
                sVar7 = *(short *)(local_50 + 0x510);
              }
              else {
                sVar7 = *(short *)(local_50 + 0x2bd1e + (long)(int)uStack_44 * 4);
              }
              local_40 = local_48 < sVar7;
            } while (local_48 < sVar7);
          }
          else {
            do {
              iVar9 = iVar9 + 1;
              if ((iVar9 % 3 == *piVar2) &&
                 (cVar3 = FUN_0100d0a0(&local_50,0,local_a8), cVar3 != '\0')) {
                cVar3 = FUN_00001f70();
                if (cVar3 != '\0') {
                  FUN_00352e30();
                }
                FUN_000f8210();
              }
              local_48 = local_48 + 1;
              if (local_48 < 0) {
                local_40 = false;
                break;
              }
              if (uStack_44 == 0xffffffff) {
                sVar7 = *(short *)(local_50 + 0x510);
              }
              else {
                sVar7 = *(short *)(local_50 + 0x2bd1e + (long)(int)uStack_44 * 4);
              }
              local_40 = local_48 < sVar7;
            } while (local_48 < sVar7);
          }
        }
      }
      lVar12 = lVar12 + 1;
      if ((int)lVar12 == 0x40) {
        *piVar2 = *piVar2 + 1 + ((*piVar2 + 1) / 3) * -3;
        if (*DAT_01a1f100 == local_38) {
          return;
        }
        thunk_FUN_012aa7f6();
        return;
      }
    } while( true );
  }
LAB_0029f7e8:
  uVar10 = (ulong)((local_78[0] & 0xffff) * (int)local_58[2]);
  iVar9 = (int)uVar8;
  if (*(char *)(uVar10 + 0x1c + *local_58) != '\0') {
    thunk_FUN_002a1440(*local_58 + uVar10);
    uVar8 = CONCAT44(uStack_64,local_68);
    iVar9 = local_68;
  }
  uVar8 = uVar8 >> 0x20;
  uVar11 = local_78[0];
LAB_0029f810:
  do {
    local_78[0] = uVar11 + 1;
    if ((int)local_78[0] < iVar9) {
      uVar8 = uVar8 >> 1;
      uStack_64 = (uint)uVar8;
      if (uStack_64 == 0) {
        local_78[0] = uVar11 + 0x20 & 0xffffffe0;
        if (iVar9 <= (int)local_78[0]) {
LAB_0029f87e:
          uVar8 = 0;
          goto LAB_0029f880;
        }
        uStack_64 = *(uint *)(local_70 + (long)((int)(uVar11 + 0x20) >> 5) * 4);
        while (uVar8 = (ulong)uStack_64, uStack_64 == 0) {
          local_78[0] = local_78[0] + 0x20;
          if (iVar9 <= (int)local_78[0]) goto LAB_0029f87e;
          uStack_64 = *(uint *)(local_70 + (long)((int)local_78[0] >> 5) * 4);
        }
      }
      uVar11 = local_78[0];
      if ((uVar8 & 1) == 0) goto LAB_0029f810;
    }
LAB_0029f880:
    if ((iVar9 <= (int)local_78[0]) ||
       (uVar11 = local_78[0],
       (*(uint *)(*(long *)(local_58[1] + 0x10) + (ulong)(local_78[0] >> 5 & 0x7ff) * 4) >>
        (local_78[0] & 0x1f) & 1) != 0)) break;
  } while( true );
  uVar8 = CONCAT44(uStack_64,local_68);
  if (local_68 <= (int)local_78[0]) goto LAB_0029f8af;
  goto LAB_0029f7e8;
}

