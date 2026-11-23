
ulong FUN_00b49600(char *param_1,undefined8 param_2)

{
  byte *pbVar1;
  long lVar2;
  int iVar3;
  ulong in_RAX;
  ulong uVar4;
  
  lVar2 = DAT_0282ee90;
  if (*param_1 == '\0') {
    uVar4 = in_RAX & 0xffffffffffffff00;
  }
  else {
    iVar3 = FUN_000a0430(param_2);
    pbVar1 = (byte *)(lVar2 + 2 + (long)iVar3 * 0xc);
    *pbVar1 = *pbVar1 & 0xfe;
    uVar4 = CONCAT71((int7)((ulong)((long)iVar3 * 3) >> 8),1);
  }
  return uVar4;
}

