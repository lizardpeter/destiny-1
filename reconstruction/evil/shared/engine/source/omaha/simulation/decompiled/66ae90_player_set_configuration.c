
void FUN_0066ae90(ushort param_1,long param_2)

{
  int *piVar1;
  int iVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  
  lVar3 = *(long *)(DAT_0273ea80 + 8);
  lVar4 = (ulong)param_1 * 0x2af0;
  piVar1 = (int *)(lVar3 + 0x2918 + lVar4);
  if (((*(int *)(lVar3 + 0x644 + lVar4) != -1) || (lVar5 = (long)*piVar1, lVar5 == -1)) ||
     (lVar5 = lVar5 * 0x8c,
     (&DAT_0000232c)[lVar3 + lVar4 + lVar5] != *(char *)(param_2 + 0xccc + lVar5))) {
    *piVar1 = -1;
  }
  iVar2 = *(int *)(lVar3 + 0x1664 + lVar4);
  if (((iVar2 != -0x7ee3623b) && (iVar2 != *(int *)(param_2 + 4))) &&
     (0 < *(int *)(lVar3 + 0x38 + lVar4))) {
    *(undefined4 *)(lVar3 + 0x2888 + lVar4) = 0;
    *(undefined4 *)(lVar3 + 0x2884 + lVar4) = 0;
    *(undefined4 *)(lVar3 + 0x2890 + lVar4) = 0x3f800000;
    *(undefined4 *)(lVar3 + 0x28a0 + lVar4) = 0;
    *(undefined4 *)(lVar3 + 0x289c + lVar4) = 0;
    *(undefined4 *)(lVar3 + 0x28a8 + lVar4) = 0x3f800000;
    *(undefined4 *)(lVar3 + 0x28b8 + lVar4) = 0;
    *(undefined4 *)(lVar3 + 0x28b4 + lVar4) = 0;
    *(undefined4 *)(lVar3 + 0x28c0 + lVar4) = 0x3f800000;
    *(undefined4 *)(lVar3 + 0x28d0 + lVar4) = 0;
    *(undefined4 *)(lVar3 + 0x28cc + lVar4) = 0;
    *(undefined4 *)(lVar3 + 0x28d8 + lVar4) = 0x3f800000;
  }
  FUN_0104f3a0(lVar3 + 0x1660 + lVar4);
  return;
}

