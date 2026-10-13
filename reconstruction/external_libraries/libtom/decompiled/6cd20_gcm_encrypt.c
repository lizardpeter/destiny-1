
undefined8
FUN_0006cd20(long param_1,undefined8 param_2,int param_3,undefined8 param_4,int param_5,
            undefined8 param_6)

{
  char *pcVar1;
  int iVar2;
  ulong uVar3;
  undefined8 uVar4;
  undefined1 uVar5;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_40 = 0x10;
  iVar2 = FUN_00f69890(*(undefined8 *)(param_1 + 8));
  uVar5 = 0;
  if (iVar2 == 0) {
    iVar2 = FUN_00f68bd0(*(undefined8 *)(param_1 + 8),param_1 + 0x12,0xc);
    if (iVar2 == 0) {
      iVar2 = FUN_00f68830(*(undefined8 *)(param_1 + 8),0,0);
      if (iVar2 == 0) {
        iVar2 = FUN_00f693d0(*(undefined8 *)(param_1 + 8),param_2,(long)param_3,param_2,0);
        if (iVar2 == 0) {
          iVar2 = FUN_00f693d0(*(undefined8 *)(param_1 + 8),param_4,(long)param_5,param_4,0);
          if (iVar2 == 0) {
            iVar2 = FUN_00f68e30(*(undefined8 *)(param_1 + 8),param_6,&local_40);
            if (iVar2 == 0) {
              uVar3 = 0;
              uVar5 = 1;
              do {
                if (0xb < uVar3) break;
                pcVar1 = (char *)(param_1 + 0x12 + uVar3);
                *pcVar1 = *pcVar1 + '\x01';
                uVar3 = uVar3 + 1;
              } while (*pcVar1 == '\0');
            }
          }
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar5);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

