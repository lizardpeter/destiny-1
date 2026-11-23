
void FUN_00906800(undefined4 *param_1)

{
  code *pcVar1;
  undefined8 *puVar2;
  undefined4 uVar3;
  long lVar4;
  
  thunk_FUN_012aa986(param_1,0,0x2b40);
  lVar4 = 0;
  do {
    pcVar1 = (code *)((long)param_1 + (long)(FUN_00001300 + lVar4));
    *(undefined8 *)(pcVar1 + 0x10) = 0;
    *(undefined8 *)(pcVar1 + 8) = 0;
    *(undefined8 *)pcVar1 = 0;
    *(undefined8 *)((long)param_1 + (long)(FUN_00001300 + lVar4)) = 0xffffffff811c9dc5;
    puVar2 = (undefined8 *)((long)param_1 + lVar4 + 0x1308);
    puVar2[1] = 0;
    *puVar2 = 0;
    lVar4 = lVar4 + 0x18;
  } while ((int)lVar4 != 0x4b0);
  param_1[0x5ec] = 0x811c9dc5;
  *(undefined1 *)(param_1 + 0x5ed) = 0;
  FUN_01018280(param_1 + 0x623);
  param_1[0x646] = 0xffffffff;
  uVar3 = FUN_00593880();
  *param_1 = uVar3;
  param_1[4] = 0;
  uVar3 = 0xfe;
  if (DAT_027bd1c8 != '\0') {
    uVar3 = DAT_027be40c;
  }
  param_1[5] = uVar3;
  FUN_002e9160(8,param_1 + 2);
  param_1[1] = 0x78a8;
  return;
}

