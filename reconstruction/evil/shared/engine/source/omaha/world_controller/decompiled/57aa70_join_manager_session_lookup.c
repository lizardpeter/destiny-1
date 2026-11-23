
void FUN_0057aa70(undefined4 *param_1)

{
  undefined4 *puVar1;
  char *pcVar2;
  long *plVar3;
  char cVar4;
  undefined4 uVar5;
  int iVar6;
  undefined8 uVar7;
  long lVar8;
  undefined4 local_40;
  char local_39;
  undefined4 local_38 [2];
  long local_30;
  
  plVar3 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  puVar1 = param_1 + 2;
  uVar7 = FUN_0056b260();
  if (*(long *)(param_1 + 2) == 0) {
LAB_0057ab23:
    local_39 = '\0';
    pcVar2 = (char *)((long)param_1 + 6);
    if (*(char *)((long)param_1 + 6) == '\0') {
      uVar7 = FUN_00583cc0();
      FUN_00583a40(uVar7,puVar1,pcVar2,&local_39);
      if ((*pcVar2 == '\0') && (local_39 == '\0')) goto LAB_0057aca1;
    }
    uVar7 = FUN_0056b260();
    cVar4 = FUN_0056bec0(uVar7,7,puVar1);
    if (cVar4 == '\0') goto LAB_0057aca1;
    uVar7 = FUN_0056b260();
    iVar6 = FUN_0056c0a0(uVar7,7,puVar1);
    if (iVar6 == 0) goto LAB_0057aca1;
    uVar7 = FUN_009503d0();
    local_40 = DAT_026bc318;
    uVar5 = FUN_00244e40();
    FUN_00950620(uVar7,&local_40,uVar5,0);
    if (*pcVar2 != '\0') {
      uVar7 = FUN_00583cc0();
      FUN_00583b00(uVar7);
      *pcVar2 = '\0';
    }
  }
  else {
    uVar5 = FUN_00001df0(uVar7);
    lVar8 = FUN_0056dc00(uVar7,7,uVar5,puVar1);
    if (lVar8 == 0) goto LAB_0057ab23;
    if (*(long *)(lVar8 + 8) != 0) {
      uVar7 = FUN_0056b260();
      if (*(long *)(lVar8 + 8) != 0) {
        uVar5 = FUN_01009850(uVar7);
        lVar8 = FUN_0056dc00(uVar7,7,uVar5,(long *)(lVar8 + 8));
        if (lVar8 != 0) {
          FUN_002e94f0(lVar8 + 8,param_1 + 0x10);
          *(undefined1 *)(param_1 + 1) = 1;
        }
      }
      goto LAB_0057aca1;
    }
    uVar7 = FUN_009503d0();
    local_38[0] = DAT_026bc308;
    uVar5 = FUN_00244e40();
    FUN_00950620(uVar7,local_38,uVar5,0);
    if (*(char *)((long)param_1 + 6) != '\0') {
      uVar7 = FUN_00583cc0();
      FUN_00583b00(uVar7);
      *(undefined1 *)((long)param_1 + 6) = 0;
    }
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
LAB_0057aca1:
  if (*plVar3 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

