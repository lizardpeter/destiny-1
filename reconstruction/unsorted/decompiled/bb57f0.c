
void FUN_00bb57f0(long param_1,undefined8 *param_2)

{
  long lVar1;
  char cVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  int iVar5;
  long lVar6;
  undefined8 local_40;
  undefined8 local_38;
  long local_30;
  
  local_30 = *DAT_01a1f100;
  cVar2 = FUN_00906f70();
  if (cVar2 == '\0') {
    local_38 = *param_2;
    iVar5 = -1;
    lVar1 = param_1 + -0x57e0;
    do {
      lVar6 = lVar1;
      iVar5 = iVar5 + 1;
      if (2 < iVar5) goto LAB_00bb5893;
      local_40 = *(undefined8 *)(lVar6 + 0x18278);
      cVar2 = FUN_000685a0(&local_40,&local_38);
      lVar1 = lVar6 + 0x18258;
    } while (cVar2 == '\0');
    uVar3 = FUN_00ba2b80(lVar6 + 0x18258);
    uVar4 = FUN_0029bd90(*(undefined8 *)(lVar6 + 0x18268));
    FUN_00b53bb0(uVar3,uVar4);
    FUN_00298db0(*(undefined8 *)(lVar6 + 0x18268));
  }
LAB_00bb5893:
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

