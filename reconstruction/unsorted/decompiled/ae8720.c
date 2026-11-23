
void FUN_00ae8720(undefined1 *param_1)

{
  undefined1 uVar1;
  char cVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  long lVar5;
  byte bVar6;
  undefined1 auVar7 [16];
  undefined8 local_30;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar1 = FUN_00906dd0();
  *param_1 = uVar1;
  uVar1 = FUN_00906f70();
  param_1[1] = uVar1;
  uVar4 = FUN_003430b0();
  uVar3 = FUN_00345620(uVar4);
  *(undefined4 *)(param_1 + 4) = uVar3;
  uVar4 = FUN_003430b0();
  uVar3 = FUN_00345610(uVar4);
  *(undefined4 *)(param_1 + 8) = uVar3;
  uVar4 = FUN_003430b0();
  auVar7 = FUN_003457a0(uVar4);
  *(undefined1 (*) [16])(param_1 + 0xc) = auVar7;
  uVar4 = FUN_003430b0();
  uVar3 = FUN_00345a80(uVar4);
  *(undefined4 *)(param_1 + 0x1c) = uVar3;
  local_30 = FUN_00001df0();
  param_1[0x20] = 0;
  cVar2 = FUN_00244ee0(&local_30);
  if (cVar2 != '\0') {
    lVar5 = FUN_0057ddd0(local_30);
    if (lVar5 != 0) {
      param_1[0x20] = *(undefined1 *)(lVar5 + 0x15);
    }
  }
  *(undefined2 *)(param_1 + 2) = 0;
  uVar3 = DAT_025d7300;
  lVar5 = FUN_0034e370();
  local_30 = CONCAT44(local_30._4_4_,uVar3);
  bVar6 = *(byte *)(lVar5 + 0xf4) ^ 1;
  lVar5 = FUN_00118870(&local_30);
  if ((lVar5 != 0) && (*(int *)(lVar5 + 4) == *(int *)PTR_DAT_01996020)) {
    bVar6 = *(byte *)(lVar5 + 8);
  }
  param_1[0x21] = bVar6;
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

