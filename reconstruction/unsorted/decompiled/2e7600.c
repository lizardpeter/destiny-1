
undefined4
FUN_002e7600(undefined4 *param_1,undefined8 param_2,undefined8 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  undefined8 uVar4;
  
  uVar2 = 0;
  if ((*(byte *)(param_1 + 5) & 1) != 0) {
    uVar2 = *param_1;
    uVar4 = FUN_00170440();
    uVar2 = FUN_000a0350(uVar2,param_2,param_3,param_4,0,uVar4);
    cVar1 = FUN_000a0300(uVar2);
    if (cVar1 == '\0') {
      iVar3 = FUN_000a0270();
      uVar2 = 0xfffffffe;
      if (iVar3 != 0) {
        if (iVar3 == 1) {
          uVar2 = 0xffffffff;
        }
        else {
          uVar2 = 0xfffffffc;
        }
      }
    }
  }
  return uVar2;
}

