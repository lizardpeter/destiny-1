
void FUN_007e33e0(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  long lVar3;
  
  if (DAT_026e2be0 == '\0') {
    puVar1 = (undefined4 *)
             FUN_000af600(0xffff,1,0x24f90,0xe,s_device_manager_0165fedf,&DAT_026e2bf0);
    puVar2 = (undefined4 *)0x0;
    if (puVar1 != (undefined4 *)0x0) {
      *puVar1 = 0;
      FUN_007e4050(puVar1 + 4);
      FUN_007e5d00(puVar1 + 0xa44);
      FUN_007e5d00(puVar1 + 0x145c);
      FUN_007e5d00(puVar1 + 0x1e74);
      FUN_007e5d00(puVar1 + 0x288c);
      FUN_007e5d00(puVar1 + 0x32a4);
      FUN_007e5d00(puVar1 + 0x3cbc);
      puVar2 = puVar1 + 0x478c;
      do {
        FUN_0006ac30(puVar2);
        puVar2[6] = 0;
        puVar2 = puVar2 + 0x24e;
      } while (puVar2 != puVar1 + 0x914c);
      lVar3 = 0;
      do {
        FUN_0006ac30((long)(puVar1 + 0x914c) + lVar3);
        lVar3 = lVar3 + 0x18;
      } while (lVar3 != 0x900);
      *(undefined8 *)(puVar1 + 0x93d8) = 0;
      *(undefined8 *)(puVar1 + 0x93da) = 0;
      thunk_FUN_012aa986(puVar1 + 0x9398,0,0x128);
      puVar1[0x93de] = 1;
      puVar2 = puVar1;
    }
    DAT_026e2be8 = puVar2;
    DAT_026e2be0 = FUN_007e3740();
  }
  return;
}

