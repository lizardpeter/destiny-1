
void FUN_00bb2170(undefined8 param_1,undefined8 param_2)

{
  char cVar1;
  undefined4 uVar2;
  long lVar3;
  undefined1 local_4b0 [8];
  undefined8 local_4a8 [2];
  undefined1 local_498 [1144];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  thunk_FUN_012aa986(local_4a8,0,0x480);
  local_4a8[0] = param_1;
  lVar3 = FUN_0075d6b0(param_1);
  if ((lVar3 != 0) && (*(char *)(lVar3 + 0x1c) != '\0')) {
    FUN_002c7e10(local_4b0,0xfffffffe);
    uVar2 = FUN_002560a0(*(undefined4 *)(lVar3 + 0xd9c));
    cVar1 = FUN_002554b0(uVar2,1,param_2,local_498);
    if (cVar1 != '\0') {
      FUN_00300230(0x19,*(undefined4 *)PTR_DAT_019b4708,local_4a8);
    }
    FUN_002c7e20(local_4b0);
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

