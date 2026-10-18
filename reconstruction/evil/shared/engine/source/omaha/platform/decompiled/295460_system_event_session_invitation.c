
/* WARNING: Removing unreachable block (ram,0x00295528) */
/* WARNING: Removing unreachable block (ram,0x002955b8) */
/* WARNING: Removing unreachable block (ram,0x002955d8) */

void FUN_00295460(void)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  undefined8 uVar6;
  ulong uVar7;
  char local_20d1;
  undefined1 local_20d0 [8];
  int local_20c8;
  undefined1 local_20c4 [8196];
  int local_c0 [34];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  thunk_FUN_012ab6f6();
  thunk_FUN_012aabf6(local_c0);
  if (0 < local_c0[0]) {
    iVar4 = 0;
    do {
      thunk_FUN_012ab706(&local_20c8);
      if (local_20c8 == 0x10000000) {
        FUN_00067090(0x10);
      }
      else if (local_20c8 == 0x20001000) {
        FUN_00067090(0x11);
        FUN_00067550();
      }
      else if (local_20c8 == 0x10000002) {
        thunk_FUN_012aa7c6(&DAT_026535d4,local_20c4,0x8c);
        LOCK();
        DAT_02653590 = 1;
        UNLOCK();
      }
      iVar4 = iVar4 + 1;
    } while (iVar4 < local_c0[0]);
  }
  uVar7 = 0;
  if ((DAT_02653580 != 0) && (DAT_0265357c != 0)) {
    FUN_002e82f0(&local_20d1);
    if (local_20d1 == '\0') {
      uVar6 = 0x20;
    }
    else {
      uVar6 = 0x1f;
    }
    FUN_002949c0(uVar6);
    LOCK();
    DAT_02653580 = 0;
    UNLOCK();
    LOCK();
    DAT_0265357c = 0;
    UNLOCK();
  }
  do {
    piVar1 = &DAT_02653500 + uVar7;
    do {
      iVar2 = *piVar1;
      LOCK();
      iVar4 = *piVar1;
      if (iVar2 == iVar4) {
        *piVar1 = 0;
        iVar4 = iVar2;
      }
      UNLOCK();
    } while (iVar2 != iVar4);
    if ((iVar2 != 0) && ((uint)uVar7 < 0x33)) {
      if ((0x48eb980c01040U >> (uVar7 & 0x3f) & 1) == 0) {
        if (((0xc0000UL >> (uVar7 & 0x3f) & 1) != 0) && (iVar4 = FUN_002449b0(), iVar4 != 0)) {
          uVar5 = 0;
          do {
            FUN_002449c0(uVar5,local_20d0);
            FUN_00294a00(uVar7 & 0xffffffff);
            uVar5 = uVar5 + 1;
            uVar3 = FUN_002449b0();
          } while (uVar5 < uVar3);
        }
      }
      else {
        FUN_002949c0(uVar7 & 0xffffffff);
      }
    }
    uVar7 = uVar7 + 1;
  } while ((int)uVar7 != 0x34);
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

