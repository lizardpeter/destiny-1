
void FUN_00299640(long *param_1)

{
  long lVar1;
  char cVar2;
  int iVar3;
  long lVar4;
  long lVar5;
  undefined8 uVar6;
  undefined8 local_178;
  undefined4 local_170;
  undefined1 local_169;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  lVar4 = (**(code **)(*(long *)param_1[0x1ca] + 0x28))();
  lVar1 = param_1[0x1c9];
  lVar5 = DAT_026553b0;
  if (DAT_026553a8 == '\0') {
    lVar5 = FUN_000694d0();
  }
  if (((long)*(int *)((long)param_1 + 0x6c74) <= lVar5 - lVar1) ||
     (*(char *)((long)param_1 + 0x15) != '\0')) {
    uVar6 = (**(code **)(*param_1 + 0x10))(param_1);
    local_170 = 1;
    cVar2 = FUN_00299d10(param_1,uVar6,0xf,0xffffffff,&local_169,1,&local_170);
    if (cVar2 == '\0') {
      if ((DAT_02655588 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_02655588), iVar3 != 0)) {
        DAT_02655580 = FUN_000e4a10(s_networking_activity_client__Coul_016229bc);
        thunk_FUN_012aa7e6(&DAT_02655588);
      }
      local_178 = (**(code **)(*param_1 + 0x10))(param_1);
      uVar6 = FUN_002a35d0(&local_178);
      FUN_01008290(local_168,s_networking_activity_client__Coul_016229bc,uVar6);
      FUN_000e4aa0(DAT_02655580,local_168);
    }
    *(undefined1 *)((long)param_1 + 0x15) = 0;
  }
  if ((lVar4 != -1) && (DAT_026553a8 == '\0')) {
    FUN_000694d0();
  }
  if (*DAT_01a1f100 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

