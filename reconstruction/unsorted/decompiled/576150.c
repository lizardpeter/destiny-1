
void FUN_00576150(undefined8 param_1,long *param_2)

{
  long *plVar1;
  long lVar2;
  long *plVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  undefined1 local_a3a;
  undefined1 local_a39;
  undefined1 local_a38 [1280];
  undefined1 local_538 [1280];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar3 = (long *)FUN_0025a550();
  lVar4 = (**(code **)(*plVar3 + 0x88))(plVar3);
  if (lVar4 != 0) {
    (**(code **)(*param_2 + 0x40))();
    thunk_FUN_012aa986(local_a38,0,0x500);
    thunk_FUN_012aa986(local_538,0,0x500);
    if (0 < *(long *)(lVar4 + 0x10)) {
      plVar3 = (long *)(lVar4 + 0x18);
      lVar5 = 0;
      do {
        lVar2 = *plVar3;
        if (0 < *(long *)((long)plVar3 + lVar5 * 0x28 + lVar2 + 0x18)) {
          plVar1 = (long *)((long)plVar3 + lVar5 * 0x28 + lVar2 + 0x20);
          lVar6 = 0;
          do {
            local_a39 = 0;
            FUN_005568c0(*(undefined2 *)((long)plVar1 + lVar6 * 2 + *plVar1 + 0x10),0,param_2,
                         local_538,local_a38,&local_a39);
            lVar6 = lVar6 + 1;
          } while (lVar6 < *(long *)((long)plVar3 + lVar5 * 0x28 + lVar2 + 0x18));
        }
        if ((*(char *)(DAT_026bc2c0 + 0x8018) != '\0') &&
           (0 < *(long *)((long)plVar3 + lVar5 * 0x28 + lVar2 + 0x28))) {
          plVar1 = (long *)((long)plVar3 + lVar5 * 0x28 + lVar2 + 0x30);
          lVar6 = 0;
          do {
            local_a3a = 0;
            FUN_005568c0(*(undefined2 *)((long)plVar1 + lVar6 * 2 + *plVar1 + 0x10),0,param_2,
                         local_538,local_a38,&local_a3a);
            lVar6 = lVar6 + 1;
          } while (lVar6 < *(long *)((long)plVar3 + lVar5 * 0x28 + lVar2 + 0x28));
        }
        lVar5 = lVar5 + 1;
      } while (lVar5 < *(long *)(lVar4 + 0x10));
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

