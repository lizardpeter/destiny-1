
void FUN_00bb6080(undefined8 *param_1)

{
  int iVar1;
  undefined1 *puVar2;
  int local_52b0;
  char local_52a9;
  undefined1 local_52a8 [21120];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  local_52a9 = '\0';
  puVar2 = local_52a8;
  FUN_00ba6510(*param_1,&local_52a9,puVar2);
  if (local_52a9 != '\0') {
    FUN_00300230(0xd,*(undefined4 *)PTR_DAT_019b45e0,local_52a8);
  }
  local_52b0 = 0;
  FUN_00ba6760(*param_1,&local_52b0,0x50,puVar2);
  if (0 < local_52b0) {
    iVar1 = 0;
    do {
      FUN_00bad130(puVar2);
      puVar2 = puVar2 + 0x108;
      iVar1 = iVar1 + 1;
    } while (iVar1 < local_52b0);
  }
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

