
void FUN_0077fbf0(long param_1)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined8 uVar5;
  long lVar6;
  char *pcVar7;
  int iVar8;
  undefined4 local_48 [2];
  undefined4 local_40 [2];
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  cVar2 = *(char *)(param_1 + 0x89);
  if ((('\x06' < cVar2) || (*(char *)(param_1 + 0x80) != '\0')) || ('\x02' < cVar2))
  goto LAB_0077fd2e;
  if ('\x01' < cVar2) {
LAB_0077fc61:
    if (*(char *)(param_1 + 0x1d2) == '\x05') {
      FUN_0077adb0(param_1,s_completed_0164ffc9);
    }
    else {
      uVar4 = FUN_0077bc90(param_1);
      FUN_0077ab30(param_1,uVar4);
    }
    goto LAB_0077fd2e;
  }
  if (*(int *)(param_1 + 0x90) != -1) {
    uVar5 = FUN_003430b0();
    cVar2 = FUN_003455e0(uVar5);
    if (cVar2 != '\0') {
      if (*(char *)(param_1 + 0x89) != '\x02') goto LAB_0077fd2e;
      goto LAB_0077fc61;
    }
  }
  lVar6 = FUN_007642b0();
  if (lVar6 == 0) goto LAB_0077fd2e;
  pcVar7 = (char *)FUN_002a2980(lVar6);
  if ((pcVar7 == (char *)0x0) || (*pcVar7 == '\0')) goto LAB_0077fd2e;
  iVar8 = *(int *)(pcVar7 + 0x54);
  uVar4 = *(undefined4 *)(pcVar7 + 0x58);
  if (*(int *)(param_1 + 0x368) == -1) {
LAB_0077fcd5:
    iVar3 = FUN_00102640();
    local_48[0] = uVar4;
    if (iVar3 != -1) {
      FUN_001026a0(local_40);
      iVar8 = iVar3;
      local_48[0] = local_40[0];
    }
  }
  else {
    uVar5 = FUN_003430b0();
    iVar3 = FUN_003454c0(uVar5,*(undefined4 *)(param_1 + 0x368));
    if (iVar3 == 5) goto LAB_0077fcd5;
    iVar8 = *(int *)(param_1 + 0x368);
    local_48[0] = 0x811c9dc5;
  }
  FUN_0077fd50(param_1,2,iVar8,local_48);
LAB_0077fd2e:
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

