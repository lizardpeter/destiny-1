
undefined8 FUN_0008a040(byte param_1)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  undefined1 local_128 [12];
  undefined4 local_11c;
  uint local_118 [30];
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 uStack_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 local_60;
  undefined8 uStack_58;
  undefined8 uStack_50;
  undefined8 uStack_48;
  long local_30;
  
  local_30 = *DAT_01a1f100;
  thunk_FUN_012aa836(0xb4);
  local_60 = 0;
  uStack_58 = 0;
  uStack_50 = 0;
  uStack_48 = 0;
  local_a0 = 0;
  uStack_98 = 0;
  uStack_90 = 0;
  uStack_88 = 0;
  local_80 = 0;
  thunk_FUN_012aadf6(&local_60,&local_a0);
  iVar2 = thunk_FUN_012aac46(&local_11c);
  if (iVar2 == -0x7f69fffe) {
    thunk_FUN_012aac56(0);
    thunk_FUN_012aac46(&local_11c);
  }
  thunk_FUN_012aae06();
  iVar2 = thunk_FUN_012aae16(local_11c,0,0,0);
  if (-1 < iVar2) {
    while (iVar3 = thunk_FUN_012aae26(iVar2,local_118,1), iVar3 != 1) {
      if (iVar3 != 0) goto LAB_0008a12c;
      FUN_000f7690(1);
    }
    bVar1 = 1;
    if ((local_118[0] & 0x4010) != 0x4010) {
LAB_0008a12c:
      bVar1 = param_1;
    }
    param_1 = bVar1;
    thunk_FUN_012aae36(iVar2);
  }
  FUN_0008a1a0(param_1 & 1);
  FUN_00065030(&DAT_01ac6240,s__download0_01610046,0x10);
  thunk_FUN_012aae46(&DAT_01ac6240,local_128);
  if (*DAT_01a1f100 != local_30) {
    uVar4 = thunk_FUN_012aa7f6();
    return uVar4;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
}

