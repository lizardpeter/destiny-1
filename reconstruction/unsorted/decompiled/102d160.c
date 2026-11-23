
void FUN_0102d160(undefined4 *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined8 extraout_RDX;
  undefined8 uVar5;
  uint local_38 [2];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  cVar2 = FUN_00073430(param_4);
  if (cVar2 == '\0') {
    FUN_00073430(param_4);
    uVar5 = 0;
    uVar4 = 0xffffffff;
  }
  else {
    local_38[0] = 0xffffffff;
    FUN_002c7d80(local_38,s_entity_index_016271c7,param_4,1);
    uVar5 = 0;
    uVar4 = 0xffffffff;
    if (local_38[0] < 0xfffffffe) {
      iVar3 = FUN_002403b0();
      if (iVar3 != -1) {
        iVar3 = FUN_00240370(iVar3);
        if (iVar3 != -1) {
          uVar4 = FUN_00105e80(iVar3);
          uVar5 = extraout_RDX;
        }
      }
    }
  }
  *param_1 = uVar4;
  *(undefined8 *)(param_1 + 2) = uVar5;
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

