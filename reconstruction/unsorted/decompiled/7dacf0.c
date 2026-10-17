
undefined8 FUN_007dacf0(undefined4 param_1)

{
  int *piVar1;
  ulong uVar2;
  bool bVar3;
  int *piVar4;
  undefined8 uVar5;
  int *piVar6;
  bool bVar7;
  undefined1 local_49;
  undefined1 local_48 [8];
  undefined4 local_40;
  long local_38;
  
  piVar4 = DAT_026df268;
  local_38 = *DAT_01a1f100;
  uVar2 = *(ulong *)(DAT_026df268 + 0xa000);
  local_49 = 1;
  local_40 = param_1;
  if ((((int)(uVar2 >> 0x20) != (int)uVar2) && (DAT_026df268[(uVar2 & 0xffffffff) * 0x10] == 1)) &&
     (piVar6 = DAT_026df268 + (uVar2 & 0xffffffff) * 0x10, piVar6 != (int *)0x0)) {
    piVar1 = DAT_026df268 + 0x9ff0;
    bVar3 = false;
    do {
      if ((char)piVar6[0xf] == '\0') {
        if (!bVar3) {
          FUN_007db2d0(local_48);
          bVar3 = true;
        }
        FUN_007db340(local_48,piVar6);
      }
      bVar7 = piVar1 == piVar6;
      piVar6 = piVar6 + 0x10;
      if (bVar7) {
        piVar6 = piVar4;
      }
      uVar2 = *(ulong *)(piVar4 + 0xa000);
      if ((uint)(uVar2 >> 0x20) < (uint)uVar2) {
        if ((long)piVar6 - (long)(piVar4 + (uVar2 & 0xffffffff) * 0x10) < 0) goto LAB_007dadd5;
      }
      else {
        if ((long)piVar6 - (long)(piVar4 + (uVar2 & 0xffffffff) * 0x10) < 0) goto LAB_007dadf0;
LAB_007dadd5:
        if (-1 < (long)piVar6 - (long)(piVar4 + (uVar2 >> 0x20) * 0x10)) goto LAB_007dadf0;
      }
      if ((*piVar6 != 1) || (piVar6 == (int *)0x0)) goto LAB_007dadf0;
    } while( true );
  }
LAB_007dae03:
  if (*DAT_01a1f100 != local_38) {
    uVar5 = thunk_FUN_012aa7f6();
    return uVar5;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_49);
LAB_007dadf0:
  if (bVar3) {
    FUN_007db4b0(local_48);
    local_49 = 0;
  }
  goto LAB_007dae03;
}

