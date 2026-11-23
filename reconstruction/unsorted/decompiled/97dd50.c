
undefined1 FUN_0097dd50(long param_1,undefined8 *param_2,undefined8 param_3)

{
  short sVar1;
  undefined1 uVar2;
  int iVar3;
  long lVar4;
  
  uVar2 = 0;
  if (1 < *(short *)*param_2) {
    sVar1 = ((short *)*param_2)[1];
    lVar4 = FUN_0097e560(*(undefined8 *)(param_1 + 0x90));
    if ((lVar4 != 0) && (*(long *)(lVar4 + 0x30) != 0)) {
      iVar3 = (int)(s__libexec_ld_elf_so_1_00000000 + 1);
      if (*(code **)(lVar4 + 0x38) != (code *)0x0) {
        iVar3 = (**(code **)(lVar4 + 0x38))(param_1);
      }
      if ((-1 < sVar1) && (sVar1 < iVar3)) {
        uVar2 = (**(code **)(lVar4 + 0x30))(param_1,(int)sVar1,param_3);
      }
    }
  }
  return uVar2;
}

