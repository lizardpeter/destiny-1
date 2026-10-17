
undefined8 FUN_0006cc60(ushort *param_1,undefined8 param_2)

{
  undefined4 uVar1;
  int iVar2;
  long lVar3;
  undefined8 uVar4;
  
  lVar3 = FUN_000b0af0((long)&DAT_01ad5000 + (ulong)*param_1 * DAT_01ad5010 + DAT_01ad5000,0x11110,
                       0x80);
  *(long *)(param_1 + 4) = lVar3;
  uVar4 = 0;
  if (lVar3 != 0) {
    *(undefined1 *)((long)param_1 + 0x11) = 1;
    uVar1 = FUN_00f6c200(&PTR_DAT_01a111b8);
    iVar2 = FUN_00f69070(*(undefined8 *)(param_1 + 4),uVar1,param_2,0x10);
    uVar4 = 1;
    if (iVar2 != 0) {
      FUN_000b0bd0((long)&DAT_01ad5000 + (ulong)*param_1 * DAT_01ad5010 + DAT_01ad5000,
                   *(undefined8 *)(param_1 + 4));
      *(undefined1 *)((long)param_1 + 0x11) = 0;
      uVar4 = 0;
    }
  }
  return uVar4;
}

