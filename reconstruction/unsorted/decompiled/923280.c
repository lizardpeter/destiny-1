
void FUN_00923280(uint param_1,undefined4 param_2,undefined1 param_3)

{
  int iVar1;
  byte bVar2;
  bool bVar3;
  
  if (param_1 != 0xffffffff) {
    iVar1 = *(int *)(DAT_0273eb80 + 0x6c + (ulong)(param_1 & 0xffff) * 4);
    bVar3 = true;
    if (iVar1 != -1) {
      FUN_00923010(iVar1,param_2);
    }
    while (((bVar2 = *(byte *)(DAT_0273eb80 + 200 + (ulong)(param_1 & 0xffff)), bVar2 != 0 &&
            (bVar3)) && (bVar2 = bVar2 & 1, bVar2 != 0))) {
      FUN_00923370((int)(char)(bVar2 - 1),param_2,param_3);
      bVar3 = bVar2 == 0;
    }
  }
  return;
}

