
void FUN_007556c0(int *param_1,undefined8 param_2)

{
  int *piVar1;
  undefined *puVar2;
  undefined8 uVar3;
  
  FUN_00065030(param_2,s_Change_world_0164a498,0x100);
  if (*param_1 == 4) {
    FUN_010080a0(param_2,s_Change_world__unload___0164a50a);
    return;
  }
  if ((char)param_1[0x1b6] == '\0') {
    piVar1 = (int *)&DAT_012ad038;
  }
  else {
    piVar1 = param_1 + 0x196;
  }
  if (*(char *)((long)param_1 + 0x6d9) == '\0') {
    puVar2 = &DAT_01621de5;
  }
  else {
    puVar2 = &DAT_01621de3;
  }
  uVar3 = 0x59;
  if ((char)param_1[0x1b9] == '\0') {
    uVar3 = 0x4e;
  }
  FUN_010080a0(param_2,s_Change_world__activity_name___s__0164a4a5,param_1 + 0x18c,piVar1,puVar2,
               uVar3,param_1[0x1b8]);
  return;
}

