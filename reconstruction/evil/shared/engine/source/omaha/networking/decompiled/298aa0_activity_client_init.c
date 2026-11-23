
void FUN_00298aa0(long param_1,undefined4 param_2,undefined4 param_3,undefined8 param_4,
                 undefined8 param_5,long *param_6,undefined8 param_7,undefined8 param_8)

{
  undefined4 *puVar1;
  undefined8 uVar2;
  ulong uVar3;
  ulong uVar4;
  
  *(long **)(param_1 + 0xe50) = param_6;
  (**(code **)(*param_6 + 0x10))(param_6,param_1 + 8);
  *(undefined8 *)(param_1 + 0xe58) = param_8;
  thunk_FUN_012aa986(&DAT_00005ea8 + param_1,0,0x600);
  *(undefined4 *)(param_1 + 0x64ac) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x64b0) = 0xffffffff;
  *(undefined1 *)(param_1 + 0x15) = 0;
  *(undefined1 *)(param_1 + 0x64a8) = 0;
  *(undefined1 *)(param_1 + 0x64a9) = 1;
  *(undefined1 *)(param_1 + 0x64aa) = 0;
  thunk_FUN_012aa986(param_1 + 0x138,0,0xd18);
  FUN_001271d0(param_1 + 0xb10);
  FUN_001271d0(param_1 + 0xba0);
  FUN_001271d0(param_1 + 0xc98);
  uVar2 = DAT_026553b0;
  if (DAT_026553a8 == '\0') {
    uVar2 = FUN_000694d0();
  }
  *(undefined8 *)(param_1 + 0xe48) = uVar2;
  FUN_002a0800(param_1 + 0xe68);
  FUN_002a0810(param_1 + 0xe68,param_7);
  uVar2 = FUN_00021860(*(undefined8 *)(param_1 + 0xe58));
  FUN_002a2d50(uVar2,param_7,param_1 + 0xe70);
  *(undefined2 *)(param_1 + 0x130) = 0;
  *(undefined4 *)(param_1 + 0x134) = 0;
  thunk_FUN_012aa986(param_1 + 0x64b4,0,0x284);
  *(undefined4 *)(param_1 + 0x18) = param_2;
  *(undefined4 *)(param_1 + 0x1c) = param_3;
  FUN_01009570(param_1 + 0x20,s__s__s_01621cf0,param_4,param_5);
  *(undefined8 *)(param_1 + 0x6740) = 0;
  *(undefined8 *)(param_1 + 0x6738) = 0;
  FUN_002a4980(param_1 + 0x6748);
  FUN_002a4980(param_1 + 0x6968);
  if (((*(int *)(param_1 + 0x6b90) << 0x12) >> 0x12 & 0xfffffffeU) == 0xfffffffe) {
    puVar1 = *(undefined4 **)(param_1 + 0x6b88);
    uVar3 = (ulong)(((*(int *)(param_1 + 0x6b90) << 4) >> 0x12) + 0x1f >> 5);
    if ((uVar3 * 4 < 0x21) && (((ulong)puVar1 & 3) == 0)) {
      if (((uVar3 & 0x3fffffffffffffff) != 0) && (*puVar1 = 0, (uVar3 & 0x3fffffffffffffff) != 1)) {
        uVar4 = 1;
        do {
          *(undefined4 *)(*(long *)(param_1 + 0x6b88) + uVar4 * 4) = 0;
          uVar4 = uVar4 + 1;
        } while ((uVar3 & 0x3fffffffffffffff) != uVar4);
      }
    }
    else {
      thunk_FUN_012aa986(puVar1,0);
    }
  }
  else {
    *(undefined4 *)(param_1 + 0x6b88) = 0;
  }
  *(undefined4 *)(param_1 + 0x6c6c) = 0;
  *(undefined1 *)(param_1 + 0x6bc0) = 0;
  *(undefined8 *)(param_1 + 0x6bb8) = 0;
  *(undefined8 *)(param_1 + 0x6bb0) = 0;
  *(undefined8 *)(param_1 + 0x6ba8) = 0;
  *(undefined8 *)(param_1 + 0x6ba0) = 0;
  *(undefined8 *)(param_1 + 0x6b98) = 0;
  FUN_01018280(param_1 + 0x6bc8);
  *(undefined8 *)(param_1 + 0x6c58) = 0;
  *(undefined8 *)(param_1 + 0x6c60) = 0xffffffffffffffff;
  *(undefined8 *)(param_1 + 0x6c68) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x6c70) = 0;
  *(undefined4 *)(param_1 + 0x6c74) = 0;
  uVar2 = DAT_026553b0;
  if (DAT_026553a8 == '\0') {
    uVar2 = FUN_000694d0();
  }
  *(undefined8 *)(param_1 + 0x6c78) = uVar2;
  uVar2 = DAT_026553b0;
  if (DAT_026553a8 == '\0') {
    uVar2 = FUN_000694d0();
  }
  *(undefined8 *)(param_1 + 0x6c80) = uVar2;
  *(undefined1 *)(param_1 + 0x14) = 1;
  return;
}

