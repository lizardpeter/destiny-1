
undefined8 FUN_00587d70(void)

{
  undefined1 uVar1;
  long lVar2;
  undefined8 uVar3;
  undefined1 local_a9;
  undefined8 local_a8;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 uStack_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined8 uStack_70;
  undefined8 uStack_68;
  undefined8 local_60;
  undefined8 local_58;
  long local_40;
  
  local_40 = *DAT_01a1f100;
  uVar1 = 0;
  if (DAT_026bc558 != 0) {
    lVar2 = FUN_0034e490();
    if (*(char *)(lVar2 + 0x70) != '\0') {
      local_80 = 0;
      uStack_78 = 0;
      uStack_70 = 0;
      uStack_68 = 0;
      local_a0 = 0;
      uStack_98 = 0;
      uStack_90 = 0;
      uStack_88 = 0;
      local_58 = 0;
      local_60 = 0;
      FUN_001271d0(&uStack_88);
      local_a9 = 0;
      FUN_00072050(&local_a8,0xffffffff);
      uVar1 = FUN_0055aa80(0,0x19,&local_a0,&local_a9,1,local_a8);
    }
  }
  if (*DAT_01a1f100 == local_40) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar1);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

