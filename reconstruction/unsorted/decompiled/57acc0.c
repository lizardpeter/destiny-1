
void FUN_0057acc0(undefined4 *param_1)

{
  undefined4 *puVar1;
  long *plVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  long lVar7;
  undefined4 local_30 [2];
  long local_28;
  
  plVar2 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  uVar6 = FUN_00582a40();
  puVar1 = param_1 + 2;
  lVar7 = FUN_00580840(uVar6,puVar1);
  if (lVar7 == 0) {
    uVar6 = FUN_0056b260();
    cVar3 = FUN_0056bec0(uVar6,2,puVar1);
    if (cVar3 != '\0') {
      uVar6 = FUN_0056b260();
      iVar4 = FUN_0056c0a0(uVar6,2,puVar1);
      if (iVar4 != 0) {
        uVar6 = FUN_009503d0();
        local_30[0] = DAT_026bc314;
        uVar5 = FUN_00244e40();
        FUN_00950620(uVar6,local_30,uVar5,0);
        if (*(char *)((long)param_1 + 6) != '\0') {
          uVar6 = FUN_00583cc0();
          FUN_00583b00(uVar6);
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
        FUN_00543ee0(param_1 + 0x24);
        *param_1 = 0;
      }
    }
  }
  else {
    *(undefined1 *)((long)param_1 + 5) = 1;
  }
  if (*plVar2 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

