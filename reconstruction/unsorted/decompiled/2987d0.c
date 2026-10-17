
void FUN_002987d0(undefined8 *param_1)

{
  undefined4 *puVar1;
  undefined8 uVar2;
  ulong uVar3;
  ulong uVar4;
  
  *param_1 = &PTR_FUN_01910400;
  param_1[1] = &PTR_FUN_01910460;
  *(undefined1 *)(param_1 + 6) = 0;
  *(undefined4 *)((long)param_1 + 0x14c) = 0;
  *(undefined4 *)(param_1 + 0xfa) = 0;
  FUN_002a07d0(param_1 + 0x1cd);
  thunk_FUN_012aa986(param_1 + 0xbd5,0,0x600);
  *(undefined4 *)((long)param_1 + 0x6804) = 0x811c9dc5;
  *(undefined4 *)((long)param_1 + 0x6814) = 0;
  *(undefined4 *)((long)param_1 + 0x68a4) = 0x811c9dc5;
  *(undefined4 *)((long)param_1 + 0x68b4) = 0;
  *(undefined4 *)((long)param_1 + 0x695c) = 0x811c9dc5;
  *(undefined4 *)((long)param_1 + 0x6a24) = 0x811c9dc5;
  *(undefined4 *)((long)param_1 + 0x6a34) = 0;
  *(undefined4 *)((long)param_1 + 0x6ac4) = 0x811c9dc5;
  *(undefined4 *)((long)param_1 + 0x6ad4) = 0;
  *(undefined4 *)((long)param_1 + 0x6b7c) = 0x811c9dc5;
  *(undefined4 *)(param_1 + 0xd71) = 0;
  *(undefined4 *)(param_1 + 0xd72) = 0x10004000;
  *(undefined4 *)(param_1 + 0xd7a) = 0;
  *(undefined1 *)((long)param_1 + 0x14) = 0;
  *(undefined1 *)((long)param_1 + 0x15) = 0;
  *(undefined2 *)(param_1 + 0x26) = 0;
  *(undefined4 *)((long)param_1 + 0x134) = 0;
  param_1[0x1ca] = 0;
  *(undefined1 *)(param_1 + 6) = 0;
  *(undefined1 *)(param_1 + 0x1cc) = 0;
  *(undefined4 *)(param_1 + 3) = 0xffffffff;
  *(undefined1 *)(param_1 + 4) = 0;
  FUN_01018280(param_1 + 0xd79);
  param_1[0xd8b] = 0;
  param_1[0xd8c] = 0xffffffffffffffff;
  *(undefined4 *)(param_1 + 0xd8d) = 0xffffffff;
  thunk_FUN_012aa986(param_1 + 0x27,0,0xd18);
  FUN_001271d0(param_1 + 0x162);
  FUN_001271d0(param_1 + 0x174);
  FUN_001271d0(param_1 + 0x193);
  uVar2 = DAT_026553b0;
  if (DAT_026553a8 == '\0') {
    uVar2 = FUN_000694d0();
  }
  param_1[0x1c9] = uVar2;
  param_1[0xce8] = 0;
  param_1[0xce7] = 0;
  FUN_002a4980(param_1 + 0xce9);
  FUN_002a4980(param_1 + 0xd2d);
  if (((*(int *)(param_1 + 0xd72) << 0x12) >> 0x12 & 0xfffffffeU) == 0xfffffffe) {
    puVar1 = (undefined4 *)param_1[0xd71];
    uVar3 = (ulong)(((*(int *)(param_1 + 0xd72) << 4) >> 0x12) + 0x1f >> 5);
    if ((uVar3 * 4 < 0x21) && (((ulong)puVar1 & 3) == 0)) {
      if (((uVar3 & 0x3fffffffffffffff) != 0) && (*puVar1 = 0, (uVar3 & 0x3fffffffffffffff) != 1)) {
        uVar4 = 1;
        do {
          *(undefined4 *)(param_1[0xd71] + uVar4 * 4) = 0;
          uVar4 = uVar4 + 1;
        } while ((uVar3 & 0x3fffffffffffffff) != uVar4);
      }
    }
    else {
      thunk_FUN_012aa986(puVar1,0);
    }
  }
  else {
    *(undefined4 *)(param_1 + 0xd71) = 0;
  }
  *(undefined4 *)((long)param_1 + 0x6c6c) = 0;
  *(undefined1 *)(param_1 + 0xd78) = 0;
  param_1[0xd77] = 0;
  param_1[0xd76] = 0;
  param_1[0xd75] = 0;
  param_1[0xd74] = 0;
  param_1[0xd73] = 0;
  return;
}

