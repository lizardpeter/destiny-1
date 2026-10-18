
void FUN_00911a70(uint param_1)

{
  byte *pbVar1;
  long lVar2;
  long *plVar3;
  char cVar4;
  long lVar5;
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
  
  plVar3 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  lVar5 = ((ulong)param_1 & 0xffff) * 0x2af0;
  lVar2 = *(long *)(DAT_0273ea80 + 8);
  if ((*(byte *)(lVar2 + 0x613 + lVar5) & 2) != 0) {
    FUN_0054dd80(lVar2 + 0x850 + lVar5);
    pbVar1 = (byte *)(lVar2 + lVar5 + 0x613);
    *pbVar1 = *pbVar1 & 0xfd;
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
    cVar4 = FUN_00912240((ulong)param_1,local_10d0);
    if (cVar4 != '\0') {
      FUN_0073dac0(param_1,local_10d0);
      *(undefined1 *)(*(long *)(DAT_0273ea80 + 8) + 0x2840 + lVar5) = 1;
    }
  }
  if (*plVar3 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

