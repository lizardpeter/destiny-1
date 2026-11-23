
ulong FUN_00589a30(undefined8 param_1,undefined8 param_2,undefined8 param_3,long param_4)

{
  undefined4 uVar1;
  long *plVar2;
  char cVar3;
  int iVar4;
  uint uVar5;
  undefined8 uVar6;
  undefined4 *puVar7;
  long lVar8;
  ulong uVar9;
  undefined1 auVar10 [16];
  undefined4 local_870 [2];
  undefined8 local_868;
  undefined8 local_860;
  undefined4 local_858;
  undefined8 local_850;
  undefined8 local_848;
  undefined8 local_840;
  long local_38;
  
  plVar2 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  uVar6 = FUN_005494c0();
  puVar7 = (undefined4 *)FUN_0054c7b0(uVar6,*(undefined2 *)(param_4 + 0xa8));
  uVar9 = 0xffffffff;
  if (puVar7 != (undefined4 *)0x0) {
    uVar6 = FUN_0033fa20();
    local_870[0] = *puVar7;
    iVar4 = FUN_0033fc20(uVar6,local_870);
    if (iVar4 != -1) {
      uVar6 = FUN_005494c0();
      auVar10 = FUN_0054bf40(uVar6);
      lVar8 = auVar10._8_8_;
      if ((auVar10._0_8_ != 0) && (lVar8 != 0)) {
        uVar1 = *(undefined4 *)(lVar8 + 0x10);
        local_848 = 0x10;
        local_850 = 0x800;
        local_840 = 0;
        local_860 = 0;
        local_858 = 0xffffffff;
        local_868 = 0;
        cVar3 = FUN_00308eb0(&local_868,iVar4);
        if (cVar3 != '\0') {
          uVar5 = FUN_0058a020(uVar1,&local_868,1,param_2,lVar8,lVar8 + 0x20,lVar8 + 0x30);
          uVar9 = (ulong)uVar5;
        }
      }
    }
  }
  if (*plVar2 == local_38) {
    return uVar9;
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

