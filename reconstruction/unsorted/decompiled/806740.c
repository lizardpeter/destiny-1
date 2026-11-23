
void FUN_00806740(void)

{
  long *plVar1;
  int iVar2;
  long lVar3;
  undefined1 local_30 [8];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  lVar3 = FUN_007ec440();
  if ((lVar3 != 0) && (*(char *)(lVar3 + 0x1fc48) != '\0')) {
    FUN_007ed1c0(local_30);
    if (DAT_0295c480 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_0295c480);
      if (iVar2 != 0) {
        DAT_0295c460 = &PTR_FUN_01949440;
        DAT_0295c468 = 0;
        DAT_0295c46c = 0;
        DAT_0295c470 = 0xffffffff;
        DAT_0295c474 = 0xffffffff;
        DAT_0295c478 = 0x3f800000;
        DAT_0295c47c = 0;
        DAT_0295c47d = 0;
        thunk_FUN_012aa7e6(&DAT_0295c480);
      }
    }
    FUN_0088be80(&DAT_0295c460);
    if (DAT_0295c480 == '\0') {
      iVar2 = thunk_FUN_012aa7d6(&DAT_0295c480);
      if (iVar2 != 0) {
        DAT_0295c460 = &PTR_FUN_01949440;
        DAT_0295c468 = 0;
        DAT_0295c46c = 0;
        DAT_0295c470 = 0xffffffff;
        DAT_0295c474 = 0xffffffff;
        DAT_0295c478 = 0x3f800000;
        DAT_0295c47c = 0;
        DAT_0295c47d = 0;
        thunk_FUN_012aa7e6(&DAT_0295c480);
      }
    }
    FUN_0088c050(&DAT_0295c460,local_30);
    thunk_FUN_008147c0(local_30);
    thunk_FUN_007ec540(local_30);
  }
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

