
ulong FUN_007965a0(long param_1)

{
  char cVar1;
  byte bVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  long lVar5;
  ulong uVar6;
  byte bVar7;
  long *plVar8;
  bool bVar9;
  int local_3c;
  long local_38;
  
  plVar8 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  cVar1 = FUN_00766750();
  if (cVar1 == '\0') {
    uVar4 = FUN_00765ee0();
    FUN_00757e10(uVar4);
  }
  if (DAT_026cfb70 == '\0') {
    bVar2 = FUN_0010c500(&local_3c);
    uVar3 = FUN_00303ba0();
    lVar5 = FUN_001192b0(uVar3);
    bVar9 = true;
    if (lVar5 != 0) {
      bVar9 = *(char *)(lVar5 + 8) == '\0';
    }
    uVar6 = *(ulong *)(param_1 + 0x1a8);
    bVar7 = 0;
    if (((uVar6 & 0x100) == 0) && ((*(byte *)(param_1 + 0x1a1) & 1) == 0)) {
      bVar7 = *(byte *)(param_1 + 0x199) & 1;
    }
    cVar1 = FUN_007660b0();
    plVar8 = DAT_01a1f100;
    if ((((!bVar9 && (bVar2 & local_3c != 0) == 1) && ((uVar6 & 4) != 0)) && ((uVar6 & 8) != 0)) &&
       ((((uVar6 & 0x40) != 0 && ((uVar6 & 1) != 0)) && (((uVar6 & 0x20) != 0 && (bVar7 == 0)))))) {
      if (*DAT_01a1f100 == local_38) {
        return (ulong)((cVar1 == '\0') + 1);
      }
      goto LAB_007966cc;
    }
  }
  else {
    FUN_0058bf90(s_Holding_0165ab84,s_Enter__world_controller_spacefli_0165ab8c);
  }
  if (*plVar8 == local_38) {
    return 1;
  }
LAB_007966cc:
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

