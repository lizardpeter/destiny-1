
void FUN_003007e0(undefined8 param_1)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  long lVar5;
  undefined1 local_40 [8];
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  iVar3 = FUN_002ff6c0();
  if (0 < iVar3) {
    lVar5 = FUN_002ff810(param_1);
    if (lVar5 != 0) {
      do {
        cVar2 = '\0';
        if (DAT_02689548 == (code *)0x0) {
LAB_0030084c:
          uVar4 = FUN_00240e10();
          FUN_002c7e10(local_40,uVar4);
          if ((*(byte *)(lVar5 + 1) & 1) == 0) {
            FUN_003000d0(lVar5);
            cVar2 = '\x01';
          }
          FUN_002c7e20(local_40);
        }
        else {
          cVar2 = (*DAT_02689548)(lVar5);
          if (cVar2 == '\0') goto LAB_0030084c;
        }
        if (cVar2 != '\0') {
          FUN_002ff560(lVar5);
          FUN_002ff440(lVar5);
        }
        lVar5 = FUN_002ff840(param_1,lVar5);
      } while (lVar5 != 0);
    }
    FUN_002ff6c0(param_1);
    FUN_002ffcb0(param_1);
  }
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

