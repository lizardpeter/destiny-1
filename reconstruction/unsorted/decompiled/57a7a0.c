
void FUN_0057a7a0(undefined4 *param_1)

{
  undefined4 *puVar1;
  char cVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  long lVar5;
  undefined4 local_d0 [2];
  undefined8 local_c8;
  long local_c0 [13];
  long local_58;
  
  local_58 = *DAT_01a1f100;
  local_c8 = FUN_00587520();
  local_c0[8] = 0;
  local_c0[9] = 0;
  local_c0[10] = 0;
  local_c0[0xb] = 0;
  local_c0[4] = 0;
  local_c0[5] = 0;
  local_c0[6] = 0;
  local_c0[7] = 0;
  local_c0[0] = 0;
  local_c0[1] = 0;
  local_c0[2] = 0;
  local_c0[3] = 0;
  uVar4 = FUN_00582a40();
  cVar2 = FUN_00580660(uVar4,&local_c8,param_1 + 4,local_c0);
  if ((cVar2 == '\0') || (local_c0[0] == 0)) {
    puVar1 = param_1 + 0x24;
    cVar2 = FUN_0012f640(puVar1);
    if (cVar2 == '\0') {
      lVar5 = FUN_0034e490();
      FUN_00543f70(puVar1,*(undefined4 *)(lVar5 + 0x44));
    }
    else {
      FUN_00544000(puVar1);
    }
    cVar2 = FUN_0010b400(puVar1);
    if (cVar2 != '\0') {
      uVar4 = FUN_009503d0();
      local_d0[0] = DAT_026bc300;
      uVar3 = FUN_00244e40();
      FUN_00950620(uVar4,local_d0,uVar3,0);
      if (*(char *)((long)param_1 + 6) != '\0') {
        uVar4 = FUN_00583cc0();
        FUN_00583b00(uVar4);
        *(undefined1 *)((long)param_1 + 6) = 0;
      }
      *(undefined8 *)(param_1 + 2) = 0;
      FUN_002b8260(param_1 + 4);
      *(undefined2 *)(param_1 + 0x23) = 0;
      param_1[0x22] = 0;
      *(undefined8 *)(param_1 + 0x20) = 0;
      *(undefined8 *)(param_1 + 0x1e) = 0;
      *(undefined8 *)(param_1 + 0x1c) = 0;
      *(undefined8 *)(param_1 + 0x1a) = 0;
      *(undefined8 *)(param_1 + 0x18) = 0;
      *(undefined8 *)(param_1 + 0x16) = 0;
      *(undefined8 *)(param_1 + 0x14) = 0;
      *(undefined8 *)(param_1 + 0x12) = 0;
      *(undefined8 *)(param_1 + 0x10) = 0;
      *(undefined1 *)(param_1 + 1) = 0;
      *(undefined1 *)((long)param_1 + 5) = 0;
      param_1[0x26] = 1;
      FUN_00543ee0(puVar1);
      *param_1 = 0;
    }
  }
  else {
    *(long *)(param_1 + 2) = local_c0[0];
    *param_1 = 2;
    FUN_0057a970(param_1);
  }
  if (*DAT_01a1f100 == local_58) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

