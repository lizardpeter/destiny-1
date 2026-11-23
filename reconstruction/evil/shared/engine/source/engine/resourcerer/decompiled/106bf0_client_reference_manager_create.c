
void FUN_00106bf0(void)

{
  undefined4 *puVar1;
  long lVar2;
  undefined4 *puVar3;
  
  puVar1 = (undefined4 *)
           FUN_000af600(0xffff,1,0x2be20,0x19,s_client_reference_manager_01617398,&DAT_025d6ff8);
  puVar3 = (undefined4 *)0x0;
  if (puVar1 != (undefined4 *)0x0) {
    thunk_FUN_012aa986(puVar1,0,0x2be20);
    lVar2 = 0x14;
    do {
      *(undefined4 *)((long)puVar1 + lVar2) = 0x811c9dc5;
      lVar2 = lVar2 + 0x14;
    } while (lVar2 != 0x514);
    puVar1[0x144] = 0;
    puVar1[0xa946] = 0;
    puVar3 = puVar1;
  }
  *puVar3 = 2;
  puVar3[2] = 0;
  puVar3[0x144] = 0;
  puVar3[0xa946] = 0;
  thunk_FUN_012aa986(puVar3 + 0xaf47,0,0x100);
  return;
}

