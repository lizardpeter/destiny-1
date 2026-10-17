
void FUN_0102cc90(undefined4 *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  long *plVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 uVar5;
  int local_38 [2];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  local_38[0] = -1;
  cVar2 = FUN_00073430(param_4);
  if (cVar2 == '\0') {
    FUN_00073430(param_4);
    uVar3 = 0;
  }
  else {
    FUN_002c7d80(local_38,s_entity_index_016271c7,param_4,1);
    uVar3 = FUN_00072c70(param_4,6);
  }
  uVar5 = 0xffffffff;
  if (local_38[0] != -1) {
    iVar4 = FUN_002403b0();
    if (iVar4 != -1) {
      uVar5 = FUN_00240390(iVar4);
      uVar5 = FUN_0030c170(uVar5,uVar3);
    }
  }
  *param_1 = uVar5;
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

