
void FUN_004ed850(long param_1,undefined4 *param_2)

{
  undefined8 uVar1;
  undefined8 uVar2;
  int iVar3;
  undefined1 local_150 [204];
  undefined4 local_84;
  undefined4 local_80;
  undefined4 local_7c;
  undefined4 local_78;
  undefined4 local_74;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_68;
  undefined4 local_64;
  undefined4 local_60;
  undefined4 local_58;
  undefined4 local_50;
  undefined4 local_48;
  undefined4 local_40;
  undefined4 local_38;
  undefined4 local_30;
  undefined4 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  *(undefined4 *)(param_1 + 0x250) = *param_2;
  *(undefined4 *)(param_1 + 0x254) = param_2[1];
  *(undefined4 *)(param_1 + 600) = param_2[2];
  *(undefined4 *)(param_1 + 0x25c) = param_2[3];
  *(undefined4 *)(param_1 + 0x260) = param_2[4];
  *(undefined4 *)(param_1 + 0x264) = param_2[5];
  *(undefined4 *)(param_1 + 0x268) = param_2[6];
  *(undefined4 *)(param_1 + 0x26c) = param_2[7];
  *(undefined4 *)(param_1 + 0x270) = param_2[8];
  *(undefined4 *)(param_1 + 0x274) = param_2[9];
  *(undefined4 *)(param_1 + 0x278) = param_2[10];
  *(undefined4 *)(param_1 + 0x27c) = param_2[0xb];
  *(undefined4 *)(param_1 + 0x280) = param_2[0xc];
  *(undefined4 *)(param_1 + 0x284) = param_2[0xd];
  uVar1 = *(undefined8 *)(param_2 + 0x16);
  uVar2 = *(undefined8 *)(param_2 + 0x18);
  *(undefined4 *)(param_1 + 0x2b8) = param_2[0x1a];
  *(undefined8 *)(param_1 + 0x2b0) = uVar2;
  *(undefined8 *)(param_1 + 0x2a8) = uVar1;
  *(undefined8 *)(param_1 + 0x2a0) = *(undefined8 *)(param_2 + 0x14);
  *(undefined8 *)(param_1 + 0x298) = *(undefined8 *)(param_2 + 0x12);
  uVar1 = *(undefined8 *)(param_2 + 0xe);
  *(undefined8 *)(param_1 + 0x290) = *(undefined8 *)(param_2 + 0x10);
  *(undefined8 *)(param_1 + 0x288) = uVar1;
  local_84 = 0;
  local_80 = 0x811c9dc5;
  local_7c = 0x811c9dc5;
  local_78 = 0x811c9dc5;
  local_74 = 0x811c9dc5;
  local_70 = 0x811c9dc5;
  local_6c = 0x811c9dc5;
  local_68 = 0x811c9dc5;
  local_64 = 0x811c9dc5;
  local_60 = 0x811c9dc5;
  local_58 = 0x811c9dc5;
  local_50 = 0x811c9dc5;
  local_48 = 0x811c9dc5;
  local_40 = 0x811c9dc5;
  local_38 = 0x811c9dc5;
  local_30 = 0x811c9dc5;
  local_28 = 0x811c9dc5;
  FUN_00644040(param_2,local_150);
  iVar3 = FUN_0063fb20(0,local_150);
  if (iVar3 != -1) {
    if (*(int *)(param_1 + 0x2fc) != -1) {
      FUN_0063fc10();
    }
    *(int *)(param_1 + 0x2fc) = iVar3;
    *(byte *)(param_1 + 0x308) = *(byte *)(param_1 + 0x308) | 8;
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

