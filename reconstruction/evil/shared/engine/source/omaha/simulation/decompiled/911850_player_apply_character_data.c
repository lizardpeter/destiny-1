
void FUN_00911850(uint param_1,undefined8 param_2,char param_3)

{
  byte *pbVar1;
  long lVar2;
  char cVar3;
  long lVar4;
  ulong uVar5;
  undefined1 local_10d0 [4];
  undefined4 local_10cc;
  undefined4 local_f4c;
  undefined4 local_f2c;
  undefined4 local_f0c;
  undefined4 local_eec;
  undefined4 local_ecc;
  undefined4 local_eac;
  undefined4 local_e8c;
  undefined4 local_e6c;
  undefined4 local_e4c;
  undefined4 local_e2c;
  undefined4 local_e0c;
  undefined4 local_dec;
  undefined4 local_dcc;
  undefined4 local_da4;
  undefined4 local_d6c;
  undefined4 local_d5c;
  undefined4 local_d58;
  undefined4 local_d1c;
  undefined4 local_a3c;
  undefined4 local_a38;
  undefined4 local_9fc;
  undefined4 local_71c;
  undefined4 local_718;
  undefined4 local_6dc;
  undefined1 local_408 [964];
  undefined4 local_44;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = (ulong)param_1 & 0xffff;
  lVar2 = *(long *)(DAT_0273ea80 + 8);
  if (param_3 == '\0') {
    lVar4 = lVar2 + 0x850 + uVar5 * 0x2af0;
    cVar3 = FUN_0054dfa0(lVar4);
    pbVar1 = (byte *)(lVar2 + 0x613 + uVar5 * 0x2af0);
    *pbVar1 = *pbVar1 | 2;
    if (cVar3 == '\0') goto LAB_00911a3b;
  }
  else {
    pbVar1 = (byte *)(lVar2 + 0x613 + uVar5 * 0x2af0);
    *pbVar1 = *pbVar1 | 2;
    lVar4 = lVar2 + 0x850 + uVar5 * 0x2af0;
  }
  FUN_0104a2b0(lVar4,param_2);
  local_10cc = 0x811c9dc5;
  local_f4c = 0x811c9dc5;
  local_f2c = 0x811c9dc5;
  local_f0c = 0x811c9dc5;
  local_eec = 0x811c9dc5;
  local_ecc = 0x811c9dc5;
  local_eac = 0x811c9dc5;
  local_e8c = 0x811c9dc5;
  local_e6c = 0x811c9dc5;
  local_e4c = 0x811c9dc5;
  local_e2c = 0x811c9dc5;
  local_e0c = 0x811c9dc5;
  local_dec = 0x811c9dc5;
  local_dcc = 0x811c9dc5;
  local_da4 = 0x811c9dc5;
  local_d6c = 0x811c9dc5;
  local_d5c = 0x811c9dc5;
  local_d58 = 0x811c9dc5;
  local_d1c = 0x811c9dc5;
  local_a3c = 0x811c9dc5;
  local_a38 = 0x811c9dc5;
  local_9fc = 0x811c9dc5;
  local_71c = 0x811c9dc5;
  local_718 = 0x811c9dc5;
  local_6dc = 0x811c9dc5;
  FUN_01042f20(local_408);
  local_44 = 0x811c9dc5;
  cVar3 = FUN_00912240(param_1,local_10d0);
  if (cVar3 != '\0') {
    FUN_0073dac0(param_1,local_10d0);
    *(undefined1 *)(*(long *)(DAT_0273ea80 + 8) + 0x2840 + uVar5 * 0x2af0) = 1;
  }
LAB_00911a3b:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

