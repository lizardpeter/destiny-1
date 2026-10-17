
void FUN_0056def0(undefined8 param_1,char *param_2)

{
  char cVar1;
  char cVar2;
  long *plVar3;
  long lVar4;
  long lVar5;
  undefined8 local_28;
  long local_20;
  
  plVar3 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  if (DAT_026bacc0 == 0) goto LAB_0056df7b;
  local_28 = *(undefined8 *)(param_2 + 8);
  cVar1 = param_2[0x10];
  cVar2 = *param_2;
  lVar5 = 0x60;
  do {
    if ((*(char *)(DAT_026bacc0 + lVar5) == cVar2) && (*(long *)(DAT_026bacc0 + 0x20 + lVar5) == 0))
    {
      lVar4 = DAT_026bacc0 + lVar5;
      break;
    }
    lVar5 = lVar5 + 0x40;
    lVar4 = 0;
  } while ((int)lVar5 != 0x40a0);
  *(undefined8 *)(lVar4 + 0x20) = local_28;
  if (cVar1 != '\x02') {
    if (cVar1 == '\x01') {
      *(undefined1 *)(lVar4 + 0x28) = 1;
      goto LAB_0056df7b;
    }
    if (cVar1 != '\0') goto LAB_0056df7b;
    FUN_005523b0((int)cVar2,&local_28);
  }
  *(undefined1 *)(lVar4 + 0x28) = 2;
LAB_0056df7b:
  if (*plVar3 != local_20) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

