
void FUN_007e1510(long param_1,undefined *param_2)

{
  undefined8 *puVar1;
  int iVar2;
  int iVar3;
  undefined8 *puVar4;
  
  puVar1 = (undefined8 *)(&DAT_00001e78 + param_1);
  iVar3 = 0;
  do {
    iVar2 = 0;
    puVar4 = puVar1;
    do {
      if (((undefined *)*puVar4 == param_2) && ((undefined *)*puVar4 != &DAT_026df2b4)) {
        FUN_00f84710(&DAT_026df2b4);
        FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,iVar3,iVar2,1,&DAT_026df2b4);
        *puVar4 = &DAT_026df2b4;
      }
      puVar4 = puVar4 + 1;
      iVar2 = iVar2 + 1;
    } while (iVar2 != 0x10);
    puVar1 = puVar1 + 0x10;
    iVar3 = iVar3 + 1;
  } while (iVar3 != 7);
  return;
}

