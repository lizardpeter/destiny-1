
void FUN_009ce800(long param_1,undefined8 param_2)

{
  long lVar1;
  undefined4 uVar2;
  char cVar3;
  int iVar4;
  long *plVar5;
  undefined8 uVar6;
  undefined4 *puVar7;
  long lVar8;
  undefined4 local_b30 [2];
  undefined1 local_b28 [24];
  undefined4 local_b10;
  undefined1 local_b00 [24];
  int local_ae8;
  undefined2 local_ae0 [256];
  undefined1 local_8e0 [24];
  undefined1 local_8c8 [8];
  undefined1 local_8c0 [72];
  undefined1 auStack_878 [2048];
  long local_78;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_009438f0();
  plVar5 = (long *)FUN_0078e990();
  cVar3 = FUN_0098c9b0(param_2);
  if ((cVar3 == '\0') && (plVar5 != (long *)0x0)) {
    iVar4 = (**(code **)(*plVar5 + 0x10))(plVar5);
    if (iVar4 == 0) {
      *(undefined4 *)(param_1 + 0x9c) = 0;
    }
  }
  if ((((3 < *(uint *)(param_1 + 0x98)) || (*(int *)(param_1 + 0xb0) == -0x7ee3623b)) ||
      (*(int *)(param_1 + 0xb4) == -0x7ee3623b)) || (*(int *)(param_1 + 0x9c) != 0))
  goto LAB_009cea5d;
  uVar6 = FUN_00982110();
  FUN_00979640(local_b00);
  cVar3 = FUN_00979930(param_1 + 0xa0,local_b00);
  if (cVar3 != '\0') {
    if (*(char *)(param_1 + 0xc0) == '\0') {
      if (local_ae8 == *(int *)(param_1 + 0xb8)) {
        *(undefined1 *)(param_1 + 0xc0) = 1;
      }
      else if (plVar5 != (long *)0x0) {
        (**(code **)(*plVar5 + 0x18))(plVar5);
        *(undefined4 *)(param_1 + 0x9c) = 0xffffffff;
        *(undefined1 *)(param_1 + 0xc1) = 1;
      }
    }
    else if (local_ae8 == *(int *)(param_1 + 0xbc)) {
      if (plVar5 != (long *)0x0) {
        (**(code **)(*plVar5 + 0x20))(plVar5);
        *(undefined1 *)(param_1 + 0xc1) = 1;
      }
    }
    else {
      *(undefined1 *)(param_1 + 0xc0) = 0;
    }
    goto LAB_009cea5d;
  }
  if ((*(char *)(param_1 + 0xc1) != '\0') ||
     ((*(long *)(param_1 + 0xa8) != 0 && (1 < *(int *)(*(long *)(param_1 + 0xa8) + 8)))))
  goto LAB_009cea5d;
  if (*(char *)(param_1 + 0xc0) == '\0') {
    puVar7 = (undefined4 *)(param_1 + 0xb0);
  }
  else {
    puVar7 = (undefined4 *)(param_1 + 0xb4);
  }
  uVar2 = *puVar7;
  FUN_00982b00(local_b28,1,*(undefined4 *)(param_1 + 0x98));
  FUN_009796a0(local_8c0);
  cVar3 = FUN_00244ee0(local_8c8);
  if (cVar3 == '\0') {
LAB_009ce9e9:
    local_ae0[0] = 0;
  }
  else {
    cVar3 = FUN_002450b0(local_8c8,local_8e0);
    if (cVar3 == '\0') goto LAB_009ce9e9;
    FUN_002483a0(local_8e0,local_ae0,0x100);
  }
  lVar1 = local_78 + 1;
  lVar8 = local_78 * 0x200;
  local_78 = lVar1;
  if (auStack_878 + lVar8 != (undefined1 *)0x0) {
    thunk_FUN_012aa7c6(auStack_878 + lVar8,local_ae0,0x200);
  }
  local_b10 = 0;
  local_b30[0] = uVar2;
  FUN_00979ab0(local_b30,local_8c0);
  FUN_009798c0(param_1 + 0xa0,uVar6,local_b28,local_8c0);
LAB_009cea5d:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

