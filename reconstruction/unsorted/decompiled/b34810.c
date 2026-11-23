
undefined8 FUN_00b34810(ushort *param_1,ushort *param_2,undefined8 param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  param_2[2] = param_1[2];
  *(undefined4 *)param_2 = *(undefined4 *)param_1;
  *param_2 = *param_1 << 8 | *param_1 >> 8;
  uVar2 = *(undefined4 *)(param_1 + 1);
  uVar1 = swap_bytes(uVar2);
  *(undefined4 *)(param_2 + 1) = uVar1;
  *param_4 = 6;
  return CONCAT71((uint7)(uint3)((uint)uVar2 >> 8),1);
}

