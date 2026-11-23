
void FUN_00772bd0(undefined8 param_1,undefined8 param_2,undefined4 param_3,undefined4 param_4,
                 undefined8 *param_5)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  char *pcVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  char *pcVar7;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  pcVar7 = (char *)0x0;
  if (DAT_026ca4e0 != (char *)0x0) {
    pcVar7 = (char *)0x0;
    pcVar4 = (char *)0x0;
    if (*DAT_026ca4e0 != '\0') {
      pcVar4 = DAT_026ca4e0;
    }
    if (pcVar4 != (char *)0x0) {
      pcVar7 = pcVar4 + ((long)*(int *)(pcVar4 + 0x26398) ^ 1U) * 0x98e0 + 0x263a0;
    }
  }
  switch(*(int *)(pcVar7 + 0x8c48)) {
  case 0:
    goto switchD_00772c60_caseD_0;
  default:
    goto switchD_00772c60_caseD_1;
  case 3:
  case 5:
  case 7:
    goto switchD_00772c60_caseD_3;
  case 8:
    pcVar4 = pcVar7 + 0x8c50;
    break;
  case 9:
    pcVar4 = pcVar7 + 0x8c54;
  }
  if (*pcVar4 == '\0') {
    if (*(int *)(pcVar7 + 0x8c48) == 0) goto switchD_00772c60_caseD_0;
switchD_00772c60_caseD_1:
    cVar1 = FUN_000e4d70(9,3);
    if (cVar1 != '\0') {
      if ((DAT_026ca500 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026ca500), iVar2 != 0)) {
        DAT_026ca4f8 = FUN_000e4a10(s_networking_logic_create_public_a_0164db43);
        thunk_FUN_012aa7e6(&DAT_026ca500);
      }
      uVar5 = FUN_00b6db70(pcVar7);
      FUN_01008290(local_178,s_networking_logic_create_public_a_0164db43,uVar5);
      uVar3 = DAT_026ca4f8;
      goto LAB_00772d6d;
    }
  }
  else {
switchD_00772c60_caseD_3:
    cVar1 = FUN_000e4d70(9,3);
    if (cVar1 != '\0') {
      if ((DAT_026ca4f0 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026ca4f0), iVar2 != 0)) {
        DAT_026ca4e8 = FUN_000e4a10(s_networking_logic_create_public_a_0164dae0);
        thunk_FUN_012aa7e6(&DAT_026ca4f0);
      }
      uVar5 = FUN_00b6db70(pcVar7);
      FUN_01008290(local_178,s_networking_logic_create_public_a_0164dae0,uVar5);
      uVar3 = DAT_026ca4e8;
LAB_00772d6d:
      FUN_000e4aa0(uVar3,local_178);
    }
  }
  FUN_00b73600(pcVar7);
switchD_00772c60_caseD_0:
  cVar1 = FUN_0076a0e0(1);
  if ((cVar1 == '\0') || (cVar1 = FUN_0075c600(), cVar1 != '\0')) {
    uVar3 = FUN_00084200();
    uVar5 = 4;
  }
  else {
    uVar3 = FUN_00084200();
    uVar5 = 0xc;
  }
  uVar6 = FUN_002e9a10();
  pcVar4 = (char *)0x0;
  cVar1 = FUN_00b6c7f0(pcVar7,uVar5,uVar3,uVar6,0,param_2,param_3,param_4);
  if (cVar1 == '\0') {
    cVar1 = FUN_000e4d70(9,4);
    if (cVar1 != '\0') {
      if ((DAT_026ca510 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026ca510), iVar2 != 0)) {
        DAT_026ca508 = FUN_000e4a10(s_networking_logic_create_public_a_0164dba5);
        thunk_FUN_012aa7e6(&DAT_026ca510);
      }
      FUN_01008290(local_178,s_networking_logic_create_public_a_0164dba5);
      FUN_000e4aa0(DAT_026ca508,local_178);
    }
  }
  else {
    FUN_00b25a80(pcVar7);
    pcVar4 = pcVar7;
  }
  *param_5 = pcVar4;
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

