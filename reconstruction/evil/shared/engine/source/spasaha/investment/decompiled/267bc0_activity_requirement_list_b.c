
undefined8 FUN_00267bc0(undefined8 param_1,undefined8 param_2,undefined4 param_3,byte param_4)

{
  char cVar1;
  byte bVar2;
  long *plVar3;
  long lVar4;
  undefined8 uVar5;
  undefined8 *local_70 [5];
  char local_48;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar1 = FUN_0025cc10();
  bVar2 = 0;
  if (cVar1 != '\0') {
    plVar3 = (long *)FUN_0025a550();
    lVar4 = (**(code **)(*plVar3 + 0x328))(plVar3,param_3);
    if (lVar4 != 0) {
      FUN_00263b70(local_70,lVar4);
      (*(code *)*local_70[0])(local_70);
      cVar1 = '\x01';
      do {
        if (local_48 == '\0') break;
        uVar5 = FUN_00263a60(local_70);
        cVar1 = FUN_0028e560(param_2,uVar5);
        (*(code *)local_70[0][1])(local_70);
      } while (cVar1 != '\0');
      bVar2 = FUN_0028a620(param_1,param_3);
      bVar2 = cVar1 != '\0' & bVar2 | param_4;
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar2);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

