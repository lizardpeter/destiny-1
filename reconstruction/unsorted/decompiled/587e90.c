
void FUN_00587e90(long param_1,char *param_2)

{
  long *plVar1;
  uint uVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  uint uVar5;
  int local_690 [2];
  undefined1 local_688 [512];
  undefined1 local_488 [512];
  undefined1 local_288 [600];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  uVar4 = FUN_009503d0();
  uVar2 = FUN_00244e40();
  FUN_00973ed0(local_688);
  if (*param_2 != '\0') {
    FUN_000663a0(param_2 + 1,local_288,0x10e,0);
  }
  if (param_2[0x201] != '\0') {
    FUN_000663a0(param_2 + 0x202,local_488,0x100,0);
  }
  local_690[0] = *(int *)(param_2 + 0x284);
  if (*(int *)(param_2 + 0x284) == 0) {
    local_690[0] = DAT_026bc560;
  }
  uVar5 = 4;
  if (uVar2 < 4) {
    uVar5 = uVar2;
  }
  uVar3 = FUN_00951a30(uVar4,local_690,local_688,uVar5,0);
  plVar1 = DAT_01a1f100;
  *(undefined4 *)(param_1 + 4) = uVar3;
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

