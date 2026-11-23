
undefined8 FUN_00a2ddb0(long param_1,undefined4 *param_2)

{
  char cVar1;
  uint uVar2;
  long lVar3;
  undefined8 uVar4;
  long lVar5;
  bool bVar6;
  long local_30;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar2 = FUN_00955260();
  bVar6 = false;
  if (((uVar2 < 3) && ((*(byte *)(param_1 + 0x50) & 2) != 0)) &&
     ((*(byte *)(param_1 + 0x54) & 4) == 0)) {
    lVar3 = FUN_00574ef0();
    if (*(char *)(lVar3 + 300) == '\0') {
      local_30 = 0;
      cVar1 = FUN_007748f0(0,&local_30);
      lVar3 = local_30;
      bVar6 = true;
      if (cVar1 != '\0') {
        lVar5 = local_30 + 0x6c28;
        cVar1 = FUN_00b8f690(lVar5);
        if (cVar1 != '\0') {
          cVar1 = FUN_00b8f690(lVar5);
          lVar5 = 0;
          if (cVar1 != '\0') {
            lVar5 = lVar3 + 0x6d09;
          }
          bVar6 = (*(byte *)(lVar5 + 5) & 1) == 0;
        }
      }
    }
    else if (param_2 != (undefined4 *)0x0) {
      *param_2 = DAT_027755bc;
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar6);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

