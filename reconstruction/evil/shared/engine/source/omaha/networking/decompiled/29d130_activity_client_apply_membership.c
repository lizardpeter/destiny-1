
undefined8 FUN_0029d130(long *param_1)

{
  long *plVar1;
  long *plVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  undefined8 uVar8;
  undefined *puVar9;
  undefined *puVar10;
  undefined4 local_528c;
  undefined1 local_5288 [320];
  undefined1 local_5148 [4];
  int local_5144;
  undefined1 local_5140 [20528];
  undefined1 local_110 [20];
  undefined4 local_fc;
  undefined1 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_fc = 1;
  FUN_00072240(local_110);
  local_40 = 0;
  plVar1 = param_1 + 0x1ce;
  FUN_00057e60(plVar1);
  FUN_01018410(local_5140);
  local_528c = 0x5038;
  thunk_FUN_012aa7c6(local_5148,plVar1,0x5038);
  FUN_00072400(local_110);
  cVar3 = FUN_002c9ae0(local_110,local_5148,&local_528c,*(undefined4 *)PTR_DAT_0191a308,1);
  FUN_00072650(local_110);
  if (cVar3 == '\0') {
    if (DAT_02655578 == '\0') {
      iVar6 = thunk_FUN_012aa7d6(&DAT_02655578);
      if (iVar6 != 0) {
        DAT_02655570 = FUN_000e4a10(s_networking_activity_client___AC___01622953);
        thunk_FUN_012aa7e6(&DAT_02655578);
      }
    }
    cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar9 = &DAT_01621de5;
    puVar10 = &DAT_01621de5;
    if (cVar3 != '\0') {
      puVar10 = &DAT_01621de3;
    }
    if (cVar4 != '\0') {
      puVar9 = &DAT_01621de3;
    }
    if (cVar5 == '\0') {
      uVar8 = FUN_00001df0();
    }
    else {
      uVar8 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar7 = FUN_00057e60(plVar1);
    FUN_01008290(local_5288,s_networking_activity_client___AC___01622953,param_1 + 4,puVar10,puVar9,
                 uVar8,uVar7);
    FUN_000e4aa0(DAT_02655570,local_5288);
  }
  plVar2 = param_1 + 0x1cd;
  iVar6 = FUN_00078d50(plVar1);
  if (local_5144 != iVar6) {
    *(undefined4 *)((long)param_1 + 0x64b4) = 0;
  }
  FUN_002a0860(plVar2,local_5148);
  uVar8 = (**(code **)(*param_1 + 0x10))(param_1);
  FUN_00240a20(uVar8,plVar2);
  *(byte *)((long)param_1 + 0x131) = *(byte *)((long)param_1 + 0x131) | 1;
  iVar6 = FUN_002a0870(plVar2);
  if (iVar6 != -1) {
    cVar3 = FUN_002a5450(plVar1,iVar6);
    if (cVar3 != '\0') {
      uVar7 = FUN_002a5470(plVar1,iVar6);
      *(undefined4 *)((long)param_1 + 0x134) = uVar7;
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar8 = thunk_FUN_012aa7f6();
  return uVar8;
}

