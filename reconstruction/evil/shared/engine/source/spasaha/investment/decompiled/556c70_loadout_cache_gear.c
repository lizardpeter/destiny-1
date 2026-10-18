
void FUN_00556c70(undefined4 param_1,long param_2,undefined8 param_3,undefined1 *param_4)

{
  undefined4 uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  long lVar4;
  char local_a39;
  undefined1 local_a38 [1280];
  undefined1 local_538 [1280];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  *param_4 = 0;
  thunk_FUN_012aa986(local_a38,0,0x500);
  thunk_FUN_012aa986(local_538,0,0x500);
  lVar4 = 0x1e8;
  do {
    if (*(short *)(param_2 + 8 + lVar4) != -1) {
      uVar2 = FUN_0056b260();
      uVar3 = 0;
      if (*(long *)(param_2 + lVar4) != 0) {
        uVar1 = FUN_00011e50(uVar2);
        uVar3 = FUN_0056dc00(uVar2,param_1,uVar1,param_2 + lVar4);
      }
      local_a39 = '\0';
      FUN_005568c0(*(undefined2 *)(param_2 + 8 + lVar4),uVar3,param_3,local_538,local_a38,&local_a39
                  );
      if (local_a39 == '\0') {
        *param_4 = 1;
      }
    }
    lVar4 = lVar4 + 0x40;
  } while ((int)lVar4 != 0x6e8);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

