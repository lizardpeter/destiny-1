
void FUN_0057ae30(undefined4 *param_1)

{
  long *plVar1;
  char cVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  long lVar5;
  undefined4 *puVar6;
  undefined4 local_50 [2];
  uint local_48 [2];
  undefined4 local_40 [2];
  undefined4 local_38 [2];
  undefined4 local_30 [2];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  cVar2 = FUN_00550170();
  if (cVar2 == '\0') {
    if (*(char *)(param_1 + 0x27) != '\0') {
      *(undefined1 *)(param_1 + 0x27) = 0;
      lVar5 = FUN_00958d30();
      FUN_00982db0(&DAT_00002400 + lVar5);
      *(undefined8 *)(&DAT_00002400 + lVar5) = 0;
    }
    FUN_0057b070(param_1);
  }
  else {
    cVar2 = FUN_0005ce00(param_1 + 0x10,8);
    if (cVar2 == '\0') {
      puVar6 = param_1 + 4;
      cVar2 = FUN_002b8450(puVar6);
      if ((cVar2 == '\0') || (*(long *)(param_1 + 2) == 0)) {
        cVar2 = FUN_002b8450(puVar6);
        if (cVar2 == '\0') {
          uVar4 = FUN_009503d0();
          local_38[0] = DAT_026bc310;
          uVar3 = FUN_00244e40();
          puVar6 = local_38;
        }
        else {
          if (*(long *)(param_1 + 2) != 0) goto LAB_0057af81;
          uVar4 = FUN_009503d0();
          local_40[0] = DAT_026bc30c;
          uVar3 = FUN_00244e40();
          puVar6 = local_40;
        }
      }
      else {
        cVar2 = FUN_00955ef0(puVar6,param_1 + 2,local_48,param_1[0x26]);
        if (cVar2 != '\0') {
          if ((local_48[0] & 0x1fffff) == 0) {
            FUN_00579d40(param_1,4,1);
            goto LAB_0057b02b;
          }
          FUN_0057b160(param_1,local_48);
          goto LAB_0057af81;
        }
        uVar4 = FUN_009503d0();
        local_50[0] = DAT_026bc31c;
        uVar3 = FUN_00244e40();
        puVar6 = local_50;
      }
    }
    else {
      uVar4 = FUN_009503d0();
      local_30[0] = DAT_026bc304;
      uVar3 = FUN_00244e40();
      puVar6 = local_30;
    }
    FUN_00950620(uVar4,puVar6,uVar3,0);
  }
LAB_0057af81:
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
  FUN_00543ee0(param_1 + 0x24);
  *param_1 = 0;
LAB_0057b02b:
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

