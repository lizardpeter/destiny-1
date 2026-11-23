
undefined8 FUN_00923320(uint *param_1)

{
  byte bVar1;
  ulong uVar2;
  
  if (*param_1 == 0xffffffff) {
    uVar2 = (ulong)param_1[1];
  }
  else {
    bVar1 = *(byte *)(DAT_0273eb80 + 200 + (ulong)(*param_1 & 0xffff));
    uVar2 = 0xffffffff;
    if ((bVar1 != 0) && (param_1[1] == 0xffffffff)) {
      uVar2 = (ulong)(uint)(int)(char)((bVar1 & 1) - 1);
    }
    param_1[1] = (uint)uVar2;
  }
  return CONCAT71((int7)(uVar2 >> 8),(int)uVar2 != -1);
}

