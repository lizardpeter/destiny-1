
void FUN_00571be0(undefined8 param_1,undefined8 param_2,undefined4 *param_3)

{
  long lVar1;
  long *plVar2;
  undefined8 *puVar3;
  long *plVar4;
  undefined4 uStack_10034;
  undefined4 uStack_10030;
  undefined1 auStack_1002c [4];
  undefined8 uStack_10028;
  
  plVar2 = DAT_01a1f100;
  lVar1 = *DAT_01a1f100;
  uStack_10030 = *param_3;
  uStack_10028 = *(undefined8 *)(param_3 + 2);
  puVar3 = (undefined8 *)FUN_00078970(&uStack_10030,*(undefined4 *)PTR_DAT_019e4c20);
  plVar4 = (long *)FUN_0055af60(0x7b);
  uStack_10030 = 0x10000;
  (**(code **)(*plVar4 + 0x18))
            (plVar4,*puVar3,*(undefined4 *)(puVar3 + 1),0x10000,&uStack_10034,auStack_1002c);
  uStack_10030 = uStack_10034;
  FUN_00566050(uStack_10034,auStack_1002c);
  if (*plVar2 == lVar1) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

