
char * FUN_002601f0(long *param_1)

{
  char cVar1;
  char *pcVar2;
  undefined8 uVar3;
  
  pcVar2 = (char *)(**(code **)(*param_1 + 0xc0))();
  if (*pcVar2 != '\0') {
    if (pcVar2[2] != '\0') {
      cVar1 = (**(code **)*param_1)(param_1);
      if (cVar1 != '\0') {
        uVar3 = (**(code **)(*param_1 + 200))(param_1);
        FUN_00260280(param_1,uVar3);
      }
    }
    if (*pcVar2 != '\0') {
      cVar1 = (**(code **)(*param_1 + 0xd8))(param_1);
      if (cVar1 != '\0') {
        (**(code **)(*param_1 + 0xe0))(param_1);
      }
      return pcVar2;
    }
  }
  (**(code **)(*param_1 + 0x80))(param_1);
                    /* WARNING: Could not recover jumptable at 0x00260276. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  pcVar2 = (char *)(**(code **)(*param_1 + 0xc0))(param_1);
  return pcVar2;
}

