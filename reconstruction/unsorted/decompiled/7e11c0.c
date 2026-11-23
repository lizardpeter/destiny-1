
undefined1 FUN_007e11c0(undefined8 param_1,int param_2,undefined8 param_3,undefined8 *param_4)

{
  undefined8 *puVar1;
  undefined4 *puVar2;
  undefined1 uVar3;
  uint uVar4;
  undefined4 *puVar5;
  
  uVar3 = 0;
  *param_4 = 0;
  if (param_2 == 0) {
    uVar4 = 0xffffffff;
    puVar2 = (undefined4 *)&DAT_026df3a0;
    do {
      puVar5 = puVar2;
      uVar4 = uVar4 + 1;
      if (0x382 < uVar4) {
        return 0;
      }
      puVar2 = puVar5 + 4;
    } while (puVar5[4] != 1);
    *puVar2 = 0;
    puVar1 = (undefined8 *)FUN_000b49b0(0x80,0xe);
    *(undefined8 **)(puVar5 + 6) = puVar1;
    *puVar1 = 0;
    puVar1[1] = 0;
    uVar3 = 1;
    puVar1[2] = 0;
    puVar1[3] = 0;
    puVar1[4] = 0;
    puVar1[5] = 0;
    puVar1[6] = 0;
    puVar1[7] = 0;
    puVar1[8] = 0;
    puVar1[9] = 0;
    puVar1[10] = 0;
    puVar1[0xb] = 0;
    puVar1[0xc] = 0;
    puVar1[0xd] = 0;
    puVar1[0xe] = 0;
    puVar1[0xf] = 0;
    *param_4 = puVar2;
  }
  return uVar3;
}

