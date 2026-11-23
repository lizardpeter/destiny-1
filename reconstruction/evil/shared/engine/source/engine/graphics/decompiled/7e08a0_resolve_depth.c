
void FUN_007e08a0(long *param_1,undefined8 param_2,undefined8 param_3)

{
  long lVar1;
  long lVar2;
  undefined4 *puVar3;
  long *plVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  undefined4 uVar8;
  undefined *puVar9;
  undefined8 in_stack_ffffffffffffff58;
  uint uVar10;
  undefined1 local_88 [48];
  undefined1 local_58 [32];
  long local_38;
  
  plVar4 = DAT_01a1f100;
  uVar10 = (uint)((ulong)in_stack_ffffffffffffff58 >> 0x20);
  local_38 = *DAT_01a1f100;
  iVar5 = FUN_00f7e540(param_2);
  uVar6 = FUN_00f7e2e0(param_2);
  iVar7 = FUN_00f7e540(param_2);
  FUN_00f83530(local_58,iVar5 * 8 + 8,(ulong)uVar6 / (ulong)(iVar7 * 8 + 8) >> 2,1,1,0xfac00a,8,0,
               (ulong)uVar10 << 0x20);
  uVar8 = FUN_00079280(param_2);
  FUN_00f841b0(local_58,uVar8);
  lVar2 = param_1[10];
  iVar5 = FUN_00f7e540(param_3);
  uVar6 = FUN_00f7e2e0(param_3);
  iVar7 = FUN_00f7e540(param_3);
  FUN_00f81f80(local_88,iVar5 * 8 + 8,(ulong)uVar6 / (ulong)(iVar7 * 8 + 8) >> 2,1,0xfac00a,8,0,0,0,
               0);
  uVar8 = FUN_00079280(param_3);
  FUN_00c2e290(local_88,uVar8);
  FUN_007e0240(param_1,local_88);
  lVar1 = lVar2 + 0xc0;
  puVar3 = *(undefined4 **)(*param_1 + 0x20);
  FUN_00f8b790(lVar1,*(long *)(*param_1 + 0x48) + 0x14,*puVar3,*(undefined8 *)(puVar3 + 2));
  FUN_00f8b8c0(lVar1,*(undefined8 *)(*param_1 + 0x50));
  FUN_00f8afd0(lVar1,1,0,1,local_58);
  FUN_00f7f1e0(lVar2,0x11);
  FUN_00f8df60(lVar1,lVar2,lVar2 + 0x80);
  FUN_00f7f260(lVar2,3);
  FUN_00f8e880(lVar1,lVar2,lVar2 + 0x80);
  FUN_007e0430(param_1);
  puVar9 = (undefined *)param_1[0x3df];
  if ((undefined *)param_1[0x3df] == (undefined *)0x0) {
    puVar9 = PTR_DAT_01a1f4b8;
  }
  FUN_00f8afd0(param_1[10] + 0xc0,1,0,1,puVar9);
  if (*plVar4 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

