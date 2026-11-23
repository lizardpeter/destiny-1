
bool FUN_002679e0(undefined8 param_1,undefined8 param_2,undefined4 param_3,byte param_4)

{
  char cVar1;
  byte bVar2;
  undefined1 uVar3;
  long *plVar4;
  long lVar5;
  undefined8 uVar6;
  undefined8 *local_a8 [5];
  char local_80;
  undefined8 *local_70 [5];
  char local_48;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar1 = FUN_0025cc10();
  bVar2 = 0;
  if (cVar1 != '\0') {
    plVar4 = (long *)FUN_0025a550();
    lVar5 = (**(code **)(*plVar4 + 0x328))(plVar4,param_3);
    if (lVar5 != 0) {
      FUN_00263ad0(local_70,lVar5);
      (*(code *)*local_70[0])(local_70);
      cVar1 = '\x01';
      do {
        if (local_48 == '\0') break;
        uVar6 = FUN_00263a60(local_70);
        cVar1 = FUN_0028e560(param_2,uVar6);
        (*(code *)local_70[0][1])(local_70);
      } while (cVar1 != '\0');
      bVar2 = FUN_0028a620(param_1,param_3);
      bVar2 = cVar1 != '\0' & bVar2 | param_4;
      if (bVar2 != 0) {
        FUN_00263b70(local_a8,lVar5);
        (*(code *)*local_a8[0])(local_a8);
        cVar1 = '\x01';
        do {
          if (local_80 == '\0') break;
          uVar6 = FUN_00263a60(local_a8);
          cVar1 = FUN_0028e560(param_2,uVar6);
          (*(code *)local_a8[0][1])(local_a8);
        } while (cVar1 != '\0');
        bVar2 = FUN_0028a620(param_1,param_3);
        bVar2 = cVar1 != '\0' & bVar2 | param_4;
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return bVar2 != 0;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return (bool)uVar3;
}

