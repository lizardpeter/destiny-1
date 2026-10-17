
undefined8 FUN_007da960(void)

{
  ulong *puVar1;
  int iVar2;
  long lVar3;
  uint uVar4;
  long lVar5;
  ulong uVar6;
  undefined8 uVar7;
  int iVar8;
  ulong uVar9;
  undefined1 uVar10;
  ulong uVar11;
  bool bVar12;
  int *in_stack_00000008;
  
  lVar5 = DAT_026df268;
  lVar3 = *DAT_01a1f100;
  if (in_stack_00000008 == (int *)0x0) {
    puVar1 = (ulong *)(DAT_026df268 + 0x28000);
    uVar10 = 0;
    uVar11 = *(ulong *)(DAT_026df268 + 0x28000);
    do {
      uVar9 = uVar11 >> 0x20;
      iVar8 = (int)(uVar11 >> 0x20);
      uVar4 = iVar8 + 1;
      if (iVar8 == 0x9ff) {
        uVar4 = 0;
      }
      if (uVar4 == (uint)uVar11) goto LAB_007daa30;
      LOCK();
      uVar6 = *puVar1;
      if (uVar11 == uVar6) {
        *puVar1 = (ulong)uVar4 << 0x20 | uVar11 & 0xffffffff;
        uVar6 = uVar11;
      }
      UNLOCK();
      bVar12 = uVar6 != uVar11;
      uVar11 = uVar6;
    } while (bVar12);
    in_stack_00000008 = (int *)(lVar5 + uVar9 * 0x40);
    if (in_stack_00000008 == (int *)0x0) goto LAB_007daa30;
  }
  FUN_007db260();
  *(undefined1 *)(in_stack_00000008 + 0xf) = 0;
  uVar10 = 1;
  do {
    iVar2 = *in_stack_00000008;
    LOCK();
    iVar8 = *in_stack_00000008;
    if (iVar2 == iVar8) {
      *in_stack_00000008 = 1;
      iVar8 = iVar2;
    }
    UNLOCK();
  } while (iVar2 != iVar8);
LAB_007daa30:
  if (*DAT_01a1f100 != lVar3) {
    uVar7 = thunk_FUN_012aa7f6();
    return uVar7;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar10);
}

