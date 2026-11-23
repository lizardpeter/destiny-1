
long FUN_000ad6f0(uint param_1)

{
  char cVar1;
  uint7 uVar3;
  long lVar2;
  long lVar4;
  ulong uVar5;
  
  lVar4 = (long)DAT_01ad4840 * 0x3b0;
  uVar5 = (ulong)param_1;
  uVar3 = (uint7)(int3)((uint)DAT_01ad4840 >> 8);
  if (DAT_01ad40d1 == '\0') {
    lVar2 = (ulong)uVar3 << 8;
    if ((&DAT_01ad40e0)[lVar4] != '\0') {
      lVar2 = CONCAT71((int7)((ulong)(&DAT_01ad40d0 + lVar4) >> 8),
                       (&DAT_01ad40d0 + lVar4)[uVar5 + 0x24] != '\0');
    }
    if (((&DAT_01ad40e1)[lVar4] != '\0') && (*(char *)(uVar5 + lVar4 + 0x1ad41b4) != '\0')) {
      lVar2 = CONCAT71((int7)((ulong)lVar2 >> 8),1);
    }
    if (((&DAT_01ad40e2)[lVar4] != '\0') && (*(char *)(uVar5 + lVar4 + 0x1ad4274) != '\0')) {
      lVar2 = CONCAT71((int7)((ulong)lVar2 >> 8),1);
    }
    if ((&DAT_01ad40e3)[lVar4] == '\0') {
      return lVar2;
    }
    cVar1 = *(char *)(uVar5 + lVar4 + 0x1ad4334);
  }
  else {
    lVar2 = (ulong)uVar3 << 8;
    if ((&DAT_01ad40e0)[lVar4] != '\0') {
      lVar2 = CONCAT71(0x1ad4e,(&DAT_01ad4e04)[uVar5] != '\0');
    }
    if (((&DAT_01ad40e1)[lVar4] != '\0') && ((&DAT_01ad4e04)[uVar5] != '\0')) {
      lVar2 = CONCAT71((int7)((ulong)lVar2 >> 8),1);
    }
    if (((&DAT_01ad40e2)[lVar4] != '\0') && ((&DAT_01ad4e04)[uVar5] != '\0')) {
      lVar2 = CONCAT71((int7)((ulong)lVar2 >> 8),1);
    }
    if ((&DAT_01ad40e3)[lVar4] == '\0') {
      return lVar2;
    }
    cVar1 = (&DAT_01ad4e04)[uVar5];
  }
  if (cVar1 != '\0') {
    lVar2 = CONCAT71((int7)((ulong)lVar2 >> 8),1);
  }
  return lVar2;
}

