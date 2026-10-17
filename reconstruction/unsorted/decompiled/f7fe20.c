
void FUN_00f7fe20(long param_1,uint param_2)

{
  undefined4 *puVar1;
  char cVar2;
  
  if ((2 < (uint)((ulong)(*(long *)(param_1 + 8) - *(long *)(param_1 + 0x10)) >> 2)) ||
     (cVar2 = (**(code **)(param_1 + 0x18))(param_1,3,*(undefined8 *)(param_1 + 0x20)),
     cVar2 != '\0')) {
    if (param_2 < 0x200) {
      if (param_2 < 0x45) {
        if (param_2 != 0) {
          return;
        }
      }
      else if (((param_2 != 0x45) && (param_2 != 0xad)) && (param_2 != 0xb0)) {
        return;
      }
    }
    else if (param_2 != 0x200) {
      return;
    }
    puVar1 = *(undefined4 **)(param_1 + 0x10);
    *puVar1 = 0xc0016900;
    puVar1[1] = 0x2d5;
    puVar1[2] = param_2;
    *(undefined4 **)(param_1 + 0x10) = puVar1 + 3;
  }
  return;
}

