
ulong FUN_0056bf90(long param_1,char param_2,ulong *param_3,undefined4 *param_4)

{
  undefined4 uVar1;
  uint uVar2;
  long lVar4;
  ulong uVar3;
  
  *param_4 = 0xffffffff;
  lVar4 = 0x9c;
  while ((uVar2 = (uint)*(char *)(param_1 + -0x3c + lVar4), uVar3 = (ulong)uVar2,
         uVar2 != (int)param_2 || (uVar3 = *(ulong *)(param_1 + -0x1c + lVar4), uVar3 != *param_3)))
  {
    lVar4 = lVar4 + 0x40;
    if ((int)lVar4 == 0x40dc) {
      return uVar3 & 0xffffffffffffff00;
    }
  }
  if (*(char *)(param_1 + -0x14 + lVar4) != '\x03') {
    return uVar3 & 0xffffffffffffff00;
  }
  uVar1 = *(undefined4 *)(param_1 + lVar4);
  *param_4 = uVar1;
  return CONCAT71((uint7)(uint3)((uint)uVar1 >> 8),1);
}

