
ulong FUN_009cdbf0(undefined8 param_1,ulong *param_2)

{
  ulong uVar1;
  
  if (*param_2 != param_2[1]) {
    uVar1 = FUN_010de350();
    return uVar1;
  }
  return *param_2 & 0xffffffffffffff00;
}

