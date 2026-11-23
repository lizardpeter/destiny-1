
undefined4 FUN_007da910(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = (int)((ulong)*(undefined8 *)(DAT_026df268 + 0x28000) >> 0x20);
  iVar3 = (int)*(undefined8 *)(DAT_026df268 + 0x28000);
  iVar2 = iVar1 - iVar3;
  if (iVar2 < 0) {
    iVar2 = (iVar1 - iVar3) + 0xa00;
  }
  return CONCAT31((int3)((uint)(iVar2 + param_1) >> 8),(uint)(iVar2 + param_1) < 0xa01);
}

