
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00b9fac0(void)

{
  char cVar1;
  long lVar2;
  undefined8 uVar3;
  ulong local_1d48 [2];
  undefined1 local_1d38 [4];
  undefined2 local_1d34;
  undefined4 local_a88;
  undefined1 local_80;
  undefined1 local_58;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  if (DAT_028a5410 != '\0') {
    cVar1 = FUN_00906e00();
    if (cVar1 != '\0') {
      lVar2 = FUN_00aeacd0();
      if (*(int *)(lVar2 + 8) != 1) {
        FUN_00bb6080(lVar2);
      }
      cVar1 = FUN_00bb6710(lVar2);
      if (cVar1 != '\0') {
        local_1d34 = 0;
        local_a88 = 0;
        local_80 = 0;
        local_58 = 0;
        local_1d48[0] = local_1d48[0] & 0xffffffffffff0000;
        uVar3 = FUN_00aeacd0();
        thunk_FUN_012aa986(local_1d38,0,0x1d10);
        local_1d48[0] = 0;
        local_1d48[1] = 0;
        FUN_00bb5f00(uVar3,0,local_1d38,local_1d48);
        FUN_00b9fca0(local_1d38,local_1d48);
        uVar3 = FUN_00aeacd0();
        FUN_00bb6440(uVar3,local_1d38,local_1d48);
        _DAT_028a5580 = local_1d38;
        FUN_00b9fd60(local_1d38);
        uVar3 = FUN_00aeacd0();
        if (DAT_028a5427 != '\0') {
          cVar1 = FUN_0093d1a0(local_1d38);
          if ((cVar1 == '\0') && (DAT_028a5427 != '\0')) {
            FUN_00baa1e0();
            FUN_0093c590(s_stopped_recording_0169738f);
            DAT_028a5427 = '\0';
          }
        }
        FUN_00bb65b0(uVar3,local_1d38);
        _DAT_028a5580 = (undefined1 *)0x0;
        FUN_00bb6360(local_1d38);
      }
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

