
void FUN_00799fa0(long param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  char *pcVar7;
  char local_120 [256];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  iVar2 = FUN_00559c30(0);
  iVar3 = *(int *)(param_1 + 0x34);
  if (iVar3 == 0) {
    *(undefined4 *)(param_1 + 0x34) = 1;
    FUN_00771b10(0xd);
    iVar3 = *(int *)(param_1 + 0x34);
  }
  if (iVar3 == 2) {
    if (iVar2 == 3) {
      FUN_0055a940(1);
      FUN_00b9c230();
      if (*(int *)(param_1 + 0x34) != 3) {
        *(undefined4 *)(param_1 + 0x34) = 3;
        FUN_00771ac0(0xd);
      }
      goto LAB_0079a0f1;
    }
    lVar6 = *(long *)(param_1 + 0x38);
    lVar4 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar4 = FUN_000694d0();
    }
    lVar5 = FUN_0034e3a0();
    if (lVar4 - lVar6 < (long)*(int *)(lVar5 + 0x1c)) goto LAB_0079a0f1;
    lVar6 = FUN_0034e3a0();
    pcVar7 = local_120;
    FUN_010080a0(pcVar7,s_BAP_connection_failed_due_to_hit_0165b462,*(undefined4 *)(lVar6 + 0x1c));
LAB_0079a0ec:
    FUN_00783ee0(0x19,0xad,pcVar7);
  }
  else {
    if (iVar3 != 1) goto LAB_0079a0f1;
    if (iVar2 == 0) {
      FUN_0055a7e0(0);
      cVar1 = FUN_0055a4f0(0);
      if (cVar1 == '\0') {
        pcVar7 = s_Primary_outbound_BAP_connection_f_0165b423;
        goto LAB_0079a0ec;
      }
    }
    lVar6 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar6 = FUN_000694d0();
    }
    *(long *)(param_1 + 0x38) = lVar6;
    if (*(int *)(param_1 + 0x34) != 2) {
      *(undefined4 *)(param_1 + 0x34) = 2;
      FUN_00771b10(0xd);
    }
  }
LAB_0079a0f1:
  if (*DAT_01a1f100 != local_20) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

