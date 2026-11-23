
ulong FUN_0006eeb0(long *param_1,uint param_2)

{
  uint uVar1;
  ulong in_RAX;
  ulong uVar2;
  
  uVar2 = in_RAX & 0xffffffffffffff00;
  if ((short)param_2 != -1) {
    uVar1 = *(uint *)(*(long *)(*(long *)(*param_1 + 8) + 0x10) + ((ulong)(param_2 >> 3) & 0x1ffc));
    uVar2 = (ulong)CONCAT31((int3)(uVar1 >> 8),(uVar1 >> (param_2 & 0x1f) & 1) != 0);
  }
  return uVar2;
}

