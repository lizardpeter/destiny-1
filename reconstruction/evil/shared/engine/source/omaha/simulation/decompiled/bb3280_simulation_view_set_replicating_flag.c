
void FUN_00bb3280(long param_1,int param_2,int param_3)

{
  bool bVar1;
  bool bVar2;
  
  if (param_2 < 2) {
    bVar2 = param_3 == -1;
  }
  else if ((param_2 == 2) || ((*(int *)(param_1 + 0x74) == 5 && (param_2 == 4)))) {
    bVar2 = false;
    if (-1 < param_3) {
      bVar2 = *(int *)(param_1 + 0x80) != param_3;
    }
  }
  else {
    bVar2 = false;
    if ((*(int *)(param_1 + 0x78) == param_3) && (*(int *)(param_1 + 0x80) != param_3)) {
      bVar2 = *(int *)(param_1 + 0x74) + 1 == param_2;
    }
  }
  if (!bVar2) {
    if (*(int *)(param_1 + 0x70) != 0) {
      return;
    }
    FUN_00bb3280(param_1,0,0xffffffff);
    *(undefined4 *)(param_1 + 0x70) = 5;
    return;
  }
  if ((*(int *)(param_1 + 0x74) == param_2) && (*(int *)(param_1 + 0x78) == param_3)) {
    return;
  }
  if ((param_2 == 0) && (*(int *)(param_1 + 0x78) != -1)) {
    *(int *)(param_1 + 0x7c) = *(int *)(param_1 + 0x78);
  }
  *(int *)(param_1 + 0x74) = param_2;
  *(int *)(param_1 + 0x78) = param_3;
  FUN_00bb3450(param_1);
  if ((((*(long *)(param_1 + 0x48) == 0) || (*(long *)(param_1 + 0x68) == 0)) ||
      (*(int *)(param_1 + 0x78) != *(int *)(param_1 + 0x88))) || (*(int *)(param_1 + 0x74) < 2)) {
    bVar2 = false;
    if (*(char *)(param_1 + 0xa5) == '\0') goto LAB_00bb338d;
    bVar2 = false;
    bVar1 = false;
  }
  else {
    bVar2 = 4 < *(int *)(param_1 + 0x84) && 4 < *(int *)(param_1 + 0x74);
    bVar1 = 1 < *(int *)(param_1 + 0x84);
    if ((*(char *)(param_1 + 0xa5) != '\0') == bVar1) goto LAB_00bb338d;
  }
  *(bool *)(param_1 + 0xa5) = bVar1;
  if (*(long *)(param_1 + 0x68) != 0) {
    FUN_00ba1500(*(long *)(param_1 + 0x68),*(undefined4 *)(*(long *)(param_1 + 0x48) + 8),bVar1);
  }
LAB_00bb338d:
  if ((bool)*(char *)(param_1 + 0xa4) != bVar2) {
    *(bool *)(param_1 + 0xa4) = bVar2;
  }
  return;
}

