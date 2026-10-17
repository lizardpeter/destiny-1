
undefined1 FUN_00b90000(long param_1,byte param_2,int param_3,int param_4,undefined8 *param_5)

{
  byte bVar1;
  bool bVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  
  iVar4 = param_3;
  if (*(char *)(param_1 + 0xfc) != '\0') {
    iVar4 = *(int *)(param_1 + 0xe4);
  }
  cVar3 = FUN_00b8f6c0(param_1);
  if (cVar3 == '\0') {
    cVar3 = FUN_00b8f710(param_1);
    if (cVar3 == '\0') {
      return 0;
    }
    *(undefined4 *)(param_1 + 0x118) = 0;
    *(undefined8 *)(param_1 + 0x110) = 0;
    *(undefined8 *)(param_1 + 0x108) = 0;
    *(undefined8 *)(param_1 + 0x100) = 0;
    *(byte *)(param_1 + 0x118) = param_2;
    *(int *)(param_1 + 0x100) = iVar4;
    *(int *)(param_1 + 0x104) = param_3;
    *(int *)(param_1 + 0x108) = param_4;
    *(undefined4 *)(param_1 + 0x10c) = 0xffffffff;
    if (param_5 != (undefined8 *)0x0) {
      *(undefined8 *)(param_1 + 0x110) = *param_5;
    }
    cVar3 = FUN_00b8f690(param_1);
    if ((cVar3 != '\0') &&
       (iVar4 = thunk_FUN_012aa826((int *)(param_1 + 0xe4),(undefined8 *)(param_1 + 0x100),0x1c),
       iVar4 == 0)) {
      return 1;
    }
    FUN_00b8f930(param_1);
    return 1;
  }
  iVar5 = *(int *)(param_1 + 0xec);
  bVar2 = false;
  if (iVar5 == 0) {
LAB_00b90083:
    iVar5 = 0;
  }
  else if (param_3 < *(int *)(param_1 + 0xf0)) {
    *(undefined4 *)(param_1 + 0xec) = 0;
    *(undefined4 *)(param_1 + 0xf0) = 0xffffffff;
    *(undefined8 *)(param_1 + 0xf4) = 0;
    bVar2 = true;
    goto LAB_00b90083;
  }
  bVar1 = *(byte *)(param_1 + 0xfc);
  if ((((bVar1 == param_2) && (*(int *)(param_1 + 0xe4) == iVar4)) &&
      (*(int *)(param_1 + 0xe8) == param_3)) && (iVar5 == param_4)) {
    if (!bVar2) goto LAB_00b901fc;
  }
  else {
    *(byte *)(param_1 + 0xfc) = param_2;
    *(int *)(param_1 + 0xe4) = iVar4;
    *(int *)(param_1 + 0xe8) = param_3;
    if ((bVar1 != 0 & param_4 != 0 & param_2) == 0) {
      *(undefined4 *)(param_1 + 0xec) = 0;
      *(undefined4 *)(param_1 + 0xf0) = 0xffffffff;
      *(undefined8 *)(param_1 + 0xf4) = 0;
    }
    else {
      *(int *)(param_1 + 0xec) = param_4;
      *(int *)(param_1 + 0xf0) = param_3;
      if (param_4 == 1) {
        *(undefined8 *)(param_1 + 0xf4) = *param_5;
      }
      else {
        *(undefined8 *)(param_1 + 0xf4) = 0;
      }
    }
  }
  FUN_00b8f880(param_1);
LAB_00b901fc:
  cVar3 = FUN_00b8f690(param_1);
  if (cVar3 == '\0') {
    FUN_00b8f880(param_1);
  }
  return 1;
}

