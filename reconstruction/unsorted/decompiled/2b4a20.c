
ulong FUN_002b4a20(ulong *param_1,undefined8 *param_2,undefined8 param_3,undefined4 *param_4,
                  undefined1 *param_5)

{
  undefined4 uVar1;
  undefined8 uVar2;
  long lVar3;
  ulong uVar4;
  
  lVar3 = DAT_0266d6a0;
  if (*param_1 == *(ulong *)(DAT_0266d6a0 + 0x280)) {
    uVar2 = *(undefined8 *)(DAT_0266d6a0 + 0x2a8);
    param_2[5] = *(undefined8 *)(DAT_0266d6a0 + 0x2b0);
    param_2[4] = uVar2;
    param_2[3] = *(undefined8 *)(lVar3 + 0x2a0);
    param_2[2] = *(undefined8 *)(lVar3 + 0x298);
    uVar2 = *(undefined8 *)(lVar3 + 0x288);
    param_2[1] = *(undefined8 *)(lVar3 + 0x290);
    *param_2 = uVar2;
    thunk_FUN_012aa7c6(param_3,lVar3 + 0x2b8,0x4e);
    uVar1 = *(undefined4 *)(lVar3 + 0x308);
    *param_4 = uVar1;
    uVar4 = CONCAT71((uint7)(uint3)((uint)uVar1 >> 8),1);
    *param_5 = *(undefined1 *)(lVar3 + 0x313);
  }
  else {
    uVar4 = *param_1 & 0xffffffffffffff00;
  }
  return uVar4;
}

