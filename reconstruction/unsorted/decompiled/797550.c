
void FUN_00797550(long param_1)

{
  char cVar1;
  long lVar2;
  undefined8 uVar3;
  int iVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 local_b8 [8];
  undefined4 local_b0;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  cVar1 = FUN_007754d0(0);
  if (cVar1 != '\0') {
    FUN_00797ac0(param_1);
    if (*(char *)(param_1 + 0x31) == '\0') {
      cVar1 = FUN_0075e4a0();
      if (cVar1 == '\0') goto LAB_00797666;
      cVar1 = FUN_0075e4f0();
      if (cVar1 == '\0') {
        iVar5 = -1;
        uVar6 = 0;
      }
      else {
        cVar1 = FUN_0075e580();
        uVar6 = 6;
        iVar5 = 3;
        if (cVar1 == '\0') {
          cVar1 = FUN_0075e600();
          uVar6 = 5;
          if (cVar1 != '\0') {
            uVar6 = 0x119;
          }
        }
      }
    }
    else {
      cVar1 = FUN_0075e4c0();
      uVar6 = 10;
      if (cVar1 != '\0') {
        uVar6 = 0;
      }
      iVar5 = -1;
    }
    cVar1 = FUN_0075e430();
    iVar4 = 0;
    if (cVar1 == '\0') {
      iVar4 = iVar5;
    }
    if (iVar4 != -1) {
      lVar2 = FUN_00775770(0);
      local_b0 = 0;
      uVar3 = FUN_011c3f80(lVar2 + 0x9b8);
      thunk_FUN_012aa7c6(local_b8,uVar3,0x8c);
      local_b8[0] = (undefined1)iVar4;
      uVar3 = FUN_00574ef0();
      FUN_00574dc0(uVar3,local_b8);
      FUN_0078b550(local_b8);
    }
    FUN_00783e90(0,0x1b,uVar6);
  }
LAB_00797666:
  if (*DAT_01a1f100 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

