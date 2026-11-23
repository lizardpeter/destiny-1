
void FUN_00269230(long *param_1,long param_2)

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
  while( true ) {
    if (*piVar3 <= (int)(char)param_1[2]) {
      return;
    }
    *(char *)(param_1 + 2) = (char)param_1[2] + '\x01';
    cVar1 = (**(code **)(*param_1 + 8))(param_1);
    if (cVar1 != '\0') break;
    if (*(char *)((long)param_1 + 0x11) != '\0') {
      return;
    }
  }
  *(undefined1 *)((long)param_1 + 0x11) = 1;
  return;
}

