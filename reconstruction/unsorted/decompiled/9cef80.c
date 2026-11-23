
void FUN_009cef80(long param_1,undefined8 param_2,long param_3)

{
  uint uVar1;
  long *plVar2;
  undefined8 *puVar3;
  undefined4 local_30 [2];
  long local_28;
  
  plVar2 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  if ((*(char *)(param_1 + 0x98) == '\x01') && (uVar1 = *(uint *)(param_3 + 0xa0), uVar1 < 4)) {
    puVar3 = (undefined8 *)FUN_0078e990();
    if (puVar3 != (undefined8 *)0x0) {
      (**(code **)*puVar3)(puVar3,uVar1);
      local_30[0] = DAT_0274c04c;
      FUN_0098a980(local_30,param_1);
    }
  }
  if (*plVar2 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

