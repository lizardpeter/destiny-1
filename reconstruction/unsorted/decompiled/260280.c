
void FUN_00260280(long *param_1,undefined1 *param_2)

{
  undefined1 *puVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  long *plVar7;
  int *piVar8;
  int iVar9;
  undefined8 local_960;
  undefined8 uStack_958;
  undefined8 uStack_950;
  undefined8 uStack_948;
  undefined8 local_940;
  undefined8 uStack_938;
  undefined8 uStack_930;
  undefined8 uStack_928;
  undefined8 local_920;
  undefined8 uStack_918;
  undefined8 uStack_910;
  undefined8 uStack_908;
  undefined8 local_900;
  undefined8 uStack_8f8;
  undefined8 uStack_8f0;
  undefined8 uStack_8e8;
  undefined8 local_8e0;
  undefined8 uStack_8d8;
  undefined8 uStack_8d0;
  undefined8 uStack_8c8;
  undefined8 local_8c0;
  undefined8 uStack_8b8;
  undefined8 uStack_8b0;
  undefined8 uStack_8a8;
  undefined8 local_8a0;
  undefined8 uStack_898;
  undefined8 uStack_890;
  undefined8 uStack_888;
  undefined8 local_880;
  undefined8 uStack_878;
  undefined8 uStack_870;
  undefined8 uStack_868;
  undefined1 local_860 [2048];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  param_2[2] = 0;
  lVar5 = (**(code **)(*param_1 + 0x10))();
  uVar6 = (**(code **)(*param_1 + 0x30))(param_1);
  plVar7 = (long *)FUN_0025a550();
  piVar8 = (int *)(**(code **)(*plVar7 + 0x1b8))(plVar7);
  thunk_FUN_012aa986(local_860,0,0x800);
  if (lVar5 != 0) {
    local_880 = 0;
    uStack_878 = 0;
    uStack_870 = 0;
    uStack_868 = 0;
    local_8a0 = 0;
    uStack_898 = 0;
    uStack_890 = 0;
    uStack_888 = 0;
    local_8c0 = 0;
    uStack_8b8 = 0;
    uStack_8b0 = 0;
    uStack_8a8 = 0;
    local_8e0 = 0;
    uStack_8d8 = 0;
    uStack_8d0 = 0;
    uStack_8c8 = 0;
    local_900 = 0;
    uStack_8f8 = 0;
    uStack_8f0 = 0;
    uStack_8e8 = 0;
    local_920 = 0;
    uStack_918 = 0;
    uStack_910 = 0;
    uStack_908 = 0;
    local_940 = 0;
    uStack_938 = 0;
    uStack_930 = 0;
    uStack_928 = 0;
    local_960 = 0;
    uStack_958 = 0;
    uStack_950 = 0;
    uStack_948 = 0;
    FUN_00275ca0(param_1);
    uVar2 = FUN_000014d0();
    puVar1 = param_2 + 4;
    FUN_00281e70(lVar5 + 8,lVar5 + 0x2b80,param_2 + 0x4804,uVar6,puVar1,uVar2,lVar5 + 0x6fd0,
                 &local_960);
    FUN_00275df0(puVar1,&local_960,5,local_860);
    FUN_00275df0(puVar1,&local_960,6,local_860);
    FUN_00275df0(puVar1,&local_960,3,local_860);
    FUN_00275df0(puVar1,&local_960,4,local_860);
  }
  iVar9 = 0;
  do {
    if (*piVar8 <= (int)(short)iVar9) goto LAB_0026043e;
    iVar3 = FUN_00276510(param_2 + 0x4004,iVar9);
    iVar4 = FUN_00276510(local_860,iVar9);
    iVar9 = iVar9 + 1;
  } while (iVar3 == iVar4);
  *param_2 = 0;
LAB_0026043e:
  if (*DAT_01a1f100 == local_60) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

