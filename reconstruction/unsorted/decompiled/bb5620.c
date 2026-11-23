
void FUN_00bb5620(long param_1,undefined8 *param_2)

{
  char cVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  int iVar4;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar1 = FUN_00906f70();
  if (cVar1 == '\0') {
    local_40 = *param_2;
    param_1 = param_1 + -0x57e0;
    iVar4 = -1;
    do {
      iVar4 = iVar4 + 1;
      if (2 < iVar4) goto LAB_00bb56d1;
      local_48 = *(undefined8 *)(param_1 + 0x18278);
      param_1 = param_1 + 0x18258;
      cVar1 = FUN_000685a0(&local_48,&local_40);
    } while (cVar1 == '\0');
    uVar3 = FUN_00ba2b80(param_1);
    FUN_00b52cd0(uVar3,(int)*(char *)(param_2 + 1),(long)param_2 + 0xc,(long)param_2 + 0x60c,
                 (long)param_2 + 0x65c,(long)param_2 + 0x6ac,*(undefined1 *)((long)param_2 + 0x6fc))
    ;
  }
LAB_00bb56d1:
  FUN_00ba0f10((long)param_2 + 0x60c);
  cVar1 = FUN_00906f70();
  if (cVar1 != '\0') {
    FUN_00ba0f60((long)param_2 + 0x65c);
  }
  uVar2 = FUN_00011e50();
  FUN_00ba0c30((long)param_2 + 0x6ac,uVar2);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

