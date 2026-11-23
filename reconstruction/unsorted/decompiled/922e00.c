
void FUN_00922e00(void)

{
  undefined2 *puVar1;
  undefined8 *puVar2;
  
  *DAT_0273eb80 = 0;
  DAT_0273eb80[1] = 0;
  *(undefined4 *)(DAT_0273eb80 + 2) = 0xffffffff;
  *(undefined4 *)(DAT_0273eb80 + 4) = 0xffffffff;
  puVar2 = (undefined8 *)(DAT_0273eb80 + 6);
  *(undefined8 *)(DAT_0273eb80 + 10) = 0xffffffffffffffff;
  *puVar2 = 0xffffffffffffffff;
  puVar1 = DAT_0273eb80;
  thunk_FUN_012aa986(DAT_0273eb80 + 0xe,0xff,0xa0);
  puVar1[0x5e] = 0;
  *(undefined4 *)(DAT_0273eb80 + 0x60) = 0xffffffff;
  *(undefined4 *)(DAT_0273eb80 + 0x62) = 0xffffffff;
  puVar1 = DAT_0273eb80;
  puVar2 = (undefined8 *)(DAT_0273eb80 + 100);
  *(undefined4 *)(DAT_0273eb80 + 0x6c) = 0;
  *(undefined8 *)(puVar1 + 0x68) = 0;
  *puVar2 = 0;
  FUN_008dd4e0();
  return;
}

