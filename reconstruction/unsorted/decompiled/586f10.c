
void FUN_00586f10(long param_1)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  undefined8 local_30;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  if (*(char *)(param_1 + 0x41e) == '\0') {
    cVar2 = FUN_00906e00();
    if (cVar2 != '\0') {
      iVar3 = FUN_00591c40(10);
      cVar2 = FUN_00906f70();
      if (cVar2 == '\0') {
        iVar4 = FUN_005916f0();
        if (iVar3 < iVar4 - *(int *)(param_1 + 0x418)) {
          local_48 = 0;
          local_48 = thunk_FUN_012aac96();
          local_40 = thunk_FUN_012aac86();
          FUN_00300230(0x25,*(undefined4 *)PTR_DAT_019e4d68,&local_48);
        }
      }
    }
  }
  else {
    local_38 = 0;
    local_38 = thunk_FUN_012aac96();
    local_30 = thunk_FUN_012aac86();
    FUN_00300230(0x25,*(undefined4 *)PTR_DAT_019e4d68,&local_38);
    *(undefined1 *)(param_1 + 0x41e) = 0;
  }
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

