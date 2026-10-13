
undefined8
FUN_0006ce20(long param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,
            undefined8 param_5)

{
  char *pcVar1;
  int iVar2;
  undefined8 uVar3;
  ulong uVar4;
  long local_50;
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_50 = 0x10;
  iVar2 = FUN_00f69890(*(undefined8 *)(param_1 + 8));
  if ((((iVar2 == 0) &&
       (iVar2 = FUN_00f68bd0(*(undefined8 *)(param_1 + 8),param_1 + 0x1e,0xc), iVar2 == 0)) &&
      (iVar2 = FUN_00f68830(*(undefined8 *)(param_1 + 8),0,0), iVar2 == 0)) &&
     (((iVar2 = FUN_00f693d0(*(undefined8 *)(param_1 + 8),param_4,(long)(int)param_3,param_2,1),
       iVar2 == 0 &&
       (iVar2 = FUN_00f68e30(*(undefined8 *)(param_1 + 8),local_48,&local_50), iVar2 == 0)) &&
      ((local_50 == 0x10 && (iVar2 = thunk_FUN_012aa826(param_5,local_48,0x10), iVar2 == 0)))))) {
    uVar4 = 0;
    uVar3 = 1;
    do {
      if (0xb < uVar4) break;
      pcVar1 = (char *)(param_1 + 0x1e + uVar4);
      *pcVar1 = *pcVar1 + '\x01';
      uVar4 = uVar4 + 1;
    } while (*pcVar1 == '\0');
  }
  else {
    FUN_00f6c140(param_4,param_3);
    uVar3 = 0;
  }
  if (*DAT_01a1f100 != local_38) {
    uVar3 = thunk_FUN_012aa7f6();
    return uVar3;
  }
  return uVar3;
}

