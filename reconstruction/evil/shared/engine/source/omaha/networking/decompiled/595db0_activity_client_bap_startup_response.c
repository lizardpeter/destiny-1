
void FUN_00595db0(long param_1,long param_2)

{
  long lVar1;
  long *plVar2;
  long lVar3;
  undefined8 uVar4;
  undefined8 local_b8;
  undefined1 local_b0 [128];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar1 = *(long *)(param_1 + 8);
  lVar3 = thunk_FUN_00768060();
  uVar4 = *(undefined8 *)(param_2 + 1);
  local_b8 = uVar4;
  thunk_FUN_012aa7c6(local_b0,param_2 + 9,0x80);
  if (lVar3 != 0) {
    FUN_0076d8e0(lVar3,*(undefined4 *)(lVar1 + 0x78),&local_b8);
    uVar4 = local_b8;
  }
  plVar2 = *(long **)(lVar1 + 8);
  (**(code **)(*plVar2 + 0x10))(plVar2,uVar4,10,&local_b8,0x88);
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

