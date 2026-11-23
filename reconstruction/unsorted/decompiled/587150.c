
void FUN_00587150(undefined8 param_1,undefined8 *param_2)

{
  char cVar1;
  int iVar2;
  long *plVar3;
  long lVar4;
  long lVar5;
  undefined8 local_78;
  undefined8 local_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 local_50;
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  undefined8 local_30;
  undefined8 local_28;
  undefined8 local_20;
  long local_18;
  
  local_18 = *DAT_01a1f100;
  cVar1 = FUN_0025cc10();
  if (cVar1 == '\0') goto LAB_0058726c;
  plVar3 = (long *)FUN_0025cbd0();
  lVar4 = (**(code **)(*plVar3 + 0x10))(plVar3);
  if (lVar4 == 0) goto LAB_0058726c;
  lVar4 = FUN_0058b960();
  if (lVar4 == 0) {
LAB_005871da:
    FUN_002b8260(&local_48);
  }
  else {
    lVar5 = 0;
    if (*(char *)(lVar4 + 0x38) != '\0') {
      lVar5 = lVar4;
    }
    if (lVar5 == 0) goto LAB_005871da;
    local_28 = *(undefined8 *)(lVar5 + 0x28);
    local_20 = *(undefined8 *)(lVar5 + 0x30);
    local_30 = *(undefined8 *)(lVar5 + 0x20);
    local_38 = *(undefined8 *)(lVar5 + 0x18);
    local_48 = *(undefined8 *)(lVar5 + 8);
    local_40 = *(undefined8 *)(lVar5 + 0x10);
  }
  FUN_00552760(&local_48);
  local_58 = param_2[4];
  local_50 = param_2[5];
  local_60 = param_2[3];
  local_68 = param_2[2];
  local_70 = param_2[1];
  local_78 = CONCAT71((int7)((ulong)*param_2 >> 8),2);
  iVar2 = thunk_FUN_012aa826(param_2,&local_78,0x30);
  if (iVar2 != 0) {
    FUN_002487e0((long)&local_78 + 1);
    param_2[5] = local_50;
    param_2[4] = local_58;
    param_2[3] = local_60;
    param_2[2] = local_68;
    param_2[1] = local_70;
    *param_2 = local_78;
  }
LAB_0058726c:
  if (*DAT_01a1f100 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

