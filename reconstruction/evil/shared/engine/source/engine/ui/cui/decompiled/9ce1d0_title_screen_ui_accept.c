
void FUN_009ce1d0(long param_1)

{
  int iVar1;
  char cVar2;
  byte bVar3;
  byte bVar4;
  long *plVar5;
  undefined8 uVar6;
  undefined4 local_918 [2];
  undefined1 local_910 [24];
  undefined4 local_8f8;
  int local_8e8 [2];
  int local_8e0 [2];
  undefined1 local_8d8 [24];
  int local_8c0;
  undefined1 local_8b8 [2184];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  FUN_009438f0();
  FUN_00979640(local_8d8);
  cVar2 = FUN_00979930(param_1 + 0xb8,local_8d8);
  if (cVar2 == '\0') {
    if ((((*(long *)(param_1 + 0xc0) == 0) || (*(int *)(*(long *)(param_1 + 0xc0) + 8) < 2)) &&
        (cVar2 = FUN_005a1430(), cVar2 == '\0')) &&
       (plVar5 = (long *)FUN_0078e990(), plVar5 != (long *)0x0)) {
      cVar2 = FUN_005a09d0();
      bVar3 = 0;
      if (cVar2 != '\0') {
        bVar3 = (**(code **)(*plVar5 + 0x28))(plVar5);
      }
      if ((*(long *)(param_1 + 0xa0) != 0) &&
         (iVar1 = *(int *)(*(long *)(param_1 + 0xa0) + 0x98), iVar1 != -0x7ee3623b)) {
        if (*(int *)(param_1 + 0xa8) != -0x7ee3623b) {
          local_8e8[0] = *(int *)(param_1 + 0xa8);
          local_8e0[0] = iVar1;
          bVar4 = FUN_0097cd70(local_8e0,local_8e8);
          bVar3 = bVar3 & bVar4;
        }
        if (((bVar3 != 0) && (*(int *)(param_1 + 0xac) != -0x7ee3623b)) &&
           (*(uint *)(param_1 + 0x98) < 4)) {
          FUN_00982b00(local_910,1);
          FUN_009796a0(local_8b8);
          local_8f8 = 0;
          local_918[0] = *(undefined4 *)(param_1 + 0xac);
          FUN_00979ab0(local_918,local_8b8);
          uVar6 = FUN_00982110();
          FUN_009798c0(param_1 + 0xb8,uVar6,local_910,local_8b8);
        }
      }
    }
  }
  else {
    plVar5 = (long *)FUN_0078e990();
    if (((plVar5 != (long *)0x0) && (cVar2 = FUN_005a09d0(), cVar2 != '\0')) &&
       (cVar2 = (**(code **)(*plVar5 + 0x28))(plVar5), cVar2 != '\0')) {
      if (local_8c0 == *(int *)(param_1 + 0xb0)) {
        uVar6 = 0;
      }
      else {
        if (local_8c0 != *(int *)(param_1 + 0xb4)) goto LAB_009ce2e3;
        uVar6 = 1;
      }
      FUN_005a0a50(uVar6,0);
    }
  }
LAB_009ce2e3:
  if (*DAT_01a1f100 != local_30) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

