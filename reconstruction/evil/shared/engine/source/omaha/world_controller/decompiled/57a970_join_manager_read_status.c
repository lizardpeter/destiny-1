
void FUN_0057a970(int *param_1)

{
  long *plVar1;
  char cVar2;
  undefined8 uVar3;
  long lVar4;
  undefined2 local_2c;
  undefined2 uStack_2a;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  if ((char)param_1[1] == '\0') {
    FUN_0057aa70(param_1);
  }
  if (*(char *)((long)param_1 + 5) == '\0') {
    if (*param_1 != 2) goto LAB_0057aa53;
    FUN_0057acc0(param_1);
    if (*(char *)((long)param_1 + 5) == '\0') goto LAB_0057aa53;
  }
  uVar3 = FUN_00582a40();
  lVar4 = FUN_00580840(uVar3,param_1 + 2);
  if (lVar4 == 0) goto LAB_0057aa53;
  if ((*(short *)(lVar4 + 8) != -1) && (*(short *)(lVar4 + 10) != -1)) {
    cVar2 = FUN_00547eb0();
    if (cVar2 != '\0') {
      _local_2c = CONCAT22(*(undefined2 *)(lVar4 + 8),*(undefined2 *)(lVar4 + 10));
      FUN_0078b7c0(&local_2c);
      cVar2 = FUN_00547d00(*(undefined2 *)(lVar4 + 10));
      if (cVar2 == '\0') goto LAB_0057aa53;
      cVar2 = FUN_00547d00(*(undefined2 *)(lVar4 + 8));
      if (cVar2 == '\0') goto LAB_0057aa53;
    }
  }
  if (((char)param_1[1] != '\0') && (*param_1 == 2)) {
    *param_1 = 3;
    FUN_0057ae30(param_1);
  }
LAB_0057aa53:
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

