
void FUN_007e0040(long *param_1,undefined8 param_2,undefined8 param_3)

{
  long lVar1;
  long lVar2;
  long *plVar3;
  char cVar4;
  uint uVar5;
  long lVar6;
  undefined4 *puVar7;
  undefined8 uVar8;
  undefined *puVar9;
  uint local_60 [2];
  undefined1 local_58 [32];
  long local_38;
  
  plVar3 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  lVar2 = param_1[10];
  FUN_00f83e80(local_58,param_2,0);
  FUN_007e0240(param_1,param_3);
  puVar7 = *(undefined4 **)(*param_1 + 0x20);
  lVar1 = lVar2 + 0xc0;
  FUN_00f8b790(lVar1,*(long *)(*param_1 + 0x48) + 0x14,*puVar7,*(undefined8 *)(puVar7 + 2));
  local_60[0] = FUN_00f82b00(param_3);
  uVar5 = local_60[0] & 0xff;
  if (((uVar5 < 0x17) && (uVar5 != 0)) && ((uVar5 | 2) != 0xf)) {
    cVar4 = FUN_00f7d980(local_60,0);
    if (cVar4 == '\0') goto LAB_007e00ff;
    cVar4 = FUN_00f7d780(local_60,0);
    if ((cVar4 == '\0') || (uVar5 = (local_60[0] & 0xff) - 1, 0x14 < uVar5)) goto LAB_007e00ff;
    lVar6 = *param_1;
    if ((0x1f8bf7U >> (uVar5 & 0x1f) & 1) != 0) {
      uVar8 = *(undefined8 *)(lVar6 + 0x50);
      goto LAB_007e0106;
    }
  }
  else {
LAB_007e00ff:
    lVar6 = *param_1;
  }
  uVar8 = *(undefined8 *)(lVar6 + 0x60);
LAB_007e0106:
  FUN_00f8b8c0(lVar1,uVar8);
  FUN_00f8afd0(lVar1,1,0,1,local_58);
  FUN_00f7f1e0(lVar2,0x11);
  FUN_00f8df60(lVar1,lVar2,lVar2 + 0x80);
  FUN_00f7f260(lVar2,3);
  FUN_00f8e880(lVar1,lVar2,lVar2 + 0x80);
  lVar1 = param_1[10];
  puVar7 = (undefined4 *)FUN_00f7feb0(lVar1,4,3);
  *puVar7 = 0;
  FUN_00f80c90(lVar1,4,0,puVar7,1,1,0,0);
  FUN_00f80e00(lVar1,puVar7,0xffffffff,3,1);
  FUN_00f80f10(lVar1,0x38,0,1);
  FUN_007e0430(param_1);
  puVar9 = (undefined *)param_1[0x3df];
  if ((undefined *)param_1[0x3df] == (undefined *)0x0) {
    puVar9 = PTR_DAT_01a1f4b8;
  }
  FUN_00f8afd0(param_1[10] + 0xc0,1,0,1,puVar9);
  if (*plVar3 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

