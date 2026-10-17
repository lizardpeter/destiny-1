
void FUN_0079f310(long param_1)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  ulong uVar4;
  byte *pbVar5;
  undefined8 uVar6;
  undefined4 local_1c4;
  undefined4 local_1c0;
  undefined4 local_1bc;
  undefined1 local_1b8 [256];
  long local_b8;
  undefined1 local_b0 [8];
  undefined1 local_a8 [8];
  undefined1 local_a0 [8];
  undefined1 local_98 [8];
  undefined1 local_90 [8];
  undefined1 local_88 [8];
  undefined8 local_80 [6];
  undefined1 local_50 [8];
  undefined1 local_48 [8];
  undefined1 local_40 [8];
  undefined1 local_38 [8];
  undefined1 local_30 [8];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  FUN_00244ee0(&local_b8);
  local_1b8[0] = 0;
  cVar1 = FUN_002e41f0();
  if (cVar1 != '\0') {
    cVar1 = FUN_00771be0(4);
    if (cVar1 != '\0') {
      FUN_00771b10(4);
      FUN_00771ac0(5);
    }
  }
  if (*(char *)(param_1 + 0x4e) != '\0') {
    cVar1 = FUN_00771be0(6);
    if (cVar1 != '\0') {
      FUN_00771b10(6);
      FUN_00771ac0(7);
    }
  }
  cVar1 = FUN_002e41f0();
  if (cVar1 != '\0') {
    cVar1 = FUN_00244ee0(local_80);
    if (cVar1 != '\0') {
      cVar1 = FUN_002459f0();
      if (cVar1 == '\0') {
        cVar1 = FUN_00244ee0(local_a8);
        if (cVar1 != '\0') {
          cVar1 = FUN_00244f90(local_a8);
          if (cVar1 != '\0') {
            cVar1 = FUN_00244ee0(local_a0);
            if (cVar1 != '\0') {
              cVar1 = FUN_00245210(local_a0);
              if (cVar1 != '\0') goto LAB_0079f605;
            }
            cVar1 = FUN_00244ee0(local_98);
            if (cVar1 != '\0') {
              uVar4 = FUN_00245170(local_98);
              if ((uVar4 & 0x2000000) != 0) goto LAB_0079f605;
            }
            cVar1 = FUN_00244ee0(local_90);
            if (cVar1 != '\0') {
              uVar4 = FUN_00245170(local_90);
              if ((uVar4 & 0x1000000) != 0) {
                cVar1 = FUN_00244ee0(local_88);
                if (cVar1 != '\0') {
                  local_1c0 = 0;
                  cVar1 = FUN_00245610(local_88,&local_1c0);
                  if (cVar1 != '\0') goto LAB_0079f605;
                }
                cVar1 = FUN_00245880(&local_b8);
                if (cVar1 != '\0') {
                  local_80[0] = 0;
                  if (local_b8 != 0) {
                    uVar2 = FUN_00244e40();
                    pbVar5 = (byte *)FUN_00945950(0);
                    cVar1 = FUN_009459f0(pbVar5);
                    if (((cVar1 != '\0') || ((*pbVar5 & 2) != 0)) && (*(int *)(pbVar5 + 4) != -1)) {
                      FUN_00b28670();
                    }
                    FUN_00946100(pbVar5);
                    pbVar5 = (byte *)FUN_00945950(1);
                    cVar1 = FUN_009459f0(pbVar5);
                    if (((cVar1 != '\0') || ((*pbVar5 & 2) != 0)) && (*(int *)(pbVar5 + 4) != -1)) {
                      FUN_00b28670();
                    }
                    FUN_00946100(pbVar5);
                    pbVar5 = (byte *)FUN_00945950(2);
                    cVar1 = FUN_009459f0(pbVar5);
                    if (((cVar1 != '\0') || ((*pbVar5 & 2) != 0)) && (*(int *)(pbVar5 + 4) != -1)) {
                      FUN_00b28670();
                    }
                    FUN_00946100(pbVar5);
                    pbVar5 = (byte *)FUN_00945950(3);
                    cVar1 = FUN_009459f0(pbVar5);
                    if (((cVar1 != '\0') || ((*pbVar5 & 2) != 0)) && (*(int *)(pbVar5 + 4) != -1)) {
                      FUN_00b28670();
                    }
                    FUN_00946100(pbVar5);
                    uVar6 = FUN_00945950(uVar2);
                    uVar2 = FUN_00946110(uVar6);
                    FUN_00b28490(uVar2,&local_b8);
                    FUN_002447a0(&local_b8,local_80);
                    FUN_00b289f0(uVar2,local_80,1,1,0,1,1);
                    FUN_00245b10(&local_b8,1);
                    FUN_00245b90(&local_b8);
                    FUN_00783ed0(6);
                  }
                  goto LAB_0079f82b;
                }
              }
            }
          }
        }
      }
    }
  }
LAB_0079f605:
  cVar1 = FUN_002e4200();
  if (cVar1 == '\0') {
    cVar1 = FUN_002e41f0();
    if (cVar1 == '\0') goto LAB_0079f82b;
    cVar1 = FUN_00244ee0(local_50);
    if (cVar1 != '\0') {
      cVar1 = FUN_00245210(local_50);
      if (cVar1 != '\0') {
        uVar6 = 0x8d;
        goto LAB_0079f618;
      }
    }
    cVar1 = FUN_002451f0(local_1b8);
    if (cVar1 == '\0') goto LAB_0079f82b;
    uVar3 = FUN_00245170(&local_b8);
    FUN_00788e10(5);
    cVar1 = FUN_00771be0(5);
    if (cVar1 != '\0') {
      FUN_00771b10(5);
      FUN_00771ac0(6);
    }
    cVar1 = FUN_00244ee0(local_80);
    if (cVar1 != '\0') {
      cVar1 = FUN_002459f0();
      if (cVar1 == '\0') {
        cVar1 = FUN_00244ee0(local_48);
        if (cVar1 != '\0') {
          cVar1 = FUN_00244f90(local_48);
          if ((cVar1 != '\0') && ((uVar3 & 0x1000000) == 0)) {
            if (*(char *)(param_1 + 0x51) == '\0') {
              cVar1 = FUN_00245a90(&local_b8);
              if (cVar1 == '\0') {
                FUN_00245b90(&local_b8);
                FUN_00245a10(&local_b8);
                *(undefined1 *)(param_1 + 0x51) = 1;
              }
            }
            goto LAB_0079f82b;
          }
        }
        cVar1 = FUN_00244ee0(local_40);
        if (cVar1 == '\0') {
LAB_0079f73f:
          cVar1 = FUN_00244ee0(local_38);
          if (cVar1 == '\0') goto LAB_0079f759;
          cVar1 = FUN_00244f90(local_38);
          if (cVar1 == '\0') goto LAB_0079f759;
LAB_0079f760:
          cVar1 = FUN_00244ee0(local_b0);
          if (cVar1 != '\0') {
            local_1c4 = 0;
            cVar1 = FUN_00245610(local_b0,&local_1c4);
            if (cVar1 != '\0') goto LAB_0079f7df;
          }
          cVar1 = FUN_00245880(&local_b8);
          if (cVar1 != '\0') goto LAB_0079f82b;
          uVar6 = 0x8b;
        }
        else {
          uVar4 = FUN_00245170(local_40);
          if ((uVar4 & 0x2000000) == 0) goto LAB_0079f73f;
LAB_0079f759:
          if (*(int *)(param_1 + 0x40) != 0) goto LAB_0079f760;
          cVar1 = FUN_00244ee0(local_30);
          if (cVar1 == '\0') {
LAB_0079f7ee:
            FUN_0079f850(param_1);
            goto LAB_0079f82b;
          }
          local_1bc = 0;
          cVar1 = FUN_00245610(local_30,&local_1bc);
          if (cVar1 == '\0') goto LAB_0079f7ee;
LAB_0079f7df:
          uVar6 = 0x8c;
        }
        goto LAB_0079f618;
      }
    }
    if (*(char *)(param_1 + 0x4c) == '\0') {
      *(undefined1 *)(param_1 + 0x4c) = 1;
      *(undefined1 *)(param_1 + 0x4e) = 1;
      FUN_002459e0(0);
    }
    if (*(char *)(param_1 + 0x4e) == '\0') goto LAB_0079f82b;
    cVar1 = FUN_00244ee0(local_80);
    if (cVar1 != '\0') goto LAB_0079f82b;
    uVar6 = 0x85;
  }
  else {
    uVar6 = 0x90;
  }
LAB_0079f618:
  FUN_00784e50(0x19,uVar6);
LAB_0079f82b:
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

