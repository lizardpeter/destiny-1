
void FUN_007de800(long param_1,undefined4 *param_2)

{
  long lVar1;
  undefined8 uVar2;
  undefined4 uVar3;
  undefined4 *puVar4;
  
  if (*(undefined4 **)(param_1 + 0x1d28) != param_2) {
    if (param_2 == (undefined4 *)0x0) {
      lVar1 = *(long *)(param_1 + 0x50);
      puVar4 = (undefined4 *)0x0;
      uVar3 = 0;
      uVar2 = 0;
    }
    else {
      lVar1 = *(long *)(param_1 + 0x50);
      uVar2 = *(undefined8 *)(param_2 + 2);
      uVar3 = *param_2;
      puVar4 = param_2 + 5;
    }
    FUN_00f8b790(lVar1 + 0xc0,puVar4,uVar3,uVar2);
    *(undefined4 **)(param_1 + 0x1d28) = param_2;
  }
  return;
}

