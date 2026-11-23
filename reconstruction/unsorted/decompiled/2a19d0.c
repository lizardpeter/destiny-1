
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

long FUN_002a19d0(long param_1)

{
  float fVar1;
  int iVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  
  lVar3 = FUN_002a2980(*(undefined8 *)(param_1 + 0x10));
  lVar3 = *(long *)(lVar3 + 0x520);
  iVar2 = FUN_002a2ec0(*(undefined8 *)(param_1 + 0x10));
  if (0 < iVar2) {
    lVar4 = FUN_002a2900(*(undefined8 *)(param_1 + 0x10));
    fVar1 = (float)iVar2 * (*(float *)(lVar4 + 4) / DAT_01622e10);
    uVar5 = (long)fVar1;
    if (_DAT_01622e14 <= fVar1) {
      uVar5 = (long)(fVar1 - _DAT_01622e14) ^ 0x8000000000000000;
    }
    lVar3 = uVar5 + lVar3;
  }
  return lVar3;
}

