
ulong FUN_0081a600(uint *param_1,undefined8 param_2,ulong *param_3,uint *param_4)

{
  ulong uVar1;
  ulong uVar2;
  ulong *puVar3;
  
  puVar3 = (ulong *)(param_1 + 0x12);
  if ((*param_1 & 8) == 0) {
    puVar3 = (ulong *)(param_1 + 0x10);
  }
  uVar1 = *puVar3;
  *param_3 = uVar1;
  uVar2 = uVar1 & 0xffffffffffffff00;
  *param_4 = param_1[0x36];
  if (*param_3 != 0) {
    *(byte *)((long)param_1 + 2) = *(byte *)((long)param_1 + 2) | 4;
    uVar2 = CONCAT71((int7)(uVar1 >> 8),1);
  }
  return uVar2;
}

