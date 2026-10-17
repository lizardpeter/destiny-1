
uint FUN_00b92300(undefined8 param_1,long param_2)

{
  char cVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar3 = FUN_00072c70(param_1,2);
  *(undefined4 *)(param_2 + 0x50) = uVar3;
  uVar3 = FUN_00072c70(param_1,2);
  *(undefined4 *)(param_2 + 0x54) = uVar3;
  cVar1 = FUN_00073430(param_1);
  uVar2 = 0xffff;
  if (cVar1 == '\0') {
    uVar2 = FUN_00072c70(param_1,0xb);
  }
  *(undefined2 *)(param_2 + 0x58) = uVar2;
  uVar4 = FUN_002e98b0(param_1,param_2);
  uVar5 = uVar4 & 0xffffff00;
  if ((((char)uVar4 != '\0') && (*(uint *)(param_2 + 0x50) < 3)) && (*(uint *)(param_2 + 0x54) < 3))
  {
    uVar5 = FUN_00072210(param_1);
    uVar5 = uVar5 ^ 1;
  }
  return uVar5;
}

