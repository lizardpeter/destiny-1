
void FUN_00913d20(long *param_1)

{
  long *plVar1;
  char cVar2;
  long lVar3;
  long *plVar4;
  uint uVar5;
  uint uVar6;
  undefined1 local_60 [8];
  undefined4 local_58;
  long local_50;
  undefined1 local_48 [8];
  undefined4 local_40;
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  uVar5 = 0xffffffff;
  if (param_1 != (long *)0x0) {
    uVar5 = 0xffffffff;
    uVar6 = 0;
    plVar4 = DAT_0273ea90;
    do {
      plVar4 = plVar4 + 1;
      if (((*(uint *)((long)DAT_0273ea90 + 4) >> (uVar6 & 0x1f) & 1) != 0) && (*param_1 == *plVar4))
      {
        uVar5 = uVar6;
      }
      uVar6 = uVar6 + 1;
    } while (uVar6 != 0x14);
  }
  if (((param_1 != (long *)0x0) != (bool)(char)DAT_0273ea90[0x15]) ||
     (((param_1 != (long *)0x0 && (*param_1 != *(long *)((long)DAT_0273ea90 + 0xa9))) ||
      (uVar5 != *(uint *)((long)DAT_0273ea90 + 0xb4))))) {
    cVar2 = FUN_00906f70();
    if (cVar2 == '\0') {
      FUN_00074a80(local_48,DAT_0273ea80);
      while( true ) {
        local_50 = FUN_00074a90(local_48);
        if (local_50 == 0) break;
        FUN_00922ef0(local_40,0xffffffff);
        FUN_00923080(local_40,0xffffffff);
        FUN_00923590(local_40);
      }
    }
    *(bool *)(DAT_0273ea90 + 0x15) = param_1 != (long *)0x0;
    *(uint *)((long)DAT_0273ea90 + 0xb4) = uVar5;
    if (param_1 == (long *)0x0) {
      *(undefined8 *)((long)DAT_0273ea90 + 0xa9) = 0;
    }
    else {
      *(long *)((long)DAT_0273ea90 + 0xa9) = *param_1;
    }
    cVar2 = FUN_00906f70();
    if ((cVar2 == '\0') && (*(int *)((long)DAT_0273ea90 + 0xb4) != -1)) {
      FUN_00074a80(local_60,DAT_0273ea80);
      while( true ) {
        lVar3 = FUN_00074a90(local_60);
        if (lVar3 == 0) break;
        if (*(int *)(lVar3 + 0x628) == *(int *)((long)DAT_0273ea90 + 0xb4)) {
          FUN_00922ef0(local_58,*(undefined4 *)(lVar3 + 0x62c));
          FUN_00923080(local_58,*(undefined4 *)(lVar3 + 0x630));
          FUN_00923430(*(undefined4 *)(lVar3 + 0x62c),local_58);
        }
      }
    }
  }
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

