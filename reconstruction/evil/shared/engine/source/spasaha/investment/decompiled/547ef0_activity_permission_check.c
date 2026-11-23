
bool FUN_00547ef0(undefined8 param_1,undefined4 param_2)

{
  long *plVar1;
  undefined1 uVar2;
  long lVar3;
  bool bVar4;
  bool bVar5;
  char local_33;
  char local_32;
  char local_31;
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  lVar3 = FUN_007756e0(0);
  bVar4 = true;
  if (lVar3 != 0) {
    bVar4 = *(int *)(lVar3 + 0xc) != *(int *)(lVar3 + 0x5d0c);
  }
  local_31 = '\0';
  local_32 = '\0';
  local_33 = '\0';
  FUN_002668d0(param_1);
  FUN_002648d0(param_1,param_2,&local_31,&local_33,&local_32);
  bVar5 = false;
  if (local_31 != '\0') {
    bVar5 = local_33 != '\0';
    if (!(bool)(local_33 == '\0' | bVar4)) {
      bVar5 = local_32 != '\0';
    }
  }
  if (*plVar1 == local_30) {
    return bVar5;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return (bool)uVar2;
}

