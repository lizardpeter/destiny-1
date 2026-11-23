
void FUN_007d91e0(undefined4 *param_1,long param_2)

{
  undefined8 uVar1;
  undefined4 *puVar2;
  
  puVar2 = (undefined4 *)FUN_0082b940(param_2,0x2d,4);
  *puVar2 = *param_1;
  uVar1 = *(undefined8 *)(param_1 + 0x1e);
  *(undefined8 *)(&DAT_000013e0 + param_2) = *(undefined8 *)(param_1 + 0x20);
  *(undefined8 *)(&DAT_000013d8 + param_2) = uVar1;
  return;
}

