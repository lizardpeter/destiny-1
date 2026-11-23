
undefined8
FUN_005631f0(undefined8 param_1,undefined8 param_2,undefined8 *param_3,undefined8 *param_4,
            undefined8 param_5,int *param_6)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  *(undefined1 *)(param_4 + 1) = *(undefined1 *)(param_3 + 1);
  *param_4 = *param_3;
  uVar2 = *(undefined8 *)((long)param_4 + 1);
  uVar1 = swap_bytes(uVar2);
  *(undefined8 *)((long)param_4 + 1) = uVar1;
  *param_6 = *param_6 + 9;
  return CONCAT71((int7)((ulong)uVar2 >> 8),1);
}

