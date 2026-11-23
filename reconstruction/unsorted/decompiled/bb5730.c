
void FUN_00bb5730(long param_1,undefined8 *param_2)

{
  char cVar1;
  undefined8 uVar2;
  int iVar3;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar1 = FUN_00906f70();
  if (cVar1 == '\0') {
    local_40 = *param_2;
    param_1 = param_1 + -0x57e0;
    iVar3 = -1;
    do {
      iVar3 = iVar3 + 1;
      if (2 < iVar3) goto LAB_00bb57bd;
      local_48 = *(undefined8 *)(param_1 + 0x18278);
      param_1 = param_1 + 0x18258;
      cVar1 = FUN_000685a0(&local_48,&local_40);
    } while (cVar1 == '\0');
    uVar2 = FUN_00ba2b80(param_1);
    FUN_00b505f0(uVar2,*(undefined1 *)(param_2 + 1));
  }
LAB_00bb57bd:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

