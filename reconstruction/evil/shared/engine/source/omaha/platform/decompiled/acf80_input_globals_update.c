
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_000acf80(void)

{
  int iVar1;
  long lVar2;
  ulong uVar3;
  ulong uVar4;
  ulong uVar5;
  ulong uVar6;
  long lVar7;
  
  if (DAT_01ad40d0 != '\0') {
    _DAT_01ad40d4 = FUN_000697a0();
    DAT_01ad40d1 = 0;
    iVar1 = FUN_000f7c30();
    LOCK();
    if (DAT_01ad4844 != 0) {
      iVar1 = DAT_01ad4844;
    }
    DAT_01ad4844 = iVar1;
    UNLOCK();
    lVar7 = (long)DAT_01ad4840 * 0x3b0;
    lVar2 = thunk_FUN_012aac96();
    uVar3 = thunk_FUN_012aac86();
    if (*(long *)(&DAT_01ad4460 + lVar7) == 0) {
      *(undefined8 *)(&DAT_01ad4478 + lVar7) = 0;
      uVar5 = 0;
    }
    else {
      uVar5 = lVar2 - *(long *)(&DAT_01ad4460 + lVar7);
      *(ulong *)(&DAT_01ad4478 + lVar7) = uVar5;
    }
    *(long *)(&DAT_01ad4460 + lVar7) = lVar2;
    uVar6 = (uVar5 - (uVar5 / uVar3) * uVar3) * 1000 + *(long *)(&DAT_01ad4480 + lVar7);
    uVar4 = uVar6 / uVar3;
    *(ulong *)(&DAT_01ad4480 + lVar7) = uVar6 - uVar3 * uVar4;
    uVar4 = (uVar5 / uVar3) * 1000 + uVar4;
    if ((long)uVar4 < 0) {
      uVar4 = 0;
    }
    uVar3 = 100;
    if ((long)uVar4 < 0x65) {
      uVar3 = uVar4 & 0xffffffff;
    }
    FUN_000ae1e0(uVar3,4,&DAT_01ad40e0 + lVar7,lVar7 + 0x1ad40f0,0);
    FUN_000ae260(DAT_01ad40d2 | DAT_01ad40d1,4,&DAT_01ad40e0 + (long)DAT_01ad4840 * 0x3b0);
    FUN_000ae390(4,(long)DAT_01ad4840 * 0x3b0 + 0x1ad4430);
    iVar1 = FUN_000f7c30();
    LOCK();
    if (iVar1 == DAT_01ad4844) {
      DAT_01ad4844 = 0;
    }
    UNLOCK();
  }
  return;
}

