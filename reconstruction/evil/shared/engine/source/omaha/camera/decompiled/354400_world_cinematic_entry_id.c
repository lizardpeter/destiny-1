
undefined4 * FUN_00354400(undefined4 *param_1,long *param_2)

{
  long lVar1;
  code *pcVar2;
  
  *param_1 = 0x811c9dc5;
  lVar1 = *param_2;
  pcVar2 = *(code **)(lVar1 + 0x30 + *(long *)(lVar1 + 0x18));
  if (((ulong)pcVar2 & 1) != 0) {
    pcVar2 = *(code **)(pcVar2 + *(long *)(param_2[1] +
                                          *(long *)(lVar1 + 0x38 + *(long *)(lVar1 + 0x18))) + -1);
  }
  (*pcVar2)(param_1);
  return param_1;
}

