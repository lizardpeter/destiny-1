
void FUN_00269470(long *param_1,long param_2,long param_3,undefined1 param_4)

{
  char cVar1;
  long *plVar2;
  int *piVar3;
  
  *param_1 = (long)&PTR_FUN_0190fa00;
  param_1[1] = param_2;
  *(undefined2 *)(param_1 + 2) = 0xff;
  plVar2 = (long *)FUN_0025a550();
  piVar3 = (int *)(**(code **)(*plVar2 + 0x100))(plVar2);
  *(undefined1 *)((long)param_1 + 0x11) = 0;
  do {
    if (*piVar3 <= (int)(char)param_1[2]) break;
    *(char *)(param_1 + 2) = (char)param_1[2] + '\x01';
    cVar1 = (**(code **)(*param_1 + 8))(param_1);
    if (cVar1 != '\0') {
      *(undefined1 *)((long)param_1 + 0x11) = 1;
      break;
    }
  } while (*(char *)((long)param_1 + 0x11) == '\0');
  param_1[3] = param_3;
  *param_1 = (long)&PTR_FUN_0190fa40;
  *(undefined1 *)(param_1 + 4) = param_4;
  *(undefined2 *)((long)param_1 + 0x22) = 0xffff;
  return;
}

