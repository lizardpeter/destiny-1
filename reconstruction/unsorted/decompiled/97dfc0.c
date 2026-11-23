
ulong FUN_0097dfc0(long param_1,uint param_2,undefined8 *param_3)

{
  undefined8 uVar1;
  ulong in_RAX;
  undefined8 *puVar2;
  undefined8 *puVar3;
  
  if (param_2 < 2) {
    if (param_2 != 0) {
      return in_RAX & 0xffffffffffffff00;
    }
    *param_3 = 0x82166bc0;
    puVar2 = &DAT_02786d08;
    param_3[1] = &DAT_02786d08;
    *(undefined4 *)(param_3 + 3) = 2;
    *(undefined4 *)((long)param_3 + 0x1c) = 0;
    param_3[4] = 0;
  }
  else {
    puVar3 = (undefined8 *)FUN_0097e560(*(undefined8 *)(param_1 + 0x90));
    if (puVar3 == (undefined8 *)0x0) {
      return (ulong)puVar3 & 0xffffffffffffff00;
    }
    uVar1 = puVar3[3];
    param_3[4] = puVar3[4];
    param_3[3] = uVar1;
    param_3[2] = puVar3[2];
    puVar2 = (undefined8 *)*puVar3;
    param_3[1] = puVar3[1];
    *param_3 = puVar2;
  }
  return CONCAT71((int7)((ulong)puVar2 >> 8),1);
}

