
void FUN_00574e20(long param_1)

{
  long lVar1;
  char cVar2;
  undefined4 uVar3;
  
  uVar3 = 0xffffffff;
  if (DAT_0193e868 != (undefined4 *)0x0) {
    uVar3 = *DAT_0193e868;
  }
  FUN_0023e010(param_1 + 8,s__investment_activity_selection_m_0163d24f + 1,0x130,4,uVar3,5,3,0x18,
               thunk_FUN_001681a0);
  lVar1 = DAT_026bc068;
  FUN_01018280(DAT_026bc068);
  FUN_01018280(lVar1 + 0x8c);
  *(undefined8 *)(lVar1 + 0x118) = 0;
  *(undefined8 *)(lVar1 + 0x120) = 0xffffffffffffffff;
  *(undefined4 *)(lVar1 + 0x128) = 0xffffffff;
  *(undefined1 *)(lVar1 + 300) = 1;
  cVar2 = FUN_00752150(0);
  if ((cVar2 == '\0') && (cVar2 = FUN_00752150(1), cVar2 == '\0')) {
    return;
  }
  *(undefined1 *)(lVar1 + 300) = 0;
  return;
}

