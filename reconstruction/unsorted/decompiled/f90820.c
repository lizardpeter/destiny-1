
ulong FUN_00f90820(long *param_1)

{
  long *plVar1;
  uint uVar2;
  uint uVar3;
  undefined8 *puVar4;
  ulong uVar5;
  undefined8 local_78;
  undefined8 uStack_70;
  undefined8 local_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 local_50;
  undefined8 local_48;
  undefined8 local_40;
  undefined4 local_38;
  undefined4 local_34;
  undefined1 local_30;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  local_34 = 0;
  local_78 = 0;
  uStack_70 = 0;
  local_68 = 0;
  local_30 = 1;
  local_38 = 0;
  local_40 = 0;
  local_48 = 0;
  local_50 = 0;
  local_58 = 0;
  local_60 = 0;
  puVar4 = (undefined8 *)FUN_00fd77b0(0x10,0);
  DAT_029593e8 = puVar4;
  if (puVar4 == (undefined8 *)0x0) {
    param_1[0xc] = 0;
    uVar5 = 0x80552c08;
    goto LAB_00f90a1c;
  }
  *puVar4 = &PTR_FUN_01a140a0;
  puVar4[1] = 0;
  param_1[0xc] = (long)puVar4;
  puVar4 = (undefined8 *)FUN_00fd77b0(0x28,0);
  DAT_029593e8 = puVar4;
  if (puVar4 == (undefined8 *)0x0) {
    param_1[0xd] = 0;
    uVar5 = 0x80552c08;
  }
  else {
    *puVar4 = &PTR_FUN_01a13fe0;
    puVar4[2] = 0;
    puVar4[1] = 0;
    puVar4[3] = &PTR_FUN_01a140a0;
    puVar4[4] = 0;
    param_1[0xd] = (long)puVar4;
    puVar4 = (undefined8 *)FUN_00fd77b0(0x10,0);
    DAT_029593e8 = puVar4;
    if (puVar4 == (undefined8 *)0x0) {
      param_1[0xe] = 0;
      uVar5 = 0x80552c08;
    }
    else {
      *puVar4 = &PTR_FUN_01a11ec0;
      *(undefined4 *)(puVar4 + 1) = 0;
      param_1[0xe] = (long)puVar4;
      uVar2 = (**(code **)(*(long *)param_1[0xc] + 0x10))
                        ((long *)param_1[0xc],s_Thread_Q_Mutex_016c79da);
      uVar5 = (ulong)uVar2;
      if (uVar2 == 0) {
        uVar2 = (**(code **)(*(long *)param_1[0xd] + 0x10))();
        if (uVar2 == 0) {
          uVar2 = (**(code **)(*(long *)param_1[0xd] + 0x38))();
          if (uVar2 == 0) {
            uVar2 = thunk_FUN_012ab436(param_1 + 0x11,0,FUN_00f90b30,param_1,s_Toolkit__NP_016c79ea)
            ;
            plVar1 = (long *)param_1[0xd];
            if (uVar2 == 0) {
              uVar2 = (**(code **)(*plVar1 + 0x30))(plVar1,0);
              uVar3 = (**(code **)(*(long *)param_1[0xd] + 0x40))();
              uVar5 = (ulong)uVar3;
              if (uVar2 == 0) {
                if (uVar3 == 0) {
                  local_78 = 0;
                  FUN_00f90340(param_1,&local_78);
                  uVar5 = 0;
                }
                else {
                  (**(code **)(*param_1 + 0x20))(param_1);
                }
              }
              else {
                (**(code **)(*param_1 + 0x20))(param_1);
                uVar5 = (ulong)uVar2;
              }
              goto LAB_00f90a1c;
            }
            (**(code **)(*plVar1 + 0x40))();
            (**(code **)(*(long *)param_1[0xd] + 0x18))();
            (**(code **)(*(long *)param_1[0xc] + 0x18))();
            uVar5 = 0x80552c01;
            if (uVar2 != 0x8002000c) {
              if (uVar2 == 0x80020023) {
                uVar5 = 0x80552c08;
              }
              else if ((uVar2 == 0x8002000e) || (uVar5 = (ulong)uVar2, uVar2 == 0x80020016)) {
                uVar5 = 0x80552c02;
              }
            }
            goto LAB_00f909a1;
          }
          (**(code **)(*(long *)param_1[0xd] + 0x18))();
        }
        (**(code **)(*(long *)param_1[0xc] + 0x18))();
        uVar5 = (ulong)uVar2;
      }
LAB_00f909a1:
      (*(code *)**(undefined8 **)param_1[0xe])();
      FUN_00fd79e0(param_1[0xe]);
      param_1[0xe] = 0;
    }
    (*(code *)**(undefined8 **)param_1[0xd])();
    FUN_00fd79e0(param_1[0xd]);
    param_1[0xd] = 0;
  }
  (*(code *)**(undefined8 **)param_1[0xc])();
  FUN_00fd79e0(param_1[0xc]);
  param_1[0xc] = 0;
LAB_00f90a1c:
  if (*DAT_01a1f100 == local_28) {
    return uVar5;
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

