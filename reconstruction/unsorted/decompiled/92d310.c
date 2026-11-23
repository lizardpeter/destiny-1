
void FUN_0092d310(void)

{
  char cVar1;
  undefined8 uVar2;
  undefined8 *puVar3;
  undefined1 local_2b70 [11072];
  undefined8 local_30;
  undefined8 local_28;
  undefined8 local_20;
  long local_18;
  
  local_18 = *DAT_01a1f100;
  cVar1 = FUN_0092c720();
  if (cVar1 == '\0') {
    FUN_00b9f1c0();
  }
  FUN_00242de0(1,2);
  FUN_002d5b00();
  FUN_0090e360();
  FUN_00b9fec0();
  FUN_008dd4e0();
  FUN_0104b440(local_2b70);
  uVar2 = FUN_009067e0();
  thunk_FUN_012aa7c6(local_2b70,uVar2,0x2b40);
  puVar3 = (undefined8 *)FUN_00906e80();
  local_20 = puVar3[2];
  local_30 = *puVar3;
  local_28 = puVar3[1];
  FUN_00592e20(&DAT_00002b58,local_2b70);
  FUN_00242ea0(1);
  if (*DAT_01a1f100 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

