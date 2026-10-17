
void FUN_00b5eba0(long param_1,uint param_2)

{
  ushort *puVar1;
  ushort uVar2;
  uint uVar3;
  long lVar4;
  long lVar5;
  
  lVar4 = (long)*(int *)(param_1 + 0xc) * 0x40;
  uVar2 = *(ushort *)
           ((&DAT_02883348)
            [(long)*(short *)(*(long *)(param_1 + 0x10) + 0xb4 + (ulong)(param_2 & 0x3fff) * 6) *
             0x10] + 0x58 + lVar4);
  *(ushort *)
   ((&DAT_02883348)
    [(long)*(short *)(*(long *)(param_1 + 0x10) + 0xb4 + (ulong)(param_2 & 0x3fff) * 6) * 0x10] +
    0x58 + lVar4) = uVar2 & 0xfff7;
  if ((uVar2 & 1) == 0) {
    lVar4 = (&DAT_02883348)
            [(long)*(short *)(*(long *)(param_1 + 0x10) + 0xb4 + (ulong)(param_2 & 0x3fff) * 6) *
             0x10];
    lVar5 = (long)*(int *)(param_1 + 0xc) * 0x40;
    puVar1 = (ushort *)(lVar4 + 0x58 + lVar5);
    *puVar1 = *puVar1 | 1;
    uVar3 = FUN_00b50b70(*(undefined8 *)(param_1 + 0x10));
    puVar1 = (ushort *)
             ((&DAT_02883348)
              [(long)*(short *)(*(long *)(param_1 + 0x10) + 0xb4 + (ulong)(uVar3 & 0x3fff) * 6) *
               0x10] + 0x58 + (long)*(int *)(param_1 + 0xc) * 0x40);
    *puVar1 = *puVar1 | 0x80;
    puVar1 = (ushort *)(lVar4 + 0x58 + lVar5);
    *puVar1 = *puVar1 | 0x740;
    *(int *)(param_1 + 0x28) = *(int *)(param_1 + 0x28) + 1;
  }
  return;
}

