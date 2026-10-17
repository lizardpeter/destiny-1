
void FUN_0102cbe0(undefined4 *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  char cVar1;
  undefined4 uVar2;
  undefined8 local_30;
  undefined4 local_28 [2];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  local_30 = 0;
  cVar1 = FUN_00073430(param_4);
  if (cVar1 == '\0') {
    local_30._0_4_ = (uint)local_30 & 0xffffff00;
    local_30 = CONCAT44(0xffffffff,(uint)local_30);
    cVar1 = FUN_00073430(param_4);
    if (cVar1 != '\0') {
      local_30 = CONCAT44(0xfffffffe,(uint)local_30);
    }
    local_30 = CONCAT71(local_30._1_7_,1);
  }
  else {
    local_28[0] = 0xffffffff;
    FUN_002c7d80(local_28,s_entity_index_016271c7,param_4,1);
    local_30 = CONCAT71(local_30._1_7_,1);
    local_30 = CONCAT44(local_28[0],(uint)local_30);
  }
  uVar2 = FUN_002cb4c0(&local_30,0);
  *param_1 = uVar2;
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

