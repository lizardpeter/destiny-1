
void FUN_000cdbd0(undefined8 param_1,undefined4 *param_2,undefined2 param_3,undefined8 param_4)

{
  long lVar1;
  long lVar2;
  
  lVar1 = FUN_000f2220(&DAT_0256c890);
  *(undefined2 *)(lVar1 + 0x18) = 0xffff;
  *(undefined1 *)(lVar1 + 8) = 0xf;
  lVar2 = FUN_000b4d00(0x110,4);
  *(long *)(lVar1 + 0x10) = lVar2;
  if (lVar2 == 0) {
    if (DAT_01a231f0 == (code *)0x0) {
      FUN_0005c750(s_resourcerer__Asynchronous_regist_01615caf);
      s__libexec_ld_elf_so_1_00000000[1] = '*';
      s__libexec_ld_elf_so_1_00000000[2] = '\0';
      s__libexec_ld_elf_so_1_00000000[3] = '\0';
      s__libexec_ld_elf_so_1_00000000[4] = '\0';
    }
    else {
      (*DAT_01a231f0)(0,s_resourcerer__Asynchronous_regist_01615caf);
    }
  }
  FUN_00065030(*(undefined8 *)(lVar1 + 0x10),param_1,0x100);
  *(undefined2 *)(*(long *)(lVar1 + 0x10) + 0x10c) = param_3;
  *(undefined8 *)(*(long *)(lVar1 + 0x10) + 0x100) = param_4;
  *(undefined4 *)(*(long *)(lVar1 + 0x10) + 0x108) = *param_2;
  LOCK();
  DAT_0254feb8 = DAT_0254feb8 + 1;
  UNLOCK();
  FUN_000f2160(&DAT_0256c880,lVar1);
  return;
}

