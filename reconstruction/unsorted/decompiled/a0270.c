
undefined8 FUN_000a0270(void)

{
  uint uVar1;
  uint *puVar2;
  
  puVar2 = (uint *)thunk_FUN_012aaeb6();
  uVar1 = *puVar2;
  if (uVar1 < 0x33) {
    if (uVar1 - 0x23 < 2) {
      return 0;
    }
  }
  else if (uVar1 < 0x41) {
    if (uVar1 < 0x3c) {
      if (uVar1 == 0x33) {
        return 4;
      }
      if (uVar1 == 0x36) {
        return 2;
      }
    }
    else {
      if (uVar1 == 0x3c) {
        return 5;
      }
      if (uVar1 == 0x3d) {
        return 3;
      }
    }
  }
  else if (uVar1 == 0x41) {
    return 1;
  }
  return 7;
}

